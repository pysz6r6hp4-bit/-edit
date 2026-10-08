import React from "react";
import { F } from "../theme";

/** PROPOSED typographic wordmark for فروج الحلو — a placeholder until the official logo file is supplied. */
export const Wordmark: React.FC<{ size: number; color: string }> = ({ size, color }) => (
  <div dir="rtl" style={{ fontFamily: F.display, fontWeight: 900, fontSize: size, color, lineHeight: 1.15, whiteSpace: "nowrap" }}>
    فروج الحلو
  </div>
);
