import React from "react";
import { Composition } from "remotion";
import { Commercial } from "./Commercial";
import cues from "./data/cues.json";

export const Root: React.FC = () => (
  <Composition id="Commercial" component={Commercial} durationInFrames={cues.total} fps={30} width={1080} height={1920} />
);
