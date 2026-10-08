"""Drawing toolkit: cairo for vectors, Pillow+raqm for shaped Arabic text."""
import math
import random
from functools import lru_cache

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, TOPH = 1080, 960

F = "/usr/share/fonts/truetype/noto/"
KUFI = F + "NotoKufiArabic-Black.ttf"
KUFI_B = F + "NotoKufiArabic-Bold.ttf"
SANS = F + "NotoSansArabic-ExtraBold.ttf"
SANS_B = F + "NotoSansArabic-Bold.ttf"
NUM = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


RED = hexc("E41E2B")
RED2 = hexc("FF3B47")
DRED = hexc("8E0A14")
WINE = hexc("4A040A")
INK = hexc("140305")
CREAM = hexc("FFF3DE")
GOLD = hexc("FFC83D")
WHITE = hexc("FFFFFF")
SILVER = hexc("D9DDE2")
GREEN = hexc("2BB673")


def with_a(c, a):
    return c[:3] + (c[3] * a,)


# ----------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def lerp(a, b, x):
    return a + (b - a) * x


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    return x ** 3


def ease_io(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_expo(x):
    return 1 if x >= 1 else 1 - 2 ** (-10 * x)


def ease_in_expo(x):
    return 0 if x <= 0 else 2 ** (10 * x - 10)


def ease_out_back(x, s=1.70158):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out_elastic(x):
    if x <= 0 or x >= 1:
        return clamp(x)
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


def spring(x, freq=4.5, damp=5.5):
    """Damped spring 0 -> 1 with overshoot."""
    if x <= 0:
        return 0.0
    return 1 - math.exp(-damp * x) * math.cos(freq * 2 * math.pi * x * 0.5)


def pop(t, start, dur=0.45):
    """Scale-in with overshoot."""
    return ease_out_back(prog(t, start, dur), 2.2)


def fade(t, start, dur=0.2):
    return ease_out_cubic(prog(t, start, dur))


def out(t, start, dur=0.2):
    return 1 - ease_in_cubic(prog(t, start, dur))


# ----------------------------------------------------------------- surfaces
def pil_to_surface(img):
    a = np.asarray(img.convert("RGBA"), dtype=np.uint16)
    alpha = a[..., 3]
    prem = (a[..., :3] * alpha[..., None] + 127) // 255
    h, w = alpha.shape
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    stride = surf.get_stride()
    buf = np.ndarray((h, stride // 4, 4), np.uint8, buffer=surf.get_data())
    buf[:, :w, 0] = prem[..., 2]
    buf[:, :w, 1] = prem[..., 1]
    buf[:, :w, 2] = prem[..., 0]
    buf[:, :w, 3] = alpha
    surf.mark_dirty()
    return surf


class Sprite:
    def __init__(self, surf, w, h):
        self.surf, self.w, self.h = surf, w, h


def _rgba255(c):
    return tuple(int(round(v * 255)) for v in c[:3]) + (int(round(c[3] * 255)),)


@lru_cache(maxsize=4096)
def text(s, size, color=WHITE, font=KUFI, stroke=0, stroke_color=INK, shadow=0, glow=0, glow_color=None):
    """Shaped RTL text rendered to a sprite. size in px."""
    f = ImageFont.truetype(font, size, layout_engine=ImageFont.Layout.RAQM)
    kw = dict(font=f, direction="rtl", language="ar", stroke_width=stroke)
    probe = ImageDraw.Draw(Image.new("L", (8, 8)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), s, **kw)
    pad = stroke + max(shadow, glow) * 3 + 8
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - x0, pad - y0), s, fill=_rgba255(color), stroke_fill=_rgba255(stroke_color), **kw)
    if glow:
        g = img.split()[3].filter(ImageFilter.GaussianBlur(glow))
        gc = _rgba255(glow_color or color)
        glayer = Image.new("RGBA", (w, h), gc[:3] + (0,))
        glayer.putalpha(g.point(lambda v: min(255, int(v * 1.6))))
        img = Image.alpha_composite(glayer, img)
    if shadow:
        a = img.split()[3].filter(ImageFilter.GaussianBlur(shadow))
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.55)))
        base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        base.alpha_composite(sh, (0, int(shadow * 0.8)))
        img = Image.alpha_composite(base, img)
    return Sprite(pil_to_surface(img), w, h)


@lru_cache(maxsize=64)
def soft_shadow(w, h, radius, blur, alpha=0.45):
    pad = blur * 3
    img = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(img).rounded_rectangle((pad, pad, pad + w, pad + h), radius, fill=int(255 * alpha))
    img = img.filter(ImageFilter.GaussianBlur(blur))
    rgba = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rgba.putalpha(img)
    return Sprite(pil_to_surface(rgba), *img.size), pad


def blit(ctx, sp, x, y, scale=1.0, rot=0.0, alpha=1.0, ax=0.5, ay=0.5, sx=1.0, sy=1.0):
    if alpha <= 0.003 or scale <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    if rot:
        ctx.rotate(rot)
    ctx.scale(scale * sx, scale * sy)
    ctx.translate(-sp.w * ax, -sp.h * ay)
    ctx.set_source_surface(sp.surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(clamp(alpha))
    ctx.restore()


def blit_motion(ctx, sp, x, y, vx, vy, n=4, **kw):
    """Cheap motion blur: ghost trail behind a moving sprite."""
    a = kw.pop("alpha", 1.0)
    for i in range(n, 0, -1):
        k = i / n
        blit(ctx, sp, x - vx * k, y - vy * k, alpha=a * 0.22 * (1 - k * 0.6), **kw)
    blit(ctx, sp, x, y, alpha=a, **kw)


def wipe_rtl(ctx, sp, x, y, p, scale=1.0, alpha=1.0, ax=0.5, ay=0.5):
    """Reveal a sprite right-to-left (the way Arabic reads)."""
    if p <= 0:
        return
    w, h = sp.w * scale, sp.h * scale
    left, top = x - w * ax, y - h * ay
    ctx.save()
    ctx.rectangle(left + w * (1 - p), top - 20, w * p + 2, h + 40)
    ctx.clip()
    blit(ctx, sp, x, y, scale, alpha=alpha, ax=ax, ay=ay)
    ctx.restore()


# ----------------------------------------------------------------- vector shapes
def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill(ctx, c):
    ctx.set_source_rgba(*c)
    ctx.fill()


def star_path(ctx, cx, cy, r_out, r_in, n, rot=0.0):
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n - math.pi / 2
        (ctx.move_to if i == 0 else ctx.line_to)(cx + r * math.cos(a), cy + r * math.sin(a))
    ctx.close_path()


def rays(ctx, cx, cy, r0, r1, n, rot, width_frac, c):
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        da = math.pi / n * width_frac
        ctx.move_to(cx + r0 * math.cos(a - da * 0.2), cy + r0 * math.sin(a - da * 0.2))
        ctx.line_to(cx + r1 * math.cos(a - da), cy + r1 * math.sin(a - da))
        ctx.line_to(cx + r1 * math.cos(a + da), cy + r1 * math.sin(a + da))
        ctx.line_to(cx + r0 * math.cos(a + da * 0.2), cy + r0 * math.sin(a + da * 0.2))
        ctx.close_path()
    ctx.set_source_rgba(*c)
    ctx.fill()


def ring(ctx, cx, cy, r, width, c):
    if r <= 0 or width <= 0:
        return
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.set_line_width(width)
    ctx.set_source_rgba(*c)
    ctx.stroke()


def circle(ctx, cx, cy, r, c):
    ctx.new_path()
    ctx.arc(cx, cy, max(r, 0), 0, 2 * math.pi)
    fill(ctx, c)


def shockwave(ctx, t, t0, cx, cy, rmax=420, dur=0.55, c=WHITE, width=18):
    p = prog(t, t0, dur)
    if 0 < p < 1:
        e = ease_out_cubic(p)
        ring(ctx, cx, cy, rmax * e, width * (1 - p) + 1, with_a(c, 0.85 * (1 - p)))


def draw_can(ctx, cx, cy, h, rot=0.0, alpha=1.0, shine=0.0):
    """Generic red soda can (no trademark), centred at cx, cy."""
    w = h * 0.52
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.push_group()
    # body
    top, bot = -h / 2 + h * 0.07, h / 2 - h * 0.035
    rrect(ctx, -w / 2, top, w, bot - top, w * 0.12)
    g = cairo.LinearGradient(-w / 2, 0, w / 2, 0)
    for o, c in ((0, DRED), (0.18, RED), (0.3, hexc("FF6A72")), (0.42, RED), (0.78, hexc("B5101C")), (1, hexc("5E050C"))):
        g.add_color_stop_rgba(o, *c)
    ctx.set_source(g)
    ctx.fill()
    # white ribbon
    ctx.new_path()
    ctx.move_to(-w / 2, h * 0.02)
    ctx.curve_to(-w * 0.15, -h * 0.12, w * 0.15, h * 0.16, w / 2, -h * 0.02)
    ctx.line_to(w / 2, h * 0.05)
    ctx.curve_to(w * 0.15, h * 0.24, -w * 0.15, -h * 0.03, -w / 2, h * 0.09)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.95)
    ctx.fill()
    # shoulder + lid
    sh = cairo.LinearGradient(-w / 2, 0, w / 2, 0)
    for o, c in ((0, hexc("7D838A")), (0.3, hexc("F4F6F8")), (0.55, hexc("B9BEC4")), (1, hexc("5D6268"))):
        sh.add_color_stop_rgba(o, *c)
    ctx.new_path()
    ctx.move_to(-w / 2, top + w * 0.1)
    ctx.curve_to(-w / 2, top - h * 0.02, -w * 0.42, -h / 2 + h * 0.015, -w * 0.4, -h / 2)
    ctx.line_to(w * 0.4, -h / 2)
    ctx.curve_to(w * 0.42, -h / 2 + h * 0.015, w / 2, top - h * 0.02, w / 2, top + w * 0.1)
    ctx.close_path()
    ctx.set_source(sh)
    ctx.fill()
    ctx.save()
    ctx.translate(0, -h / 2)
    ctx.scale(1, 0.22)
    ctx.arc(0, 0, w * 0.4, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(*hexc("C7CBD0"))
    ctx.fill()
    # bottom rim
    rrect(ctx, -w * 0.46, bot - 2, w * 0.92, h * 0.045, h * 0.02)
    ctx.set_source(sh)
    ctx.fill()
    # moving shine
    if shine > 0:
        sx = lerp(-w * 1.2, w * 1.2, shine)
        lg = cairo.LinearGradient(sx - w * 0.3, -h / 2, sx + w * 0.3, h / 2)
        lg.add_color_stop_rgba(0, 1, 1, 1, 0)
        lg.add_color_stop_rgba(0.5, 1, 1, 1, 0.55)
        lg.add_color_stop_rgba(1, 1, 1, 1, 0)
        rrect(ctx, -w / 2, -h / 2, w, h, w * 0.12)
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.set_source(lg)
        ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def can_shadow(ctx, cx, cy, h, alpha=0.35):
    ctx.save()
    ctx.translate(cx, cy + h * 0.5)
    ctx.scale(1, 0.18)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, h * 0.42)
    g.add_color_stop_rgba(0, 0, 0, 0, alpha)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.arc(0, 0, h * 0.42, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()


# ----------------------------------------------------------------- backgrounds
@lru_cache(maxsize=1)
def grain_frames():
    rng = np.random.default_rng(7)
    out = []
    for _ in range(6):
        n = rng.integers(0, 255, (TOPH // 2, W // 2), dtype=np.uint8)
        img = Image.fromarray(n, "L").resize((W, TOPH), Image.BILINEAR)
        rgba = Image.merge("RGBA", (img, img, img, Image.new("L", img.size, 255)))
        out.append(Sprite(pil_to_surface(rgba), W, TOPH))
    return out


def grain(ctx, frame, amount=0.045):
    sp = grain_frames()[frame % 6]
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source_surface(sp.surf, 0, 0)
    ctx.paint_with_alpha(amount * 2.2)
    ctx.restore()


def bg_radial(ctx, t, inner, outer, cx=W / 2, cy=TOPH * 0.45, drift=1.0):
    ctx.set_source_rgba(*outer)
    ctx.paint()
    x = cx + math.sin(t * 0.7) * 60 * drift
    y = cy + math.cos(t * 0.5) * 40 * drift
    g = cairo.RadialGradient(x, y, 0, x, y, 820)
    g.add_color_stop_rgba(0, *inner)
    g.add_color_stop_rgba(1, *outer)
    ctx.set_source(g)
    ctx.paint()


def bg_pattern_dots(ctx, t, c, spacing=54, r=3.2, speed=18):
    off = (t * speed) % spacing
    ctx.set_source_rgba(*c)
    for j in range(-1, TOPH // spacing + 2):
        for i in range(-1, W // spacing + 2):
            x = i * spacing + (j % 2) * spacing / 2 - off
            y = j * spacing + off * 0.5
            ctx.new_sub_path()
            ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def bg_stripes(ctx, t, c, width=70, speed=40):
    off = (t * speed) % (width * 2)
    ctx.save()
    ctx.set_source_rgba(*c)
    for i in range(-4, 30):
        x = i * width * 2 + off
        ctx.move_to(x, 0)
        ctx.line_to(x + width, 0)
        ctx.line_to(x + width - TOPH * 0.6, TOPH)
        ctx.line_to(x - TOPH * 0.6, TOPH)
        ctx.close_path()
    ctx.fill()
    ctx.restore()


def vignette(ctx, strength=0.55):
    g = cairo.RadialGradient(W / 2, TOPH / 2, TOPH * 0.35, W / 2, TOPH / 2, TOPH * 0.95)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, strength)
    ctx.set_source(g)
    ctx.paint()


# ----------------------------------------------------------------- particles
class Burst:
    """Deterministic confetti / spark burst."""

    def __init__(self, t0, cx, cy, n=60, seed=1, speed=(500, 1300), gravity=1500, life=1.6,
                 colors=(RED, WHITE, GOLD), kind="confetti", spread=(0, 2 * math.pi)):
        r = random.Random(seed)
        self.t0, self.life, self.g, self.kind = t0, life, gravity, kind
        self.p = []
        for _ in range(n):
            a = r.uniform(*spread)
            v = r.uniform(*speed)
            self.p.append(dict(x=cx, y=cy, vx=math.cos(a) * v, vy=math.sin(a) * v - 250,
                               rot=r.uniform(0, 6.3), vr=r.uniform(-12, 12), s=r.uniform(8, 18),
                               c=r.choice(colors), life=life * r.uniform(0.6, 1.0), drag=r.uniform(1.4, 2.4)))

    def draw(self, ctx, t):
        dt = t - self.t0
        if dt < 0 or dt > self.life:
            return
        for p in self.p:
            if dt > p["life"]:
                continue
            k = p["drag"]
            ex = (1 - math.exp(-k * dt)) / k
            x = p["x"] + p["vx"] * ex
            y = p["y"] + p["vy"] * ex + 0.5 * self.g * dt * dt * 0.35
            a = 1 - (dt / p["life"]) ** 2
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(p["rot"] + p["vr"] * dt)
            ctx.set_source_rgba(*with_a(p["c"], a))
            if self.kind == "confetti":
                ctx.scale(1, abs(math.cos(p["vr"] * dt * 0.7)) + 0.15)
                ctx.rectangle(-p["s"] / 2, -p["s"] / 4, p["s"], p["s"] / 2)
                ctx.fill()
            elif self.kind == "spark":
                ctx.arc(0, 0, p["s"] * 0.35 * (1 - dt / p["life"]) + 1, 0, 2 * math.pi)
                ctx.fill()
            else:  # star
                star_path(ctx, 0, 0, p["s"] * 0.8, p["s"] * 0.32, 4)
                ctx.fill()
            ctx.restore()


def bubbles(ctx, t, seed, n, area, c=WHITE, speed=160, rmax=14):
    x0, y0, x1, y1 = area
    r = random.Random(seed)
    for _ in range(n):
        bx = r.uniform(x0, x1)
        ph = r.uniform(0, 10)
        sp = speed * r.uniform(0.6, 1.4)
        rad = r.uniform(3, rmax)
        span = y1 - y0
        y = y1 - ((t * sp + ph * 100) % span)
        x = bx + math.sin(t * 3 + ph) * 10
        a = clamp((y - y0) / 120) * 0.7
        ring(ctx, x, y, rad, 2.2, with_a(c, a))


def sparkle(ctx, x, y, s, a, c=WHITE):
    if a <= 0:
        return
    star_path(ctx, x, y, s, s * 0.18, 4)
    ctx.set_source_rgba(*with_a(c, a))
    ctx.fill()
