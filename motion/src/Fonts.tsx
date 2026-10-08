import React, { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

const css = `
@font-face{font-family:Tajawal;font-weight:500;src:url(${staticFile("fonts/Tajawal-Medium.ttf")})}
@font-face{font-family:Tajawal;font-weight:700;src:url(${staticFile("fonts/Tajawal-Bold.ttf")})}
@font-face{font-family:Tajawal;font-weight:800;src:url(${staticFile("fonts/Tajawal-ExtraBold.ttf")})}
@font-face{font-family:Tajawal;font-weight:900;src:url(${staticFile("fonts/Tajawal-Black.ttf")})}
@font-face{font-family:Cairo;font-weight:200 1000;src:url(${staticFile("fonts/Cairo.ttf")})}`;

/** Loads the Arabic faces and holds the frame until they are ready (no fallback-font frames). */
export const Fonts: React.FC = () => {
  const [handle] = useState(() => delayRender("fonts", { timeoutInMilliseconds: 120000 }));
  useEffect(() => {
    const specs = ["500 40px Tajawal", "700 40px Tajawal", "800 40px Tajawal", "900 40px Tajawal", "700 40px Cairo", "600 40px Cairo"];
    Promise.all(specs.map((s) => document.fonts.load(s, "فروج"))).then(() => continueRender(handle));
  }, [handle]);
  return <style>{css}</style>;
};
