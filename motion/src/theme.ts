import { Easing, interpolate } from "remotion";

// Proposed design system (no official فروج الحلو brand guide was supplied).
export const C = {
  red: "#C8102E",       // deep commercial red, sits beside Coca-Cola red without competing
  redDeep: "#7A0A16",
  ink: "#121014",
  white: "#FFFFFF",
  cream: "#F6EFE6",
};
export const F = {
  display: "Tajawal", // 800/900 for headlines & numerals
  text: "Cairo",      // captions
};

export const ease = {
  out: Easing.bezier(0.16, 1, 0.3, 1),        // expo-out: confident arrivals
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  in: Easing.bezier(0.7, 0, 0.84, 0),
  back: Easing.bezier(0.34, 1.32, 0.64, 1),   // restrained overshoot, key moments only
};

/** frame -> 0..1 progress over [start, start+dur] with easing, clamped */
export const prog = (f: number, start: number, dur: number, e = ease.out) =>
  interpolate(f, [start, start + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: e });

/** in/out envelope: rises over `inDur` from a, falls over `outDur` ending at b */
export const env = (f: number, a: number, b: number, inDur = 10, outDur = 8) =>
  Math.min(prog(f, a, inDur), 1 - prog(f, b - outDur, outDur, ease.in));

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
