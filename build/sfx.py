"""Synthesised SFX bed, every hit placed on an animation beat. Writes sfx.wav (48 kHz stereo)."""
import math
import wave

import numpy as np

from scenes import SCHEDULE, T, COUNTS

SR = 48000
DUR = 40.6
rng = np.random.default_rng(3)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def svf(x, f0, f1, q=0.7, mode="bp"):
    """State-variable filter with an exponential cutoff sweep f0 -> f1."""
    n = len(x)
    f = f0 * (f1 / f0) ** (np.arange(n) / max(1, n - 1))
    g = 2 * np.sin(np.pi * np.minimum(f, SR / 6) / SR)
    lp = bp = 0.0
    out = np.empty(n)
    damp = 1 / q
    for i in range(n):
        hp = x[i] - lp - damp * bp
        bp += g[i] * hp
        lp += g[i] * bp
        out[i] = bp if mode == "bp" else lp if mode == "lp" else hp
    return out


def whoosh(d=0.45, f0=300, f1=3200, q=1.2, shape=0.35):
    n = int(d * SR)
    x = rng.standard_normal(n)
    y = svf(x, f0, f1, q)
    t = np.linspace(0, 1, n)
    e = np.where(t < shape, (t / shape) ** 2, ((1 - t) / (1 - shape)) ** 1.6)
    return y * e


def pop(f0=900, f1=260, d=0.09, click=0.25):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 45)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * env_exp(n, d / 4)
    y[:120] += rng.standard_normal(120) * click * np.linspace(1, 0, 120)
    return y


def click(f=2600, d=0.03):
    n = int(d * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * env_exp(n, 0.004)
    y[:60] += rng.standard_normal(60) * 0.5
    return y


def bell(f=1320, d=1.4, partials=((1, 1), (2.76, 0.45), (5.4, 0.25), (8.9, 0.1))):
    n = int(d * SR)
    t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.5 + k * 1.2)) for k, a in partials)
    return y * np.minimum(1, t / 0.002)


def thud(f0=140, f1=48, d=0.35, noise=0.4):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 30)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.09)
    nz = svf(rng.standard_normal(n), 2500, 500, 0.8, "lp") * env_exp(n, 0.025) * noise
    return y + nz


def sparkle(d=0.7, n_pings=7, base=3200):
    out = np.zeros(int(d * SR))
    r = np.random.default_rng(int(base))
    for k in range(n_pings):
        st = int(r.uniform(0, d * 0.6) * SR)
        p = bell(base * r.uniform(0.8, 1.9), 0.35, ((1, 1), (2.0, 0.2))) * r.uniform(0.3, 0.7)
        out[st:st + len(p)] += p[:len(out) - st]
    return out


def fizz(d):
    n = int(d * SR)
    y = np.zeros(n)
    idx = rng.integers(0, n - 200, int(d * 260))
    for i in idx:
        y[i:i + 40] += rng.standard_normal(40) * np.linspace(1, 0, 40) * rng.uniform(0.1, 0.6)
    y = svf(y, 4000, 4000, 0.6, "hp")
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.3 * SR))
    return y * fade


def ticks(t0, t1, start_rate=8, end_rate=30):
    """Slot-machine rattle accelerating towards the reveal."""
    out = []
    t = t0
    while t < t1:
        frac = (t - t0) / (t1 - t0)
        out.append(t)
        t += 1 / (start_rate + (end_rate - start_rate) * frac)
    return out


bus = np.zeros((int(DUR * SR) + SR, 2))


def put(t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    lg, rg = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    n = min(len(sig), len(bus) - i)
    bus[i:i + n, 0] += sig[:n] * lg * 1.414
    bus[i:i + n, 1] += sig[:n] * rg * 1.414


# ---------------------------------------------------------- transitions
for start, _, fn, kind in SCHEDULE[1:]:
    t0 = start - (0.02 if kind == "cut" else 0.16)
    if kind == "swipe":
        put(t0 - 0.05, whoosh(0.5, 400, 4200, 1.4, 0.45), 0.55, 0.3)
    elif kind == "zoom":
        put(t0 - 0.1, whoosh(0.55, 2500, 300, 1.0, 0.6), 0.5)
    elif kind == "circle":
        put(t0 - 0.05, whoosh(0.5, 250, 2600, 1.6, 0.5), 0.5, -0.2)
    elif kind == "liquid":
        put(t0 - 0.05, whoosh(0.6, 200, 1400, 2.5, 0.5), 0.5)
        put(t0 + 0.1, fizz(0.6), 0.25)

# ---------------------------------------------------------- scene beats
P = 0.42   # standard pop level
put(0.08, pop(1100, 500, 0.07), P * 0.8)
put(T["hani"], pop(800, 300), P)
put(T["endak"] - 0.15, pop(500, 180, 0.15), P * 1.1, -0.4)
put(T["hani2"], click(1800), 0.3)
put(T["othman"] + 0.05, sparkle(1.2, 9, 2600), 0.28)
put(T["salli"], whoosh(0.6, 1200, 5000, 3, 0.5), 0.18)
put(T["youm"] + 0.12, thud(160, 70, 0.25, 0.2), 0.45)
put(T["khamis"], click(2200), 0.35)
put(T["ahsan"] - 0.1, whoosh(0.35, 500, 2500), 0.3)
put(T["orood"], pop(950, 320), P, -0.3)
put(T["lahme"] - 0.25, whoosh(0.45, 300, 2200, 1.2, 0.6), 0.4, 0.5)
put(T["moallem"], sparkle(0.7), 0.3)
put(T["kaman"], pop(1200, 600, 0.07), P * 0.9)
put(T["kaman"] + 0.15, whoosh(0.6, 180, 1500, 1.5, 0.6), 0.42)
put(T["kaman"] + 0.2, fizz(2.0), 0.16)
put(T["orood2"], pop(800, 300, 0.07), P * 0.7, -0.4)
put(T["cola"], pop(700, 220, 0.12), P * 1.1, 0.3)
put(T["cola"] + 0.05, whoosh(0.5, 1500, 6000, 2, 0.3), 0.25)
put(T["baba"], sparkle(0.6, 5, 3600), 0.25)

notes = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]   # rising pentatonic per count
for k, c in enumerate(COUNTS):
    put(c - 0.2, whoosh(0.22, 2500, 600, 1.0, 0.7), 0.18, [0.4, 0, -0.4][k % 3])
    put(c, pop(notes[k] * 1.6, notes[k], 0.12, 0.35), P * 1.05, [0.4, 0, -0.4][k % 3])
    put(c + 0.01, bell(notes[k] * 2, 0.4, ((1, 1), (2.76, 0.3))), 0.14)
put(T["lissa"], pop(330, 140, 0.18), P, -0.5)
put(T["lissa"] + 0.08, pop(380, 160, 0.14), P * 0.6, -0.5)
put(T["khallast"] - 0.2, click(1500), 0.25)
put(T["c6"] + 0.05, bell(1568, 1.2), 0.32)
put(T["c6"] + 0.05, sparkle(1.0, 9, 3000), 0.3)
put(T["baba2"], sparkle(0.6, 5, 4000), 0.22)

for k in range(6):
    put(T["sit"] + k * 0.05, pop(1300, 700, 0.05, 0.1), 0.2)
put(T["sit"] + 0.2, pop(900, 300), P * 0.8, -0.4)
put(T["bikam"] - 0.3, whoosh(0.7, 2200, 300, 1.2, 0.3), 0.4, 0.4)
put(T["bikam"] + 0.1, click(1200, 0.04), 0.25, 0.4)
put(T["b15"] - 0.1, whoosh(0.3, 600, 3500, 1.5, 0.5), 0.3, 0.4)
put(T["b15"] + 0.1, click(2400), 0.35, 0.4)

put(T["mish"], thud(170, 45, 0.5, 0.6), 0.75)
put(T["mish"] + 0.05, whoosh(0.18, 4000, 1200, 1.0, 0.2), 0.35, 0.4)
put(T["mish"] + 0.18, whoosh(0.18, 4000, 1200, 1.0, 0.2), 0.35, 0.4)
put(T["mish"] + 0.18, thud(130, 50, 0.35, 0.5), 0.45)
put(T["k15"] + 0.25, whoosh(0.25, 1500, 5000, 1.2, 0.3), 0.3, -0.4)

for k in range(6):
    put(T["hadool3"] + k * 0.06, pop(1000 + k * 120, 500, 0.06, 0.1), 0.24, 0.5 - k * 0.2)
for tk in ticks(T["sitte"] + 0.1, T["ashra"] - 0.03):
    put(tk, click(3200, 0.015), 0.16)
put(T["ashra"] - 0.6, whoosh(0.62, 300, 6000, 2.5, 0.95), 0.3)
put(T["ashra"], thud(110, 50, 0.4, 0.3), 0.5)
put(T["ashra"], bell(1760, 1.6), 0.38)
put(T["ashra"] + 0.03, bell(2637, 1.2), 0.2)
put(T["ashra"] + 0.05, sparkle(1.4, 12, 3000), 0.32)
put(T["shekel"], pop(900, 350), P)
put(T["hajj"], sparkle(0.6, 5, 3800), 0.22)

for k in range(6):
    put(T["taqm"] + k * 0.07, pop(900 + k * 90, 450, 0.06, 0.1), 0.22)
put(T["taqm"] + 0.45, whoosh(0.3, 800, 3000, 1, 0.3), 0.2)
put(T["taqm"] + 0.1, pop(1100, 500, 0.07), P * 0.7, -0.5)
put(T["ashra2"] - 0.05, whoosh(0.2, 3000, 800, 1, 0.5), 0.25, 0.5)
put(T["ashra2"] + 0.1, thud(220, 90, 0.2, 0.7), 0.45, 0.5)
put(T["coke"] - 0.05, whoosh(0.5, 700, 4500, 1.4, 0.5), 0.33)
put(T["coke"] + 0.25, click(2000), 0.2)
put(T["ml300"], pop(1000, 400), P, 0.5)
put(T["ml300"] + 0.6, sparkle(1.2, 7, 4200), 0.2)

put(T["haje"] - 0.05, whoosh(0.25, 3000, 500, 1, 0.8), 0.3)
put(T["haje"] + 0.22, thud(150, 55, 0.45, 0.8), 0.7)
put(T["alf"], pop(700, 250, 0.12), P * 1.1)
put(T["alf"], sparkle(1.0, 9, 3300), 0.3)
put(T["baba3"], pop(1200, 600, 0.06), 0.3)

put(T["ind"] - 0.1, whoosh(0.4, 2000, 300, 1, 0.5), 0.35)
put(T["ind"] + 0.25, thud(180, 80, 0.2, 0.3), 0.3)
put(T["farouj"] - 0.05, whoosh(0.55, 600, 4000, 1.3, 0.5), 0.32)
put(T["helou"], sparkle(0.9, 8, 3500), 0.3)

put(T["onwan"], pop(1100, 500, 0.07), P * 0.8)
put(T["maroof"] - 0.1, whoosh(0.3, 2600, 500, 1.2, 0.85), 0.35, 0.4)
put(T["maroof"] + 0.2, pop(600, 200, 0.12), P, 0.4)
put(T["share"] - 0.1, whoosh(0.6, 300, 2200, 1.0, 0.5), 0.3, 0.6)
put(T["nasr"], pop(900, 350), P * 0.8, -0.4)
put(T["mqabel"], click(1800), 0.3, 0.6)
put(T["burj"] - 0.1, whoosh(0.5, 200, 1800, 1.5, 0.7), 0.35, 0.2)
put(T["shifa"], pop(850, 320), P * 0.8, -0.4)

put(T["ahlan"], pop(800, 300, 0.1), P)
put(T["ahlan"] + 0.02, sparkle(1.2, 10, 3000), 0.3)
put(T["sahlan"], pop(900, 340, 0.08), P * 0.8)
put(T["bikom"], pop(1050, 400, 0.08), P * 0.8)
put(T["tsharfuna"] - 0.05, pop(1150, 500, 0.07), P * 0.7)

put(T["hot"] + 0.05, pop(800, 300), P * 0.8)
put(T["hot"] + 0.3, pop(1000, 400), P * 0.7)
put(T["hot"] + 0.55, whoosh(0.4, 600, 2400), 0.2)
put(T["hot"] + 0.6, sparkle(1.4, 8, 3800), 0.2)
put(40.0, whoosh(0.6, 2500, 200, 1, 0.3), 0.3)

# gentle bus limiting
peak = np.max(np.abs(bus))
y = np.tanh(bus / max(peak, 1e-9) * 1.4) * 0.9
pcm = (y[: int(DUR * SR)] * 32767).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("sfx.wav written", len(pcm) / SR, "s")
