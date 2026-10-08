"""Compose the final 1080x1920 frames: graphics on top, footage below, captions on the seam.

usage: python3 render.py <first_frame> <last_frame_exclusive> <out.mp4>
"""
import math
import subprocess
import sys

import cairo

from gfx import *  # noqa: F401,F403
from scenes import SCHEDULE, T
from timeline import PAGES

FPS = 30
H = 1920
SEAM = TOPH
FOOTAGE = "footage_sdr.mp4"
SRC_Y = 200          # source row shown at the top of the footage panel
SPEECH_END = 39.2

TRANS_DUR = 0.42
TRANS_LEAD = 0.16    # transitions start slightly before the word lands


# --------------------------------------------------------------- camera moves
SHAKES = [(T["mish"] + 0.05, 16), (T["mish"] + 0.18, 11), (T["ashra"], 13), (T["haje"] + 0.22, 11), (T["c6"], 6),
          (T["k15"] + 0.25, 5)]
PUNCHES = [(T["mish"], 0.13, 1.3), (T["ashra"], 0.09, 1.4), (T["haje"], 0.07, 1.5), (T["c6"], 0.05, 0.7),
           (T["hani2"], 0.04, 0.3), (T["farouj"], 0.05, 0.9)]


def shake(t):
    dx = dy = 0.0
    for t0, amp in SHAKES:
        d = t - t0
        if 0 <= d < 0.6:
            k = amp * math.exp(-7 * d)
            dx += k * math.sin(d * 71)
            dy += k * math.cos(d * 53)
    return dx, dy


def zoom(t):
    z = 1.03 + 0.05 * (t / 40.6)
    for t0, amt, hold in PUNCHES:
        z += amt * ease_out_expo(prog(t, t0, 0.22)) * (1 - ease_io(prog(t, t0 + hold, 0.6)))
    return z


# --------------------------------------------------------------- scene compositor
def lead(kind):
    return 0.02 if kind == "cut" else TRANS_LEAD


def scene_at(t):
    idx = 0
    for i, (s, e, fn, tr) in enumerate(SCHEDULE):
        if t >= s - lead(tr):
            idx = i
    return idx


def draw_scene(i, t, fr):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, TOPH)
    ctx = cairo.Context(surf)
    SCHEDULE[i][2](ctx, t, fr)
    grain(ctx, fr)
    return surf


def transition(ctx, kind, p, old, new):
    """Paint old->new for progress p in [0,1]."""
    e = ease_io(p)
    if kind == "swipe":
        ctx.set_source_surface(old)
        ctx.paint()
        edge = lerp(W + 420, -420, e)
        slant = 300

        def band(x0):
            ctx.new_path()
            ctx.move_to(x0, 0)
            ctx.line_to(W + 800, 0)
            ctx.line_to(W + 800, TOPH)
            ctx.line_to(x0 - slant, TOPH)
            ctx.close_path()
        ctx.save()
        band(edge + 160)
        ctx.clip()
        ctx.set_source_surface(new)
        ctx.paint()
        ctx.restore()
        for off, c in ((0, GOLD), (80, RED2)):
            ctx.new_path()
            ctx.move_to(edge + off, 0)
            ctx.line_to(edge + off + 80, 0)
            ctx.line_to(edge + off + 80 - slant, TOPH)
            ctx.line_to(edge + off - slant, TOPH)
            ctx.close_path()
            fill(ctx, c)
    elif kind == "zoom":
        ctx.save()
        s = lerp(1.0, 1.35, ease_in_cubic(min(1, p * 1.6)))
        ctx.translate(W / 2, TOPH / 2)
        ctx.scale(s, s)
        ctx.translate(-W / 2, -TOPH / 2)
        ctx.set_source_surface(old)
        ctx.paint_with_alpha(1 - clamp(p * 1.8))
        ctx.restore()
        ctx.save()
        s = lerp(0.82, 1.0, ease_out_cubic(clamp((p - 0.25) / 0.75)))
        ctx.translate(W / 2, TOPH / 2)
        ctx.scale(s, s)
        ctx.translate(-W / 2, -TOPH / 2)
        ctx.set_source_surface(new)
        ctx.paint_with_alpha(clamp((p - 0.2) / 0.5))
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, 0.35 * math.sin(math.pi * p))
        ctx.paint()
    elif kind == "circle":
        ctx.set_source_surface(old)
        ctx.paint()
        r = lerp(0, 1150, ease_in_expo(p) * 0.4 + e * 0.6)
        ctx.save()
        ctx.arc(W / 2, TOPH / 2, r, 0, 2 * math.pi)
        ctx.clip()
        ctx.set_source_surface(new)
        ctx.paint()
        ctx.restore()
        ring(ctx, W / 2, TOPH / 2, r, 26 * (1 - p) + 4, with_a(GOLD, 1 - p * 0.6))
    elif kind == "liquid":
        ctx.set_source_surface(old)
        ctx.paint()
        level = lerp(TOPH + 120, -160, e)

        def wave(dy, amp):
            ctx.new_path()
            ctx.move_to(0, TOPH + 10)
            for x in range(0, W + 41, 40):
                ctx.line_to(x, level + dy + amp * math.sin(x / 120 + p * 14) + amp * 0.5 * math.sin(x / 47 - p * 9))
            ctx.line_to(W, TOPH + 10)
            ctx.close_path()
        wave(-40, 34)
        fill(ctx, with_a(RED2, 0.9))
        ctx.save()
        wave(0, 30)
        ctx.clip()
        ctx.set_source_surface(new)
        ctx.paint()
        ctx.restore()
        wave(0, 30)
        ctx.set_line_width(6)
        ctx.set_source_rgba(1, 1, 1, 0.55)
        ctx.stroke()
    else:  # cut with flash
        ctx.set_source_surface(new if p > 0.05 else old)
        ctx.paint()
        ctx.set_source_rgba(1, 1, 1, 0.85 * (1 - ease_out_cubic(p)))
        ctx.paint()


def draw_top(ctx, t, fr):
    i = scene_at(t)
    start, _, _, kind = SCHEDULE[i]
    p = (t - (start - lead(kind))) / TRANS_DUR
    new = draw_scene(i, t, fr)
    if i > 0 and 0 <= p < 1 and kind != "none":
        old = draw_scene(i - 1, t, fr)
        transition(ctx, kind, p if kind != "cut" else clamp(p * 1.4), old, new)
    else:
        ctx.set_source_surface(new)
        ctx.paint()


# --------------------------------------------------------------- captions
CAP_SIZE = 60
CAP_Y = SEAM


def page_window(k):
    pg = PAGES[k]
    nxt = PAGES[k + 1]["s"] if k + 1 < len(PAGES) else 1e9
    return pg["s"] - 0.1, min(nxt - 0.1, pg["e"] + 0.45)


def draw_captions(ctx, t):
    for k, pg in enumerate(PAGES):
        a0, a1 = page_window(k)
        if not (a0 <= t < a1):
            continue
        pin = prog(t, a0, 0.22)
        pout = prog(t, a1 - 0.14, 0.14)
        alpha = ease_out_cubic(pin) * (1 - pout)
        pad = 8
        sps = []
        for w in pg["words"]:
            active = w["s"] <= t < w["e"]
            sps.append((w, text(w["w"], CAP_SIZE, WHITE, SANS), text(w["w"], CAP_SIZE, GOLD, SANS), active))
        gap = 18
        widths = [s.w - 2 * pad for _, s, _, _ in sps]
        total = sum(widths) + gap * (len(sps) - 1)
        fit = min(1.0, 900 / total)
        pw, ph = (total + 80) * fit, 112
        s = lerp(0.86, 1.0, ease_out_back(pin, 2.0))
        ctx.save()
        ctx.translate(W / 2, CAP_Y)
        ctx.scale(s, s)
        sh, _ = soft_shadow(int(pw), ph, ph // 2, 18, 0.55)
        blit(ctx, sh, 0, 10, alpha=alpha)
        rrect(ctx, -pw / 2, -ph / 2, pw, ph, ph / 2)
        fill(ctx, with_a(INK, 0.86 * alpha))
        rrect(ctx, -pw / 2, -ph / 2, pw, ph, ph / 2)
        ctx.set_line_width(3)
        ctx.set_source_rgba(*with_a(RED, 0.9 * alpha))
        ctx.stroke()
        x = total / 2 * fit
        for (w, white, gold, active), wd in zip(sps, widths):
            wd *= fit
            said = t >= w["s"]
            bump = 1 + 0.16 * math.exp(-10 * max(0, t - w["s"])) * said
            rise = 14 * (1 - ease_out_cubic(prog(t, a0 + 0.03 * sps.index((w, white, gold, active)), 0.25)))
            sp = gold if active else white
            a = alpha * (1.0 if said else 0.42)
            blit(ctx, sp, x - wd / 2, 4 + rise, fit * bump, alpha=a)
            x -= wd + gap * fit
        if pg["spk"] == "cam":
            lab = text("المصوّر", 30, WHITE, SANS_B)
            cx = pw / 2 - 80
            rrect(ctx, cx - lab.w / 2 - 6, -ph / 2 - 30, lab.w + 12, 46, 23)
            fill(ctx, with_a(RED, alpha))
            blit(ctx, lab, cx, -ph / 2 - 7, alpha=alpha)
        ctx.restore()


# --------------------------------------------------------------- seam + footage
def draw_footage(ctx, t, src):
    z = zoom(t)
    dx, dy = shake(t)
    ctx.save()
    ctx.rectangle(0, SEAM, W, H - SEAM)
    ctx.clip()
    ctx.translate(W / 2 + dx * 0.4, SEAM + (H - SEAM) / 2 + dy * 0.4)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -(H - SEAM) / 2)
    ctx.set_source_surface(src, 0, -SRC_Y)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()
    # shade under the seam + soft vignette
    g = cairo.LinearGradient(0, SEAM, 0, SEAM + 160)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.5)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.rectangle(0, SEAM, W, 160)
    ctx.set_source(g)
    ctx.fill()
    g = cairo.LinearGradient(0, H - 260, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.35)
    ctx.rectangle(0, H - 260, W, 260)
    ctx.set_source(g)
    ctx.fill()


def draw_seam(ctx, t):
    g = cairo.LinearGradient(0, 0, W, 0)
    off = (t * 0.35) % 1
    for k in range(5):
        o = (k / 4 + off) % 1
        g.add_color_stop_rgba(o, *(GOLD if k % 2 else RED))
    ctx.rectangle(0, SEAM - 4, W, 8)
    ctx.set_source(g)
    ctx.fill()


def render(f0, f1, out):
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", out],
        stdin=subprocess.PIPE)
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", f"{f0 / FPS:.4f}", "-i", FOOTAGE, "-frames:v", str(f1 - f0),
         "-f", "rawvideo", "-pix_fmt", "bgra", "-"], stdout=subprocess.PIPE)
    frame_bytes = W * H * 4
    frame = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    last = None
    for fr in range(f0, f1):
        t = fr / FPS
        raw = dec.stdout.read(frame_bytes)
        if len(raw) == frame_bytes:
            last = cairo.ImageSurface.create_for_data(bytearray(raw), cairo.FORMAT_ARGB32, W, H, W * 4)
        ctx = cairo.Context(frame)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        draw_footage(ctx, t, last)
        ctx.save()
        ctx.rectangle(0, 0, W, SEAM)
        ctx.clip()
        dx, dy = shake(t)
        ctx.translate(dx, dy)
        ctx.scale(1 + abs(dx) / 400 + 0.0001, 1 + abs(dx) / 400 + 0.0001)
        draw_top(ctx, t, fr)
        ctx.restore()
        draw_seam(ctx, t)
        draw_captions(ctx, t)
        # final fade to black as the hand covers the lens
        fo = prog(t, 40.0, 0.55)
        if fo > 0:
            ctx.set_source_rgba(0, 0, 0, ease_in_cubic(fo))
            ctx.paint()
        frame.flush()
        enc.stdin.write(bytes(frame.get_data()))
        if fr % 60 == 0:
            print(f"[{f0}-{f1}] frame {fr}", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()


if __name__ == "__main__":
    render(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
