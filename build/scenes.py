"""The 14 motion-graphics scenes for the top half. Every key time is a spoken word."""
import math
import random

import cairo

from gfx import *  # noqa: F401,F403
from timeline import word_time as wt

# --------------------------------------------------------------- key times
T = dict(
    hani=wt("هاني"), eish=wt("إيش"), endak=wt("عندك"), hani2=wt("هاني", 1),
    othman=wt("عثمان"), salli=wt("صلّي"),
    youm=wt("اليوم"), khamis=wt("الخميس"), ahsan=wt("أحسن"), orood=wt("عروض"), lahme=wt("اللحمة"), moallem=wt("معلم"),
    kaman=wt("كمان"), orood2=wt("عروض", 1), cola=wt("الكولا"), baba=wt("بابا"),
    c1=wt("واحدة"), c2=wt("اثنين"), c3=wt("ثلاثة"), c4=wt("أربعة"), lissa=wt("لسّه"), khallast=wt("خلّصتش"),
    c5=wt("خمسة"), c6=wt("ستة"), baba2=wt("بابا", 1),
    sit=wt("ست"), bikam=wt("بكم"), b15=wt("بخمستعش"), indak2=wt("عندك", 1),
    mish=wt("مش"), k15=wt("خمستعش"),
    hadool3=wt("هدول", 2), sitte=wt("الستة"), ashra=wt("بعشرة"), shekel=wt("شيكل"), hajj=wt("حج"),
    taqm=wt("طقم"), ashra2=wt("بعشرة", 1), coke=wt("كوكاكولا"), ml300=wt("300"),
    haje=wt("حاجة"), alf=wt("ألف"), baba3=wt("بابا", 2),
    ind=wt("عند"), farouj=wt("فروج"), helou=wt("الحلو"),
    onwan=wt("عنواننا"), maroof=wt("معروف"), share=wt("شارع"), nasr=wt("النصر"), mqabel=wt("مقابل"), burj=wt("برج"), shifa=wt("الشفاء"),
    ahlan=wt("أهلاً"), sahlan=wt("وسهلاً"), bikom=wt("بكم", 1), tsharfuna=wt("تشرّفونا"), btnawruna=wt("وبتنوّرونا"),
    hot=wt("حط"),
)
COUNTS = [T["c1"], T["c2"], T["c3"], T["c4"], T["c5"], T["c6"]]

# (start, end, scene, transition-in)
SCHEDULE = []


def scene(start, end, trans):
    def deco(fn):
        SCHEDULE.append((start, end, fn, trans))
        return fn
    return deco


def word_row(ctx, t, items, cx, cy, size, font=KUFI, gap=18, shadow=10, rise=40, dur=0.42):
    """items: [(word, t_in, color)] laid out right-to-left, each word springs in."""
    sps = [text(w, size, c, font, shadow=shadow) for w, _, c in items]
    pad = shadow * 3 + 8
    widths = [s.w - 2 * pad for s in sps]
    total = sum(widths) + gap * (len(sps) - 1)
    x = cx + total / 2
    for sp, wdt, (_, t0, _) in zip(sps, widths, items):
        p = prog(t, t0, dur)
        if p > 0:
            s = 0.35 + 0.65 * ease_out_back(p, 2.4)
            blit(ctx, sp, x - wdt / 2, cy + rise * (1 - ease_out_cubic(p)), s, alpha=fade(t, t0, 0.15))
        x -= wdt + gap
    return total


def chip(ctx, t, t0, label, cx, cy, bg=RED, fg=WHITE, size=40, icon=None, alpha=1.0):
    p = prog(t, t0, 0.5)
    if p <= 0:
        return
    sp = text(label, size, fg, SANS)
    pad = 11
    w = sp.w - 2 * pad + 56 + (52 if icon else 0)
    h = size * 1.75
    s = ease_out_back(p, 2.0)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    sh, sp_pad = soft_shadow(int(w), int(h), int(h / 2), 14, 0.35)
    blit(ctx, sh, 0, 8, alpha=alpha)
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    fill(ctx, with_a(bg, alpha))
    tx = -26 if icon else 0
    blit(ctx, sp, tx + (26 if icon else 0) - (26 if icon else 0), 2, alpha=alpha)
    if icon == "camera":
        x0 = w / 2 - 62
        rrect(ctx, x0, -15, 40, 30, 7)
        fill(ctx, with_a(fg, alpha))
        circle(ctx, x0 + 20, 0, 9, with_a(bg, alpha))
        circle(ctx, x0 + 20, 0, 5, with_a(fg, alpha))
    elif icon == "pin":
        x0 = w / 2 - 44
        pin_shape(ctx, x0, 12, 34, with_a(fg, alpha), with_a(bg, alpha))
    ctx.restore()


def pin_shape(ctx, x, y, h, c, hole):
    """Map pin with its tip at (x, y)."""
    r = h * 0.36
    cy = y - h + r
    ctx.new_path()
    ctx.arc(x, cy, r, math.pi * 0.85, math.pi * 0.15)
    ctx.line_to(x, y)
    ctx.close_path()
    fill(ctx, c)
    circle(ctx, x, cy, r * 0.42, hole)


def heart(ctx, x, y, s, c):
    ctx.new_path()
    ctx.move_to(x, y + s * 0.35)
    ctx.curve_to(x - s * 1.1, y - s * 0.35, x - s * 0.45, y - s * 1.05, x, y - s * 0.45)
    ctx.curve_to(x + s * 0.45, y - s * 1.05, x + s * 1.1, y - s * 0.35, x, y + s * 0.35)
    fill(ctx, c)


def underline(ctx, t, t0, cx, cy, w, c=RED, h=12, dur=0.4):
    p = ease_out_expo(prog(t, t0, dur))
    if p > 0:
        rrect(ctx, cx + w / 2 - w * p, cy - h / 2, w * p, h, h / 2)
        fill(ctx, c)


# ===================================================================== A
@scene(0.0, T["othman"], "none")
def s_question(ctx, t, fr):
    bg_radial(ctx, t, WINE, INK)
    bg_pattern_dots(ctx, t, with_a(WHITE, 0.05))
    chip(ctx, t, 0.08, "المصوّر يسأل", 540, 120, RED, WHITE, 36, icon="camera")
    # giant question mark, left, elastic in + idle bob
    p = prog(t, T["endak"] - 0.15, 0.9)
    if p > 0:
        q = text("؟", 420, RED2, KUFI, shadow=16)
        bob = math.sin(t * 5) * 10
        rot = -0.35 * (1 - ease_out_elastic(p)) + math.sin(t * 3) * 0.04
        blit(ctx, q, 230, 560 + bob, ease_out_elastic(p), rot)
        for k in range(3):
            shockwave(ctx, t, T["endak"] + k * 0.35, 230, 560, 300, 0.9, RED2, 10)
    s = 1 + 0.12 * math.exp(-8 * max(0, t - T["hani2"])) * (t > T["hani2"])
    nm = text("هاني", 190, WHITE, KUFI, shadow=12)
    pn = prog(t, T["hani"], 0.5)
    if pn > 0:
        blit(ctx, nm, 640, 330, (0.4 + 0.6 * ease_out_back(pn, 2.5)) * s, alpha=fade(t, T["hani"], 0.15))
        underline(ctx, t, T["hani"] + 0.15, 640, 450, 330, RED, 14)
    shockwave(ctx, t, T["hani2"], 640, 330, 380, 0.6, WHITE, 12)
    word_row(ctx, t, [("إيش", T["eish"], GOLD), ("عندك", T["endak"], WHITE)], 640, 640, 130)
    vignette(ctx, 0.5)


# ===================================================================== B
@scene(T["othman"], T["youm"], "zoom")
def s_salawat(ctx, t, fr):
    lt = t - T["othman"]
    bg_radial(ctx, t, hexc("3A0710"), INK)
    cx, cy = 540, 470
    # rotating rays
    rays(ctx, cx, cy, 120, 900, 18, lt * 0.15, 0.55, with_a(GOLD, 0.06))
    # geometric 8-point stars drawing on
    for i, (r, a) in enumerate(((300, 0.9), (220, 0.6), (380, 0.35))):
        p = ease_out_cubic(prog(t, T["othman"] + i * 0.12, 0.9))
        if p <= 0:
            continue
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(lt * (0.18 if i % 2 == 0 else -0.14) + i * 0.2)
        for k in range(2):
            ctx.save()
            ctx.rotate(k * math.pi / 4)
            ctx.rectangle(-r * 0.7, -r * 0.7, r * 1.4, r * 1.4)
            ctx.restore()
        ctx.set_line_width(4 if i == 0 else 2.5)
        per = r * 1.4 * 4 * 2
        ctx.set_dash([per * p, per])
        ctx.set_source_rgba(*with_a(GOLD, a))
        ctx.stroke()
        ctx.set_dash([])
        ctx.restore()
    circle(ctx, cx, cy, 160 * ease_out_back(prog(t, T["othman"], 0.6)), with_a(GOLD, 0.08))
    nm = text("عثمان", 70, GOLD, KUFI_B, shadow=8)
    blit(ctx, nm, cx, 150, pop(t, T["othman"]), alpha=fade(t, T["othman"]))
    sp = text("صلّي على النبي", 120, WHITE, KUFI, shadow=12, glow=14, glow_color=with_a(GOLD, 0.6))
    wipe_rtl(ctx, sp, cx, cy, ease_io(prog(t, T["salli"] - 0.05, 0.6)))
    sl = text("ﷺ", 110, GOLD, F + "NotoNaskhArabic-Bold.ttf", shadow=6)
    blit(ctx, sl, cx, cy + 170, pop(t, T["salli"] + 0.5, 0.5), alpha=fade(t, T["salli"] + 0.5))
    for i in range(10):
        r = random.Random(i)
        ph = r.uniform(0, 6)
        sparkle(ctx, cx + math.cos(ph + lt * 0.6) * r.uniform(260, 420), cy + math.sin(ph + lt * 0.6) * r.uniform(200, 330),
                r.uniform(6, 14), fade(t, T["othman"] + 0.2 + i * 0.05) * (0.5 + 0.5 * math.sin(lt * 6 + ph)), GOLD)
    vignette(ctx, 0.55)


# ===================================================================== C
def calendar(ctx, x, y, s, flip, t):
    w, h = 340, 380
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    sh, _ = soft_shadow(w, h, 34, 22, 0.45)
    blit(ctx, sh, 0, 22)
    rrect(ctx, -w / 2, -h / 2, w, h, 34)
    fill(ctx, WHITE)
    ctx.save()
    rrect(ctx, -w / 2, -h / 2, w, h, 34)
    ctx.clip()
    ctx.rectangle(-w / 2, -h / 2, w, 110)
    fill(ctx, RED)
    ctx.restore()
    for dx in (-90, 90):
        rrect(ctx, dx - 12, -h / 2 - 30, 24, 60, 12)
        fill(ctx, hexc("3B3B3B"))
    blit(ctx, text("اليوم", 52, WHITE, KUFI_B), 0, -h / 2 + 55)
    ctx.save()
    ctx.translate(0, 50)
    ctx.scale(1, max(0.001, flip))
    blit(ctx, text("الخميس", 68, INK, KUFI), 0, 0)
    ctx.restore()
    ctx.restore()


def steak(ctx, x, y, s, rot):
    """T-bone steak: fat rim, marbled meat, bone."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    sh, _ = soft_shadow(420, 420, 210, 24, 0.45)
    blit(ctx, sh, 0, 30)
    circle(ctx, 0, 0, 205, CREAM)
    ring(ctx, 0, 0, 170, 4, hexc("E7D6BC"))

    def blob(k, dx=0, dy=0):
        ctx.new_path()
        ctx.move_to(-165 * k + dx, 10 * k + dy)
        ctx.curve_to(-175 * k + dx, -95 * k + dy, -60 * k + dx, -128 * k + dy, 30 * k + dx, -104 * k + dy)
        ctx.curve_to(95 * k + dx, -88 * k + dy, 110 * k + dx, -40 * k + dy, 160 * k + dx, -22 * k + dy)
        ctx.curve_to(205 * k + dx, 0 + dy, 190 * k + dx, 88 * k + dy, 110 * k + dx, 100 * k + dy)
        ctx.curve_to(20 * k + dx, 114 * k + dy, -150 * k + dx, 120 * k + dy, -165 * k + dx, 10 * k + dy)
        ctx.close_path()
    blob(1.0)
    fill(ctx, hexc("FFE9DA"))
    blob(0.84, 4, 4)
    g = cairo.RadialGradient(-40, -40, 10, 0, 0, 190)
    g.add_color_stop_rgba(0, *hexc("C42A33"))
    g.add_color_stop_rgba(1, *hexc("6A0A12"))
    ctx.set_source(g)
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(1, 0.86, 0.82, 0.45)
    for (a, b, c, d, lw) in ((-120, -20, -40, -60, 5), (-90, 40, 10, 10, 4), (40, -50, 110, 20, 4), (-30, 70, 80, 60, 3)):
        ctx.set_line_width(lw)
        ctx.move_to(a, b)
        ctx.curve_to(a + 30, b - 25, c - 30, d + 25, c, d)
        ctx.stroke()
    # T bone
    ctx.set_line_width(20)
    ctx.set_source_rgba(*hexc("FFF6EC"))
    ctx.move_to(-20, -96)
    ctx.curve_to(-5, -30, -10, 40, -30, 104)
    ctx.stroke()
    ctx.move_to(-14, -10)
    ctx.line_to(120, -12)
    ctx.stroke()
    # glossy highlight
    ctx.new_path()
    ctx.save()
    ctx.translate(-80, -55)
    ctx.scale(1, 0.4)
    ctx.arc(0, 0, 45, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.18)
    ctx.fill()
    ctx.restore()


@scene(T["youm"], T["kaman"], "swipe")
def s_thursday(ctx, t, fr):
    lt = t - T["youm"]
    bg_radial(ctx, t, RED, DRED)
    bg_stripes(ctx, t, with_a(WHITE, 0.035))
    # calendar: drops in, then shrinks into the corner
    pd = spring(prog(t, T["youm"] - 0.05, 0.9) * 1.0)
    move = ease_io(prog(t, T["ahsan"] - 0.1, 0.45))
    x = lerp(540, 830, move)
    y = lerp(-300, 470, pd) if move == 0 else lerp(470, 250, move)
    s = lerp(1.15, 0.62, move)
    flip = ease_out_back(prog(t, T["khamis"], 0.35), 2.0)
    calendar(ctx, x, y, s, flip, t)
    if move > 0:
        # starburst offer badge
        pb = pop(t, T["orood"] - 0.05, 0.5)
        if pb > 0:
            ctx.save()
            ctx.translate(320, 290)
            ctx.scale(pb, pb)
            ctx.rotate(-0.12 + lt * 0.25)
            star_path(ctx, 0, 0, 190, 160, 22)
            fill(ctx, GOLD)
            ctx.restore()
            blit(ctx, text("أحسن", 56, DRED, KUFI_B), 320, 235, pb, -0.12)
            blit(ctx, text("عروض", 96, INK, KUFI), 320, 315, pb, -0.12)
            shockwave(ctx, t, T["orood"], 320, 290, 330, 0.6, WHITE, 12)
        ps = prog(t, T["lahme"] - 0.25, 0.6)
        if ps > 0:
            e = ease_out_back(ps, 1.6)
            steak(ctx, lerp(1300, 560, e), 600 + math.sin(t * 3) * 6, 0.92, lerp(0.6, -0.08, e))
            blit(ctx, text("على اللحمة", 78, WHITE, KUFI, shadow=10), 560, 835, pop(t, T["lahme"]), alpha=fade(t, T["lahme"]))
        Burst(T["moallem"], 560, 650, 40, seed=3, kind="star", colors=(GOLD, WHITE), speed=(400, 900)).draw(ctx, t)
    vignette(ctx, 0.45)


# ===================================================================== D
@scene(T["kaman"], T["c1"] - 0.25, "liquid")
def s_cola(ctx, t, fr):
    lt = t - T["kaman"]
    bg_radial(ctx, t, RED2, DRED, cy=520)
    bubbles(ctx, t, 11, 34, (0, 0, W, TOPH), WHITE, 140, 12)
    big = text("الكولا", 300, with_a(WHITE, 1), KUFI)
    pc = ease_out_expo(prog(t, T["cola"] - 0.05, 0.6))
    if pc > 0:
        blit(ctx, big, 540, 470, lerp(1.25, 1.0, pc), alpha=0.22 * pc)
    pr = spring(prog(t, T["kaman"] + 0.15, 1.2))
    cy = lerp(1300, 500, pr)
    sway = math.sin(lt * 2.2) * 0.06
    can_shadow(ctx, 540, cy + 40, 520, 0.4 * pr)
    shine = prog(t, T["cola"], 0.7)
    draw_can(ctx, 540, cy, 520, sway, 1, shine if 0 < shine < 1 else 0)
    chip(ctx, t, T["kaman"], "وكمان", 540, 110, GOLD, INK, 46)
    word_row(ctx, t, [("عروض", T["orood2"], WHITE), ("على", T["orood2"] + 0.32, WHITE)], 255, 330, 88)
    pcl = prog(t, T["cola"], 0.5)
    if pcl > 0:
        sp = text("الكولا", 120, WHITE, KUFI, shadow=14)
        blit(ctx, sp, 820, 650, ease_out_back(pcl, 2.2), -0.08)
        underline(ctx, t, T["cola"] + 0.12, 820, 740, 300, GOLD, 12)
    Burst(T["baba"], 540, 380, 26, seed=9, kind="spark", colors=(WHITE, GOLD), speed=(300, 700), life=1.0).draw(ctx, t)
    vignette(ctx, 0.4)


# ===================================================================== E
SLOTS = [(780, 470), (540, 470), (300, 470), (780, 735), (540, 735), (300, 735)]  # RTL order
NUM_AR = ["واحدة", "اثنين", "ثلاثة", "أربعة", "خمسة", "ستة"]


@scene(T["c1"] - 0.25, T["sit"], "circle")
def s_count(ctx, t, fr):
    bg_radial(ctx, t, hexc("5A0710"), INK, cy=560)
    bg_pattern_dots(ctx, t, with_a(WHITE, 0.04))
    n = sum(1 for c in COUNTS if t >= c - 0.05)
    # slots
    for i, (sx, sy) in enumerate(SLOTS):
        empty = i >= n
        if empty:
            pulse = 0.5 + 0.5 * math.sin(t * 9) if (T["lissa"] - 0.1 < t < T["c5"] - 0.05 and i >= 4) else 0
            ctx.save()
            rrect(ctx, sx - 95, sy - 120, 190, 240, 30)
            ctx.set_dash([16, 12], t * 40)
            ctx.set_line_width(4 + 3 * pulse)
            ctx.set_source_rgba(*with_a(GOLD if pulse else WHITE, 0.25 + 0.6 * pulse))
            ctx.stroke()
            ctx.restore()
            blit(ctx, text(str(i + 1), 60, with_a(WHITE, 0.18), NUM), sx, sy)
    for i, c in enumerate(COUNTS):
        p = prog(t, c - 0.22, 0.22)
        if p <= 0:
            continue
        sx, sy = SLOTS[i]
        # drop with gravity, then squash-bounce
        land = c
        if t < land:
            e = ease_in_cubic(p)
            y = lerp(-250, sy, e)
            draw_can(ctx, sx, y, 220, 0, 1)
        else:
            dt = t - land
            sq = math.exp(-7 * dt) * math.sin(dt * 28) * 0.12
            wave = 0
            if t > T["c6"]:
                wave = math.exp(-4 * (t - T["c6"])) * math.sin((t - T["c6"]) * 14 - i * 0.9) * 18
            can_shadow(ctx, sx, sy + 8, 220, 0.45)
            ctx.save()
            ctx.translate(sx, sy + 110)
            ctx.scale(1 + sq, 1 - sq)
            ctx.translate(-sx, -(sy + 110))
            draw_can(ctx, sx, sy - wave, 220, 0, 1, prog(t, T["c6"] + 0.1 + i * 0.05, 0.5) if t > T["c6"] else 0)
            ctx.restore()
            shockwave(ctx, t, land, sx, sy + 100, 150, 0.45, GOLD, 8)
    # counter header
    cx, cy = 540, 175
    if n > 0:
        last = COUNTS[n - 1]
        pk = prog(t, last, 0.35)
        done = n == 6
        col = GOLD if done else WHITE
        num = text(str(n), 210, col, NUM, shadow=12)
        if n > 1 and pk < 1:
            old = text(str(n - 1), 210, WHITE, NUM, shadow=12)
            blit(ctx, old, cx + 120, cy - 120 * ease_out_cubic(pk), 1, alpha=1 - pk)
        blit(ctx, num, cx + 120, cy + 90 * (1 - ease_out_back(pk, 1.8)), 1, alpha=fade(t, last, 0.12))
        blit(ctx, text(NUM_AR[n - 1], 70, col, KUFI), cx - 110, cy - 10, pop(t, last, 0.35))
        # progress segments
        for k in range(6):
            fillp = ease_out_expo(prog(t, COUNTS[k], 0.3))
            x = cx + 250 - k * 84
            rrect(ctx, x - 74, cy + 112, 74, 14, 7)
            fill(ctx, with_a(WHITE, 0.16))
            if fillp > 0:
                rrect(ctx, x - 74 * fillp, cy + 112, 74 * fillp, 14, 7)
                fill(ctx, GOLD if done else RED2)
    if T["lissa"] - 0.05 < t < T["c5"] + 0.2:
        a = fade(t, T["lissa"] - 0.05, 0.15) * out(t, T["c5"], 0.2)
        wig = math.sin((t - T["lissa"]) * 22) * 0.12 * math.exp(-2.5 * (t - T["lissa"]))
        ctx.save()
        ctx.translate(180, 170)
        ctx.rotate(-0.12 + wig)
        ctx.scale(pop(t, T["lissa"] - 0.05), pop(t, T["lissa"] - 0.05))
        rrect(ctx, -140, -70, 280, 140, 34)
        fill(ctx, with_a(GOLD, a))
        blit(ctx, text("لسّه", 92, INK, KUFI), 0, -2, alpha=a)
        ctx.restore()
        blit(ctx, text("ما خلّصتش", 48, WHITE, SANS), 180, 285, pop(t, T["khallast"] - 0.2), alpha=a)
    if t > T["c6"]:
        rays(ctx, 660, 175, 80, 520, 16, t * 0.6, 0.5, with_a(GOLD, 0.12 * fade(t, T["c6"], 0.3)))
        Burst(T["c6"], 540, 600, 70, seed=6).draw(ctx, t)
        Burst(T["baba2"], 540, 200, 30, seed=16, kind="star", colors=(GOLD, WHITE), speed=(300, 800)).draw(ctx, t)
    vignette(ctx, 0.5)


# ===================================================================== F
def price_tag(ctx, x, y, angle, s, label_fn, flip=1.0):
    """Swinging tag hung from (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.move_to(0, 0)
    ctx.line_to(0, 120)
    ctx.set_line_width(4)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.stroke()
    circle(ctx, 0, 0, 9, WHITE)
    ctx.translate(0, 120)
    ctx.scale(s * flip, s)
    w, h = 360, 400
    sh, _ = soft_shadow(w, h, 40, 22, 0.5)
    blit(ctx, sh, 18, h / 2 + 30)
    ctx.new_path()
    ctx.move_to(0, 0)
    ctx.line_to(w / 2, 70)
    ctx.line_to(w / 2, h - 30)
    ctx.arc(w / 2 - 30, h - 30, 30, 0, math.pi / 2)
    ctx.line_to(-w / 2 + 30, h)
    ctx.arc(-w / 2 + 30, h - 30, 30, math.pi / 2, math.pi)
    ctx.line_to(-w / 2, 70)
    ctx.close_path()
    fill(ctx, CREAM)
    circle(ctx, 0, 52, 16, hexc("C9B79C"))
    label_fn(ctx, w, h)
    ctx.restore()


def mini_pack(ctx, cx, cy, s, t, t0, stagger=0.06):
    pos = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0)]
    for k, (i, j) in enumerate(pos):
        p = prog(t, t0 + k * stagger, 0.45)
        if p <= 0:
            continue
        e = ease_out_back(p, 2.0)
        x = cx + i * 92 * s
        y = cy + j * 70 * s + (1 - e) * 120
        sc = 0.88 if j < 0 else 1.0
        draw_can(ctx, x, y, 170 * s * sc * e, 0, 1 if j == 0 else 0.92)


@scene(T["sit"], T["mish"], "swipe")
def s_ask_price(ctx, t, fr):
    bg_radial(ctx, t, hexc("2C0A10"), INK)
    # spotlight cone
    g = cairo.RadialGradient(720, 380, 20, 720, 380, 520)
    g.add_color_stop_rgba(0, 1, 0.85, 0.6, 0.14)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.paint()
    chip(ctx, t, T["sit"] - 0.05, "المصوّر يسأل", 540, 95, RED, WHITE, 34, icon="camera")
    mini_pack(ctx, 300, 520, 1.0, t, T["sit"], 0.05)
    blit(ctx, text("6 علب", 86, WHITE, KUFI, shadow=10), 300, 780, pop(t, T["sit"] + 0.2), alpha=fade(t, T["sit"] + 0.2))
    pt = prog(t, T["bikam"] - 0.3, 0.5)
    if pt > 0:
        sw = t - (T["bikam"] - 0.3)
        angle = 0.45 * math.exp(-1.6 * sw) * math.cos(sw * 5.2) + 0.02 * math.sin(t * 1.7)
        fl = 1.0
        rev = prog(t, T["b15"] - 0.1, 0.4)
        if 0 < rev < 1:
            fl = abs(math.cos(rev * math.pi))
        show15 = rev >= 0.5

        def label(ctx, w, h):
            if not show15:
                q = text("؟", 230, RED, KUFI)
                blit(ctx, q, 0, 230 + math.sin(t * 6) * 6, 1)
                blit(ctx, text("بكم", 60, DRED, KUFI_B), 0, 345)
            else:
                blit(ctx, text("15", 190, DRED, NUM), 18, 215)
                blit(ctx, text("₪", 80, DRED, SYM), -120, 225)
                blit(ctx, text("بخمستعش؟", 46, INK, KUFI_B), 0, 345)
        y = lerp(-500, 150, ease_out_back(pt, 1.3))
        price_tag(ctx, 750, y, angle, 0.95, label, fl)
    vignette(ctx, 0.5)


# ===================================================================== G
@scene(T["mish"], T["hadool3"], "cut")
def s_not15(ctx, t, fr):
    lt = t - T["mish"]
    bg_radial(ctx, t, hexc("B3121E"), hexc("3A0307"))
    bg_stripes(ctx, t, with_a(INK, 0.18), 46, 160)

    def label(ctx, w, h):
        blit(ctx, text("15", 190, DRED, NUM), 18, 215)
        blit(ctx, text("₪", 80, DRED, SYM), -120, 225)
    price_tag(ctx, 720, 150, 0.06 * math.sin(lt * 8) * math.exp(-2 * lt), 0.95, label)
    # the red X, two slashes
    for k, (a, b, c, d) in enumerate(((560, 330, 890, 690), (890, 330, 560, 690))):
        p = ease_out_expo(prog(t, T["mish"] + 0.05 + k * 0.13, 0.18))
        if p > 0:
            ctx.move_to(a, b)
            ctx.line_to(lerp(a, c, p), lerp(b, d, p))
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_width(46)
            ctx.set_source_rgba(0, 0, 0, 0.35)
            ctx.stroke_preserve()
            ctx.set_line_width(36)
            ctx.set_source_rgba(*WHITE)
            ctx.stroke()
    ps = prog(t, T["mish"], 0.28)
    mish = text("مش", 220, WHITE, KUFI, shadow=16)
    blit(ctx, mish, 285, 360, lerp(2.6, 1.0, ease_out_expo(ps)), -0.1, alpha=fade(t, T["mish"], 0.08))
    shockwave(ctx, t, T["mish"] + 0.05, 285, 360, 500, 0.6, WHITE, 18)
    k15 = text("خمستعش", 92, GOLD, KUFI, shadow=10)
    pk = prog(t, T["k15"], 0.35)
    blit(ctx, k15, 270, 700, pop(t, T["k15"]), -0.05, alpha=fade(t, T["k15"]))
    sl = ease_out_expo(prog(t, T["k15"] + 0.25, 0.25))
    if sl > 0:
        rrect(ctx, 270 + 190 - 380 * sl, 700 - 6, 380 * sl, 14, 7)
        fill(ctx, WHITE)
    vignette(ctx, 0.5)


# ===================================================================== H
@scene(T["hadool3"], T["taqm"], "circle")
def s_reveal(ctx, t, fr):
    lt = t - T["hadool3"]
    bg_radial(ctx, t, RED2, DRED, cy=520)
    hit = T["ashra"]
    if t > hit - 0.05:
        rays(ctx, 540, 500, 40, 1100, 20, t * 0.35, 0.55, with_a(GOLD, 0.18 * fade(t, hit, 0.2)))
        rays(ctx, 540, 500, 40, 1100, 20, -t * 0.2, 0.25, with_a(WHITE, 0.08 * fade(t, hit, 0.2)))
    for k in range(6):
        p = prog(t, T["hadool3"] + k * 0.06, 0.45)
        x = 790 - k * 108
        if p > 0:
            draw_can(ctx, x, lerp(-150, 140, ease_out_back(p, 1.8)) + math.sin(t * 4 + k) * 5, 170)
    blit(ctx, text("الستة", 60, WHITE, KUFI_B, shadow=8), 540, 275, pop(t, T["sitte"]), alpha=fade(t, T["sitte"]))
    # slot-machine roll 15 -> 10
    roll0 = T["sitte"] + 0.1
    if t >= roll0:
        if t < hit:
            p = prog(t, roll0, hit - roll0)
            n = 15 - int(ease_in_cubic(p) * 5)
            n = max(11, n)
            jitter = math.sin(t * 60) * 10
            blit(ctx, text(str(n), 300, with_a(WHITE, 0.8), NUM, shadow=14), 560, 520 + jitter, 1.0)
        else:
            dt = t - hit
            s = 1 + 0.5 * math.exp(-9 * dt) * math.cos(dt * 30)
            blit(ctx, text("10", 330, WHITE, NUM, shadow=18, glow=20, glow_color=with_a(GOLD, 0.8)), 600, 515, s)
            blit(ctx, text("₪", 150, GOLD, SYM, shadow=10), 300, 540, pop(t, hit + 0.12))
            shockwave(ctx, t, hit, 540, 520, 600, 0.7, WHITE, 24)
            shockwave(ctx, t, hit + 0.1, 540, 520, 480, 0.7, GOLD, 14)
    ps = prog(t, T["shekel"], 0.5)
    if ps > 0:
        sp = text("بعشرة شيكل", 96, INK, KUFI)
        w = sp.w - 30
        ctx.save()
        ctx.translate(540, 790)
        ctx.scale(ease_out_back(ps, 2), ease_out_back(ps, 2))
        rrect(ctx, -w / 2 - 20, -62, w + 40, 124, 62)
        fill(ctx, GOLD)
        blit(ctx, sp, 0, 4)
        ctx.restore()
    Burst(hit, 540, 520, 120, seed=10, speed=(700, 1700), life=2.0).draw(ctx, t)
    Burst(T["hajj"], 540, 790, 30, seed=11, kind="star", colors=(WHITE, GOLD), speed=(300, 700)).draw(ctx, t)
    vignette(ctx, 0.4)


# ===================================================================== I
def six_pack(ctx, cx, cy, t, t0, shine_t):
    back = [(-1, 0), (0, 0), (1, 0)]
    for row, ys, sc, al in ((0, -70, 0.86, 0.9), (1, 40, 1.0, 1.0)):
        for k, (i, _) in enumerate(back):
            idx = row * 3 + k
            p = prog(t, t0 + idx * 0.07, 0.5)
            if p <= 0:
                continue
            e = ease_out_back(p, 1.8)
            x = cx + i * 150 * (0.92 if row == 0 else 1) + (25 if row == 0 else 0)
            y = cy + ys + (1 - e) * 200
            if row == 1:
                can_shadow(ctx, x, y, 300 * sc, 0.3)
            sh = prog(t, shine_t + idx * 0.08, 0.6)
            draw_can(ctx, x, y, 300 * sc, 0, al, sh if 0 < sh < 1 else 0)
    # cardboard band
    p = ease_out_expo(prog(t, t0 + 0.45, 0.4))
    if p > 0:
        w = 480 * p
        rrect(ctx, cx - w / 2, cy + 70, w, 70, 14)
        fill(ctx, hexc("1E1E1E"))
        blit(ctx, text("طقم 6", 44, WHITE, KUFI_B), cx, cy + 105, 1, alpha=p)


@scene(T["taqm"], T["haje"], "swipe")
def s_product(ctx, t, fr):
    lt = t - T["taqm"]
    bg_radial(ctx, t, WHITE, CREAM, drift=0.5)
    bg_pattern_dots(ctx, t, with_a(RED, 0.08), 48, 3, 10)
    six_pack(ctx, 540, 470, t, T["taqm"], T["coke"] + 0.2)
    sp = text("كوكاكولا", 150, RED, KUFI, shadow=6)
    wipe_rtl(ctx, sp, 540, 140, ease_io(prog(t, T["coke"] - 0.05, 0.5)))
    underline(ctx, t, T["coke"] + 0.25, 540, 235, 420, INK, 10)
    # price sticker
    pp = prog(t, T["ashra2"] - 0.05, 0.4)
    if pp > 0:
        e = lerp(2.4, 1.0, ease_out_back(pp, 1.5))
        ctx.save()
        ctx.translate(845, 330)
        ctx.rotate(0.2 + 0.03 * math.sin(lt * 3))
        ctx.scale(e, e)
        star_path(ctx, 0, 0, 150, 130, 24)
        fill(ctx, RED)
        circle(ctx, 0, 0, 118, with_a(WHITE, 0.15))
        blit(ctx, text("10", 120, WHITE, NUM), 18, -12)
        blit(ctx, text("₪", 58, WHITE, SYM), -70, -6)
        blit(ctx, text("شيكل", 40, WHITE, KUFI_B), 0, 72)
        ctx.restore()
        shockwave(ctx, t, T["ashra2"] + 0.1, 845, 330, 260, 0.5, RED, 10)
    chip(ctx, t, T["taqm"] + 0.1, "طقم الستة", 250, 790, INK, WHITE, 46)
    pm = prog(t, T["ml300"] - 0.05, 0.5)
    if pm > 0:
        ctx.save()
        ctx.translate(800, 790)
        e = ease_out_back(pm, 2)
        ctx.scale(e, e)
        rrect(ctx, -170, -58, 340, 116, 58)
        fill(ctx, RED)
        blit(ctx, text("300 مل", 64, WHITE, KUFI), 0, 2)
        ctx.restore()
    for i in range(7):
        r = random.Random(40 + i)
        tw = 0.5 + 0.5 * math.sin(t * 5 + i * 1.7)
        sparkle(ctx, r.uniform(220, 860), r.uniform(330, 640), r.uniform(10, 20), tw * fade(t, T["ml300"] + 0.6), WHITE)


# ===================================================================== J
@scene(T["haje"], T["ind"], "zoom")
def s_stamp(ctx, t, fr):
    lt = t - T["haje"]
    bg_radial(ctx, t, RED, hexc("5C040B"))
    rays(ctx, 540, 470, 60, 1100, 24, t * 0.25, 0.5, with_a(WHITE, 0.06))
    p = prog(t, T["haje"] - 0.05, 0.3)
    if p > 0:
        e = ease_out_expo(p)
        s = lerp(2.8, 1.0, e)
        rot = lerp(-0.6, -0.14, e) + 0.02 * math.sin(lt * 2)
        ctx.save()
        ctx.translate(540, 470)
        ctx.rotate(rot)
        ctx.scale(s, s)
        star_path(ctx, 0, 0, 330, 305, 36)
        fill(ctx, GOLD)
        ring(ctx, 0, 0, 270, 10, DRED)
        ring(ctx, 0, 0, 245, 4, DRED)
        blit(ctx, text("حاجة", 92, DRED, KUFI), 0, -110)
        pa = prog(t, T["alf"], 0.4)
        if pa > 0:
            blit(ctx, text("ألف", 210, DRED, KUFI), 0, 50, ease_out_back(pa, 2.6))
        for k in range(5):
            a = math.pi + (k - 2) * 0.32
            star_path(ctx, math.cos(a + math.pi) * 195, -math.sin(a) * 0 + 190 - abs(k - 2) * 22, 20, 8, 5)
            fill(ctx, with_a(DRED, fade(t, T["alf"] + 0.2 + k * 0.06)))
        ctx.restore()
        shockwave(ctx, t, T["haje"] + 0.22, 540, 470, 520, 0.6, WHITE, 18)
    Burst(T["alf"], 540, 470, 60, seed=21, kind="star", colors=(GOLD, WHITE), speed=(600, 1300), life=1.5).draw(ctx, t)
    Burst(T["baba3"], 540, 470, 40, seed=22, speed=(500, 1100)).draw(ctx, t)
    vignette(ctx, 0.45)


# ===================================================================== K
def awning(ctx, t, t0, y_bottom=250):
    p = spring(prog(t, t0, 0.9))
    off = (1 - p) * -300
    n = 9
    sw = W / n
    for i in range(n):
        ctx.new_path()
        x = i * sw
        ctx.rectangle(x, off - 10, sw, y_bottom - 40 + 10)
        fill(ctx, RED if i % 2 == 0 else WHITE)
        ctx.new_path()
        ctx.arc(x + sw / 2, off + y_bottom - 40, sw / 2, 0, math.pi)
        fill(ctx, RED if i % 2 == 0 else WHITE)
    g = cairo.LinearGradient(0, off, 0, off + y_bottom)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.25)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.rectangle(0, off, W, y_bottom)
    ctx.set_source(g)
    ctx.fill()


@scene(T["ind"], T["onwan"], "swipe")
def s_store(ctx, t, fr):
    bg_radial(ctx, t, hexc("3A0A10"), INK)
    bg_pattern_dots(ctx, t, with_a(WHITE, 0.04))
    awning(ctx, t, T["ind"] - 0.1)
    pb = ease_out_back(prog(t, T["ind"] + 0.05, 0.5), 1.6)
    if pb > 0:
        w, h = 900, 380
        ctx.save()
        ctx.translate(540, 570)
        ctx.scale(pb, pb)
        sh, _ = soft_shadow(w, h, 40, 26, 0.55)
        blit(ctx, sh, 0, 26)
        rrect(ctx, -w / 2, -h / 2, w, h, 40)
        fill(ctx, CREAM)
        rrect(ctx, -w / 2 + 16, -h / 2 + 16, w - 32, h - 32, 28)
        ctx.set_line_width(5)
        ctx.set_source_rgba(*RED)
        ctx.stroke()
        blit(ctx, text("عند", 54, INK, KUFI_B), 0, -120)
        sp = text("فروج الحلو", 170, RED, KUFI)
        wipe_rtl(ctx, sp, 0, 30, ease_io(prog(t, T["farouj"] - 0.05, 0.55)))
        sh = prog(t, T["helou"] + 0.2, 0.6)
        if 0 < sh < 1:
            sx = lerp(-w * 0.7, w * 0.7, sh)
            lg = cairo.LinearGradient(sx - 120, -h / 2, sx + 120, h / 2)
            lg.add_color_stop_rgba(0, 1, 1, 1, 0)
            lg.add_color_stop_rgba(0.5, 1, 1, 1, 0.5)
            lg.add_color_stop_rgba(1, 1, 1, 1, 0)
            rrect(ctx, -w / 2, -h / 2, w, h, 40)
            ctx.set_source(lg)
            ctx.fill()
        ctx.restore()
    Burst(T["helou"], 540, 570, 50, seed=31, kind="star", colors=(GOLD, WHITE), speed=(500, 1100)).draw(ctx, t)


# ===================================================================== L
STREET_Y = 560


@scene(T["onwan"], T["ahlan"], "circle")
def s_map(ctx, t, fr):
    lt = t - T["onwan"]
    ctx.set_source_rgba(*hexc("F6EFE3"))
    ctx.paint()
    # city blocks
    r = random.Random(5)
    for gx in range(-1, 7):
        for gy in range(-1, 6):
            p = fade(t, T["onwan"] + (gx + gy) * 0.03, 0.4)
            x, y = gx * 190 + 25, gy * 190 - 60
            if abs(y + 80 - STREET_Y) < 140:
                continue
            rrect(ctx, x, y, 150, 150, 18)
            fill(ctx, with_a(hexc("E9DCC6") if r.random() > 0.2 else hexc("D8E8CF"), p))
    # minor streets
    ctx.set_line_width(14)
    ctx.set_source_rgba(1, 1, 1, 0.9)
    for gx in range(0, 7):
        x = gx * 190 + 10
        ctx.move_to(x, -10)
        ctx.line_to(x, lerp(-10, TOPH + 10, ease_out_cubic(prog(t, T["onwan"] + gx * 0.04, 0.6))))
        ctx.stroke()
    # main street draws right-to-left
    ps = ease_io(prog(t, T["share"] - 0.1, 0.6))
    if ps > 0:
        x0 = W + 20
        x1 = lerp(x0, -20, ps)
        ctx.rectangle(x1, STREET_Y - 46, x0 - x1, 92)
        fill(ctx, hexc("3B3B40"))
        ctx.set_dash([34, 26])
        ctx.set_line_width(7)
        ctx.move_to(x0, STREET_Y)
        ctx.line_to(x1, STREET_Y)
        ctx.set_source_rgba(1, 0.85, 0.3, 0.95)
        ctx.stroke()
        ctx.set_dash([])
    pl = prog(t, T["nasr"] - 0.1, 0.4)
    if pl > 0:
        sp = text("شارع النصر", 60, WHITE, KUFI_B)
        w = sp.w - 10
        ctx.save()
        ctx.translate(290, STREET_Y)
        e = ease_out_back(pl, 2)
        ctx.scale(e, e)
        rrect(ctx, -w / 2, -40, w, 80, 16)
        fill(ctx, RED)
        blit(ctx, sp, 0, 2)
        ctx.restore()
    # shop pin above the street
    pp = prog(t, T["maroof"] - 0.1, 0.55)
    px, py = 780, STREET_Y - 70
    if pp > 0:
        dy = (1 - ease_out_back(pp, 2.2)) * -500
        ctx.save()
        ctx.translate(px, py + 10)
        ctx.scale(1, 0.3)
        circle(ctx, 0, 0, 40 * pp, (0, 0, 0, 0.25))
        ctx.restore()
        for k in range(2):
            pr = prog(t, T["maroof"] + 0.35 + k * 0.6, 1.0)
            if 0 < pr < 1:
                ctx.save()
                ctx.translate(px, py + 10)
                ctx.scale(1, 0.35)
                ring(ctx, 0, 0, 40 + 140 * pr, 5, with_a(RED, 1 - pr))
                ctx.restore()
        pin_shape(ctx, px, py + dy, 170, RED, WHITE)
        lab = text("فروج الحلو", 46, INK, KUFI_B)
        rrect(ctx, px - lab.w / 2, py - 290 + dy - 34, lab.w, 68, 34)
        fill(ctx, WHITE)
        blit(ctx, lab, px, py - 290 + dy)
    # tower opposite (below the street)
    pt = prog(t, T["burj"] - 0.1, 0.6)
    tx, ty = 680, STREET_Y + 60
    if pt > 0:
        hgt = 320 * ease_out_back(pt, 1.4)
        ctx.save()
        ctx.rectangle(0, ty, W, TOPH)
        ctx.clip()
        rrect(ctx, tx - 70, ty + 10, 140, hgt, 10)
        fill(ctx, hexc("2E4A6B"))
        for wy in range(int(ty + 40), int(ty + 10 + hgt), 38):
            for wx in (-40, 0, 40):
                ctx.rectangle(tx + wx - 12, wy, 24, 20)
        ctx.set_source_rgba(1, 0.9, 0.6, 0.85)
        ctx.fill()
        ctx.restore()
    pl2 = prog(t, T["shifa"] - 0.05, 0.4)
    if pl2 > 0:
        lab = text("برج الشفاء", 54, WHITE, KUFI_B)
        e = ease_out_back(pl2, 2)
        ctx.save()
        ctx.translate(380, ty + 200)
        ctx.scale(e, e)
        rrect(ctx, -lab.w / 2, -38, lab.w, 76, 18)
        fill(ctx, hexc("2E4A6B"))
        blit(ctx, lab, 0, 2)
        ctx.restore()
    # "opposite" connector arrow
    pc = ease_io(prog(t, T["mqabel"] - 0.05, 0.4))
    if pc > 0:
        ctx.set_line_width(6)
        ctx.set_dash([14, 10])
        ctx.set_source_rgba(*INK)
        ctx.move_to(px, py + 30)
        ctx.curve_to(px + 120 * pc, py + 80, tx + 140, ty, lerp(px, tx + 80, pc), lerp(py + 30, ty + 60, pc))
        ctx.stroke()
        ctx.set_dash([])
        lab = text("مقابل", 44, WHITE, KUFI_B)
        blit(ctx, lab, 940, STREET_Y + 2, pop(t, T["mqabel"]), alpha=fade(t, T["mqabel"]))
    chip(ctx, t, T["onwan"], "عنواننا معروف", 540, 95, INK, WHITE, 44, icon="pin")


# ===================================================================== M
@scene(T["ahlan"], T["hot"], "swipe")
def s_welcome(ctx, t, fr):
    lt = t - T["ahlan"]
    bg_radial(ctx, t, RED2, DRED)
    rays(ctx, 540, 400, 60, 1100, 16, t * 0.2, 0.5, with_a(WHITE, 0.05))
    r = random.Random(77)
    for i in range(16):
        x0 = r.uniform(60, 1020)
        sp = r.uniform(90, 180)
        ph = r.uniform(0, 4)
        y = TOPH + 60 - ((lt + ph) * sp) % (TOPH + 160)
        heart(ctx, x0 + math.sin(t * 2 + ph) * 18, y, r.uniform(14, 30), with_a(WHITE if i % 3 else GOLD, 0.35 * fade(t, T["ahlan"] + 0.2)))
    word_row(ctx, t, [("أهلاً", T["ahlan"], WHITE), ("وسهلاً", T["sahlan"], WHITE)], 540, 330, 170, shadow=14)
    blit(ctx, text("بكم", 120, GOLD, KUFI, shadow=12), 540, 520, pop(t, T["bikom"]), alpha=fade(t, T["bikom"]))
    pp = prog(t, T["tsharfuna"] - 0.05, 0.5)
    if pp > 0:
        e = ease_out_back(pp, 1.8)
        ctx.save()
        ctx.translate(540, 730)
        ctx.scale(e, e)
        rrect(ctx, -420, -70, 840, 140, 70)
        fill(ctx, CREAM)
        ctx.restore()
        word_row(ctx, t, [("تشرّفونا", T["tsharfuna"], RED), ("وبتنوّرونا", T["btnawruna"], DRED)], 540, 730, 68, KUFI, 26, shadow=0, rise=20)
    Burst(T["ahlan"], 540, 330, 80, seed=51, speed=(600, 1500)).draw(ctx, t)
    vignette(ctx, 0.4)


# ===================================================================== N
@scene(T["hot"], 99, "zoom")
def s_end(ctx, t, fr):
    lt = t - T["hot"]
    bg_radial(ctx, t, hexc("4A0A12"), INK)
    bg_pattern_dots(ctx, t, with_a(WHITE, 0.04))
    awning(ctx, t, T["hot"] - 0.05, 170)
    sp = text("فروج الحلو", 150, WHITE, KUFI, shadow=14)
    blit(ctx, sp, 540, 330, pop(t, T["hot"] + 0.05, 0.5), alpha=fade(t, T["hot"] + 0.05))
    p2 = prog(t, T["hot"] + 0.3, 0.5)
    if p2 > 0:
        e = ease_out_back(p2, 1.8)
        ctx.save()
        ctx.translate(540, 520)
        ctx.scale(e, e)
        rrect(ctx, -400, -78, 800, 156, 78)
        fill(ctx, GOLD)
        draw_can(ctx, 300, 0, 120, 0.15)
        blit(ctx, text("6 علب كولا", 64, INK, KUFI), 70, -4)
        blit(ctx, text("10", 80, DRED, NUM), -230, -6)
        blit(ctx, text("₪", 46, DRED, SYM), -310, 0)
        ctx.restore()
    p3 = prog(t, T["hot"] + 0.55, 0.5)
    if p3 > 0:
        lab = text("شارع النصر، مقابل برج الشفاء", 50, WHITE, KUFI_B)
        blit(ctx, lab, 520, 700 + 30 * (1 - ease_out_cubic(p3)), 1, alpha=ease_out_cubic(p3))
        pin_shape(ctx, 540 + lab.w / 2 + 10, 720, 60, RED2, INK)
    for i in range(8):
        rr = random.Random(90 + i)
        sparkle(ctx, rr.uniform(80, 1000), rr.uniform(220, 820), rr.uniform(8, 16),
                (0.5 + 0.5 * math.sin(t * 4 + i)) * fade(t, T["hot"] + 0.6), GOLD)
    vignette(ctx, 0.5)


SCHEDULE.sort(key=lambda s: s[0])
