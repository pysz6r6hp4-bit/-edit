import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, interpolate } from "remotion";
import cues from "./data/cues.json";
import skyline from "./data/skyline.json";
import canTrack from "./data/can_track.json";
import { C, F, ease, prog, env, lerp } from "./theme";
import { Fonts } from "./Fonts";
import { Caption } from "./components/Caption";
import { CountMeter } from "./components/CountMeter";
import { Wordmark } from "./components/Wordmark";

const W = 1080, H = 1920;
const plate = staticFile("base.mp4");

/* ---------------- Camera (virtual push-ins on the 1080p plate) ---------------- */
// [frame, scale, pivotX, pivotY]. Jumps sit on edit points so they read as punch-in cuts.
const CAM: [number, number, number, number][] = [
  [0, 1.12, 540, 760], [79, 1.05, 540, 760],
  [80, 1, 540, 960], [240, 1, 540, 960], [262, 1.06, 540, 1150], [440, 1.06, 540, 1150], [452, 1, 540, 960],
  [509, 1, 540, 960], [510, 1.1, 540, 560], [604, 1.1, 540, 560], [616, 1, 540, 960],
  [693, 1, 540, 960], [694, 1, 540, 960], [712, 1, 540, 960], [736, 1.15, 420, 860], [804, 1.15, 420, 860], [832, 1, 540, 960],
  [1026, 1.05, 540, 820], [1080, 1.07, 540, 820],
];
const camAt = (f: number) => {
  let i = CAM.findIndex((k) => k[0] > f);
  if (i === -1) return CAM[CAM.length - 1].slice(1) as number[];
  if (i === 0) return CAM[0].slice(1) as number[];
  const a = CAM[i - 1], b = CAM[i];
  const t = ease.inOut((f - a[0]) / (b[0] - a[0]));
  return [lerp(a[1], b[1], t), lerp(a[2], b[2], t), lerp(a[3], b[3], t)];
};

/* ---------------- Occlusion: "behind the cans" graphics are clipped to the region ABOVE the can wall ---------------- */
// The wall edge (per-frame skyline, see pipeline/analyze_plate.py) is tracked from the plate, so hands resting on
// the cans and the irregular can tops correctly cover the graphic.
const abovePolygon = (f: number) => {
  const row: number[] = skyline.sky[Math.min(f, skyline.sky.length - 1)];
  const step = W / skyline.cols;
  const pts = row.map((y, c) => `${(c + 0.5) * step}px ${y + 2}px`).reverse();
  return `polygon(0px 0px, ${W}px 0px, ${W}px ${row[row.length - 1] + 2}px, ${pts.join(", ")}, 0px ${row[0] + 2}px)`;
};
const BehindCans: React.FC<{ f: number; children: React.ReactNode }> = ({ f, children }) => (
  <AbsoluteFill style={{ clipPath: abovePolygon(f) }}>{children}</AbsoluteFill>
);

/* ---------------- Scenes ---------------- */

// HOOK: a giant "10" surfaces from behind the can wall on "بعشرة شيكل"
const HookTen: React.FC<{ f: number }> = ({ f }) => {
  const up = prog(f, cues.hookTen, 16, ease.back);
  const down = prog(f, cues.hookOut - 4, 8, ease.in);
  const y = lerp(560, 0, up) + down * 560;
  return (
    <div style={{ position: "absolute", left: 0, width: W, top: 760, height: 560, display: "flex", justifyContent: "center", alignItems: "flex-end", transform: `translateY(${y}px)` }}>
      <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 560, lineHeight: 0.78, color: C.white, letterSpacing: -20,
        textShadow: "0 18px 50px rgba(0,0,0,.35)", WebkitTextStroke: `6px ${C.red}` }}>10</div>
    </div>
  );
};
const HookKicker: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.hookTen + 8, cues.hookOut, 10, 6);
  return (
    <div style={{ position: "absolute", top: 1338, width: W, textAlign: "center", opacity: o, transform: `translateY(${(1 - o) * 30}px)` }}>
      <span dir="rtl" style={{ fontFamily: F.display, fontWeight: 800, fontSize: 70, color: C.white, background: C.red, padding: "6px 34px 12px", borderRadius: 18 }}>
        بعشرة شيكل
      </span>
    </div>
  );
};

// Diagonal red wipe that covers the HOOK→INTRO cut
const Wipe: React.FC<{ f: number; at: number }> = ({ f, at }) => {
  const t = interpolate(f, [at - 7, at + 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease.inOut });
  if (t <= 0 || t >= 1) return null;
  const x = lerp(1700, -1700, t);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: x - 300, top: -400, width: 1500, height: 2800, background: C.red, transform: "rotate(14deg)" }} />
      <div style={{ position: "absolute", left: x + 1230, top: -400, width: 40, height: 2800, background: C.white, transform: "rotate(14deg)" }} />
    </AbsoluteFill>
  );
};

// Small persistent brand chip (top) — brand recall without fighting the product
const BrandChip: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.brandChipIn, cues.brandIn, 14, 10);
  if (o <= 0) return null;
  const sx = prog(f, cues.brandChipIn, 18);
  return (
    <div style={{ position: "absolute", top: 96, width: W, display: "flex", justifyContent: "center", opacity: o }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, background: "rgba(18,16,20,.72)", borderRadius: 999, padding: "10px 30px 14px",
        clipPath: `inset(0 ${(1 - sx) * 50}% 0 ${(1 - sx) * 50}% round 999px)` }}>
        <div style={{ width: 14, height: 14, borderRadius: 7, background: C.red }} />
        <Wordmark size={44} color={C.white} />
      </div>
    </div>
  );
};

// "قولي 15؟" → "مش 15!" : number struck through with a drawn red stroke
const Fifteen: React.FC<{ f: number }> = ({ f }) => {
  const [a] = cues.fifteenCap; const [b, end] = cues.notFifteen;
  const o = env(f, a, end, 10, 8);
  if (o <= 0) return null;
  const strike = prog(f, b + 2, 10, ease.inOut);
  const shake = f >= b + 2 && f < b + 10 ? Math.sin((f - b) * 2.2) * (1 - (f - b - 2) / 8) * 6 : 0;
  return (
    <div style={{ position: "absolute", top: 1180, width: W, display: "flex", justifyContent: "center", opacity: o, transform: `translateX(${shake}px) scale(${lerp(0.9, 1, prog(f, a, 14, ease.back))})` }}>
      <div dir="rtl" style={{ position: "relative", fontFamily: F.display, fontWeight: 900, fontSize: 230, color: C.white, lineHeight: 1,
        textShadow: "0 10px 40px rgba(0,0,0,.45)", opacity: lerp(1, 0.6, strike) }}>
        <span>{f < b ? "15؟" : "15"}</span>
        <div style={{ position: "absolute", right: -30, top: "52%", height: 22, width: "calc(100% + 60px)", background: C.red, borderRadius: 11,
          transformOrigin: "right center", transform: `rotate(-8deg) scaleX(${strike})` }} />
      </div>
    </div>
  );
};

// OFFER: the main payoff. Red slab rises from behind the cans; "10 شيكل" lands on the vocal emphasis.
const OfferBehind: React.FC<{ f: number }> = ({ f }) => {
  const rise = prog(f, cues.offerIn, 18, ease.out);
  const sink = prog(f, cues.offerToBadge - 6, 8, ease.in);
  if (rise <= 0 || sink >= 1) return null;
  const num = prog(f, cues.offerImpact - 4, 12, ease.back);
  const word = prog(f, cues.offerShekel, 12, ease.out);
  const y = lerp(420, 0, rise) + sink * 460;
  return (
    <div style={{ position: "absolute", left: 120, top: 900, width: 840, height: 520, transform: `translateY(${y}px)` }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 34, background: `linear-gradient(160deg, ${C.red} 0%, ${C.redDeep} 100%)`, boxShadow: "0 30px 80px rgba(0,0,0,.4)" }} />
      <div style={{ position: "absolute", inset: 16, borderRadius: 24, border: "3px solid rgba(255,255,255,.35)" }} />
      <div dir="rtl" style={{ position: "absolute", top: 18, width: "100%", display: "flex", justifyContent: "center", alignItems: "center", gap: 26 }}>
        <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 300, lineHeight: 1, color: C.white, letterSpacing: -10, direction: "ltr",
          transform: `translateY(${(1 - num) * 120}px) scale(${lerp(1.25, 1, num)})`, opacity: num }}>10</div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", opacity: word, transform: `translateX(${(1 - word) * -40}px)` }}>
          <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 112, lineHeight: 1, color: C.white }}>شيكل</div>
          <div style={{ height: 10, width: lerp(0, 230, prog(f, cues.offerShekel + 6, 12)), background: C.white, borderRadius: 5, marginTop: 14 }} />
        </div>
      </div>
    </div>
  );
};
const CanPip: React.FC<{ on: number; size?: number; color?: string }> = ({ on, size = 1, color = C.red }) => (
  <svg width={26 * size} height={46 * size} viewBox="0 0 26 46">
    <rect x="2" y="2" width="22" height="42" rx="6" fill={color} opacity={0.15 + 0.85 * on} />
    <rect x="2" y="2" width="22" height="42" rx="6" fill="none" stroke={color} strokeWidth="3" />
    <line x1="5" y1="8" x2="21" y2="8" stroke="#fff" strokeOpacity={0.6 * on} strokeWidth="2" />
  </svg>
);
const OfferFront: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.offerIn + 8, cues.offerToBadge, 14, 6);
  if (o <= 0) return null;
  return (
    <div style={{ position: "absolute", top: 1326, width: W, display: "flex", justifyContent: "center", opacity: o, transform: `translateY(${(1 - o) * 40}px)` }}>
      <div dir="rtl" style={{ display: "flex", alignItems: "center", gap: 20, background: C.white, borderRadius: 22, padding: "14px 34px 18px", boxShadow: "0 16px 40px rgba(0,0,0,.35)" }}>
        <span style={{ fontFamily: F.display, fontWeight: 900, fontSize: 66, color: C.red }}>6 علب</span>
        <span style={{ fontFamily: F.display, fontWeight: 700, fontSize: 54, color: C.ink }}>كوكاكولا</span>
        <div style={{ display: "flex", gap: 6, marginRight: 8 }}>
          {[0, 1, 2, 3, 4, 5].map((i) => <CanPip key={i} size={0.9} on={prog(f, cues.offerIn + 14 + i * 3, 6)} />)}
        </div>
      </div>
    </div>
  );
};

// Persistent offer badge after the reveal
const OfferBadge: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.offerToBadge + 2, cues.brandIn + 4, 14, 10);
  if (o <= 0) return null;
  const s = lerp(0.4, 1, prog(f, cues.offerToBadge + 2, 16, ease.back));
  return (
    <div style={{ position: "absolute", top: 190, right: 46, width: 210, height: 210, borderRadius: 105, background: C.red, opacity: o,
      transform: `scale(${s}) rotate(${lerp(-25, -8, o)}deg)`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      boxShadow: "0 14px 36px rgba(0,0,0,.35)", border: `5px solid ${C.white}` }}>
      <div dir="rtl" style={{ fontFamily: F.display, fontWeight: 800, fontSize: 38, color: C.white, lineHeight: 1 }}>6 علب</div>
      <div dir="rtl" style={{ fontFamily: F.display, fontWeight: 900, fontSize: 74, color: C.white, lineHeight: 1.05 }}>بـ10 ₪</div>
    </div>
  );
};

/* ---------------- HERO: tracked can ---------------- */
type T = { x: number; y: number; w: number; h: number; a: number };
const track = canTrack as Record<string, T>;
const keys = Object.keys(track).map(Number).sort((a, b) => a - b);
const canAt = (f: number): T => track[String(Math.max(keys[0], Math.min(keys[keys.length - 1], f)))] ?? track[String(keys[0])];

const HeroSpot: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.heroStart + 6, cues.heroEnd, 14, 14);
  if (o <= 0) return null;
  const c = canAt(f);
  return <AbsoluteFill style={{ opacity: o, background: `radial-gradient(circle at ${c.x}px ${c.y}px, rgba(0,0,0,0) 150px, rgba(12,8,10,.55) 560px)` }} />;
};
const HeroFrame: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.heroStart + 10, cues.heroEnd, 12, 10);
  if (o <= 0) return null;
  const c = canAt(f);
  const k = lerp(1.35, 1, prog(f, cues.heroStart + 10, 16, ease.out));
  const bw = (c.w + 70) * k, bh = (Math.max(c.h, 170) + 70) * k, L = 34;
  const hw = bw / 2, hh = bh / 2;
  const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([sx, sy], i) => (
    <path key={i} d={`M ${sx * hw} ${sy * (hh - L)} L ${sx * hw} ${sy * hh} L ${sx * (hw - L)} ${sy * hh}`}
      stroke={C.white} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
  ));
  // highlight sweep, clipped to the can's oriented rectangle
  const sw = prog(f, cues.heroSweep, 16, ease.inOut);
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#fff" stopOpacity="0" /><stop offset=".5" stopColor="#fff" stopOpacity=".55" /><stop offset="1" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
          <clipPath id="canclip"><rect x={-c.w / 2} y={-c.h / 2} width={c.w} height={c.h} rx={14} /></clipPath>
        </defs>
        <g transform={`translate(${c.x} ${c.y}) rotate(${c.a})`}>
          {corners}
          {sw > 0 && sw < 1 && (
            <g clipPath="url(#canclip)" style={{ mixBlendMode: "screen" }}>
              <rect x={lerp(-c.w * 1.6, c.w * 0.6, sw)} y={-c.h} width={c.w} height={c.h * 2} fill="url(#sweep)" transform="rotate(-18)" />
            </g>
          )}
        </g>
      </svg>
    </AbsoluteFill>
  );
};
const HeroLabel: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.heroLabel, cues.heroEnd, 12, 10);
  if (o <= 0) return null;
  const c = canAt(f);
  const ax = c.x + 70, ay = c.y + 100;            // anchor: lower-right of can
  const lx = ax + 90, ly = ay + 110;              // label elbow
  const line = prog(f, cues.heroLabel, 10, ease.out);
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <circle cx={ax} cy={ay} r={9} fill={C.white} />
        <polyline points={`${ax},${ay} ${lerp(ax, lx, line)},${lerp(ay, ly, line)} ${lx + 40 * prog(f, cues.heroLabel + 8, 6)},${ly}`} stroke={C.white} strokeWidth={4} fill="none" />
      </svg>
      <div dir="rtl" style={{ position: "absolute", left: lx + 40, top: ly - 62, background: C.white, borderRadius: 18, padding: "10px 26px 14px",
        clipPath: `inset(0 ${(1 - prog(f, cues.heroLabel + 10, 14)) * 100}% 0 0 round 18px)`, boxShadow: "0 12px 30px rgba(0,0,0,.35)" }}>
        <div style={{ fontFamily: F.display, fontWeight: 700, fontSize: 44, color: C.ink, lineHeight: 1.1 }}>كوكاكولا</div>
        <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 70, color: C.red, lineHeight: 1 }}>300 مل</div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- Brand + address ---------------- */
const BrandLockup: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.brandIn, cues.endIn, 1, 8);
  if (o <= 0) return null;
  const bar = prog(f, cues.brandIn, 16, ease.out);
  const txt = prog(f, cues.brandIn + 6, 16, ease.out);
  const lift = prog(f, cues.addressIn - 4, 16, ease.inOut);
  return (
    <div style={{ position: "absolute", top: lerp(1250, 1150, lift), width: W, display: "flex", flexDirection: "column", alignItems: "center", opacity: o }}>
      <div dir="rtl" style={{ fontFamily: F.display, fontWeight: 700, fontSize: 48, color: C.white, opacity: txt, marginBottom: 6, textShadow: "0 4px 16px rgba(0,0,0,.6)" }}>عند</div>
      <div style={{ background: C.red, borderRadius: 26, padding: "8px 56px 22px", clipPath: `inset(0 0 0 ${(1 - bar) * 100}% round 26px)`, boxShadow: "0 18px 50px rgba(0,0,0,.4)" }}>
        <div style={{ transform: `translateY(${(1 - txt) * 50}px)`, opacity: txt }}><Wordmark size={138} color={C.white} /></div>
      </div>
    </div>
  );
};
const Address: React.FC<{ f: number }> = ({ f }) => {
  const o = env(f, cues.addressIn, cues.endIn, 1, 8);
  if (o <= 0) return null;
  const pin = prog(f, cues.addressIn + 4, 18, ease.inOut);
  const txt = prog(f, cues.addressIn + 12, 16, ease.out);
  const PIN = 190;
  return (
    <div dir="rtl" style={{ position: "absolute", top: 1418, width: W, display: "flex", justifyContent: "center", alignItems: "center", gap: 22, opacity: o }}>
      <svg width={70} height={90} viewBox="0 0 70 90">
        <path d="M35 86 C35 86 6 52 6 33 A29 29 0 1 1 64 33 C64 52 35 86 35 86 Z" fill="none" stroke={C.white} strokeWidth={6}
          strokeDasharray={PIN} strokeDashoffset={PIN * (1 - pin)} strokeLinejoin="round" />
        <circle cx={35} cy={33} r={10 * prog(f, cues.addressIn + 18, 8, ease.back)} fill={C.red} />
      </svg>
      <div style={{ background: "rgba(18,16,20,.78)", borderRadius: 20, padding: "8px 30px 14px", clipPath: `inset(0 0 0 ${(1 - txt) * 100}% round 20px)` }}>
        <div style={{ fontFamily: F.text, fontWeight: 600, fontSize: 34, color: C.cream, lineHeight: 1.3 }}>عنواننا معروف</div>
        <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 68, color: C.white, lineHeight: 1.05 }}>شارع النصر</div>
      </div>
    </div>
  );
};

/* ---------------- End card ---------------- */
const EndCard: React.FC<{ f: number }> = ({ f }) => {
  const s = cues.endIn;
  const bg = prog(f, s, 12, ease.inOut);
  if (bg <= 0) return null;
  const a = prog(f, s + 4, 16), b = prog(f, s + 12, 16, ease.back), c = prog(f, s + 20, 14), line = prog(f, s + 8, 18, ease.inOut);
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(122,10,22,${0.86 * bg}) 0%, rgba(18,16,20,${0.92 * bg}) 100%)` }}>
      <div dir="rtl" style={{ position: "absolute", top: 520, width: W, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ opacity: a, transform: `translateY(${(1 - a) * 40}px)` }}><Wordmark size={150} color={C.white} /></div>
        <div style={{ height: 6, width: 520 * line, background: C.red, borderRadius: 3, margin: "34px 0 46px" }} />
        <div style={{ fontFamily: F.display, fontWeight: 700, fontSize: 58, color: C.cream, opacity: c }}>6 علب كوكاكولا 300 مل</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 24, transform: `scale(${lerp(0.7, 1, b)})`, opacity: b, marginTop: 10 }}>
          <span style={{ fontFamily: F.display, fontWeight: 900, fontSize: 92, color: C.white }}>بـ</span>
          <span style={{ fontFamily: F.display, fontWeight: 900, fontSize: 250, color: C.white, lineHeight: 1, direction: "ltr" }}>10</span>
          <span style={{ fontFamily: F.display, fontWeight: 900, fontSize: 92, color: C.white }}>شيكل</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 46, opacity: c, background: C.red, borderRadius: 999, padding: "10px 36px 16px" }}>
          <span style={{ fontFamily: F.display, fontWeight: 800, fontSize: 50, color: C.white }}>شارع النصر</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- Composition ---------------- */
export const Commercial: React.FC = () => {
  const f = useCurrentFrame();
  const [s, px, py] = camAt(f);
  const endBlur = prog(f, cues.endIn, 14, ease.inOut);
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <Fonts />
      {/* camera space: plate + graphics that live "in" the scene */}
      <AbsoluteFill style={{ transform: `translate(${px}px, ${py}px) scale(${s}) translate(${-px}px, ${-py}px)`, filter: endBlur > 0 ? `blur(${endBlur * 14}px)` : undefined }}>
        <OffthreadVideo src={plate} muted />
        <BehindCans f={f}>
          {f < cues.hookOut + 6 && <HookTen f={f} />}
          <OfferBehind f={f} />
        </BehindCans>
        <HeroSpot f={f} />
        <HeroFrame f={f} />
        <HeroLabel f={f} />
      </AbsoluteFill>

      {/* screen space: typography & UI */}
      <HookKicker f={f} />
      <BrandChip f={f} />
      <Caption f={f} range={cues.introCap} parts={["هاني، شو عندك يا هاني؟"]} />
      <Caption f={f} range={cues.colaCap} parts={["كمان في عروض على ", { em: "الكولا" }]} />
      <CountMeter f={f} beats={cues.counts} end={cues.bikamCap[0] + 40} />
      <Caption f={f} range={cues.othmanCap} parts={["يا عثمان… لسّه ما خلصت!"]} subtle />
      <Caption f={f} range={cues.bikamCap} parts={["هدول ", { em: "بكم" }, " يا معلّم؟"]} />
      <Fifteen f={f} />
      <Caption f={f} range={cues.notFifteen} parts={[{ em: "مش 15" }, " يا عثمان!"]} />
      <OfferFront f={f} />
      <OfferBadge f={f} />
      <BrandLockup f={f} />
      <Address f={f} />
      <Caption f={f} range={[cues.welcomeIn, cues.endIn]} parts={["أهلاً وسهلاً… ", { em: "بتشرّفونا" }, " وبتنوّرونا"]} y={1600} />
      <EndCard f={f} />
      <Wipe f={f} at={cues.cut1} />
    </AbsoluteFill>
  );
};
