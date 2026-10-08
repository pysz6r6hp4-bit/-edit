import React from "react";
import { C, F, ease, prog, env, lerp } from "../theme";

/** Product-count indicator: six can slots fill as the presenter pulls each can forward. */
export const CountMeter: React.FC<{ f: number; beats: number[]; end: number }> = ({ f, beats, end }) => {
  const o = env(f, beats[0] - 14, end, 12, 10);
  if (o <= 0) return null;
  const n = beats.filter((b) => f >= b).length;
  const last = n ? beats[n - 1] : beats[0];
  const pop = n ? prog(f, last, 10, ease.back) : 0;
  const done = prog(f, beats[5] + 4, 14, ease.out);
  return (
    <div style={{ position: "absolute", top: 196, width: 1080, display: "flex", justifyContent: "center", opacity: o, transform: `translateY(${(1 - o) * -20}px)` }}>
      <div dir="rtl" style={{ display: "flex", alignItems: "center", gap: 26, background: "rgba(18,16,20,.72)", borderRadius: 28, padding: "14px 30px" }}>
        <div style={{ width: 96, height: 112, position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: F.display, fontWeight: 900, fontSize: 108, color: done > 0 ? C.white : C.white, lineHeight: 1,
            transform: `translateY(${(1 - pop) * 34}px) scale(${lerp(1, 1.12, done)})`, opacity: n ? 1 : 0.25 }}>{n || 0}</div>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          {beats.map((b, i) => {
            const on = prog(f, b, 8, ease.out);
            const flash = Math.max(0, 1 - (f - b) / 10) * (f >= b ? 1 : 0);
            return (
              <svg key={i} width={46} height={84} viewBox="0 0 46 84" style={{ transform: `translateY(${(1 - on) * 8 - flash * 6}px)` }}>
                <rect x="4" y="4" width="38" height="76" rx="11" fill={C.red} opacity={on} />
                <rect x="4" y="4" width="38" height="76" rx="11" fill="none" stroke={on > 0.5 ? C.red : "rgba(255,255,255,.55)"} strokeWidth="4" />
                <rect x="10" y="12" width="26" height="3" rx="1.5" fill="#fff" opacity={0.7 * on} />
                <rect x="4" y="4" width="38" height="76" rx="11" fill="#fff" opacity={flash * 0.6} />
              </svg>
            );
          })}
        </div>
        <div style={{ fontFamily: F.display, fontWeight: 800, fontSize: 44, color: C.white, opacity: done, width: lerp(0, 110, done), overflow: "hidden", whiteSpace: "nowrap" }}>علب</div>
      </div>
    </div>
  );
};
