import React from "react";
import { C, F, ease, prog, env, lerp } from "../theme";

type Part = string | { em: string };

/**
 * Restrained caption: one plate, phrase-level entrance. Emphasis words get a red
 * marker drawn right→left (RTL reading direction) slightly after the plate lands.
 */
export const Caption: React.FC<{ f: number; range: number[]; parts: Part[]; y?: number; subtle?: boolean }> = ({ f, range, parts, y = 1440, subtle }) => {
  const [a, b] = range;
  const o = env(f, a, b, 9, 7);
  if (o <= 0) return null;
  const inP = prog(f, a, 14, ease.out);
  const mark = prog(f, a + 7, 12, ease.inOut);
  return (
    <div style={{ position: "absolute", top: y, width: 1080, display: "flex", justifyContent: "center", opacity: o,
      transform: `translateY(${(1 - inP) * 26}px)` }}>
      <div dir="rtl" style={{ maxWidth: 940, textAlign: "center", background: subtle ? "rgba(18,16,20,.55)" : "rgba(18,16,20,.80)", borderRadius: 22,
        padding: "10px 34px 18px", transform: `scaleX(${lerp(0.94, 1, inP)})` }}>
        {parts.map((p, i) => typeof p === "string" ? (
          <span key={i} style={{ fontFamily: F.text, fontWeight: 700, fontSize: subtle ? 50 : 56, color: C.white, lineHeight: 1.4 }}>{p}</span>
        ) : (
          <span key={i} style={{ position: "relative", display: "inline-block", fontFamily: F.display, fontWeight: 900, fontSize: 66, color: C.white, lineHeight: 1.2, padding: "0 8px" }}>
            <span style={{ position: "absolute", right: 0, left: 0, bottom: 6, height: "42%", background: C.red, borderRadius: 8, zIndex: 0,
              transformOrigin: "right center", transform: `scaleX(${mark})` }} />
            <span style={{ position: "relative" }}>{p.em}</span>
          </span>
        ))}
      </div>
    </div>
  );
};
