# فروج الحلو — Coca-Cola offer reel (1080×1920, 36 s)

**Final:** `deliverables/frouj_alhelou_coca_cola_reel_1080x1920.mp4` (H.264 High, 30 fps, AAC 256k, −14 LUFS, faststart, made for Instagram Reels)

Verified offer on screen: **6 cans of Coca-Cola 300 ml for 10 shekels**, at فروج الحلو, شارع النصر.

## Deliverables
| Path | What |
|---|---|
| `deliverables/*.mp4` | Final commercial |
| `deliverables/transcript_ar.md`, `transcript.json` | Arabic transcript with timestamps and confidence |
| `deliverables/EDL.md` | Source→output timecodes + every graphic/sound cue |
| `deliverables/preview_frames/` | Frames from the key design moments |
| `deliverables/graphics/` | SVG assets (can counter, map pin, focus brackets, offer badge) |
| `sound/stems/`, `sound/music_bed.wav`, `sound/sfx_bus.wav`, `sound/cue_sheet.json` | Separate sound-design elements (all original, procedurally synthesised) |
| `motion/` | Remotion (React/TS) motion project — editable |
| `pipeline/` | Reproducible build scripts + `cues.json` (single timing source for picture & sound) |

## Rebuild
```sh
pip install opencv-python-headless numpy scipy sherpa-onnx
python3 pipeline/build_base.py          # cut + grade + 1080p plate, cleaned voice
python3 analysis/track_can.py           # hero can tracking (source coords)
python3 pipeline/analyze_plate.py       # can-wall occlusion edge + track → motion/src/data
cp render/base.mp4 motion/public/base.mp4
python3 pipeline/sound_design.py        # SFX + music + mix → render/mix.wav
cd motion && npm i && npx remotion render src/index.ts Commercial ../render/picture.mp4 --codec=h264 --crf=14 \
   --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
cd .. && ffmpeg -i render/picture.mp4 -i render/mix.wav -map 0:v -map 1:a -c:v libx264 -crf 17 -preset slow \
   -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart -shortest deliverables/frouj_alhelou_coca_cola_reel_1080x1920.mp4
```
To retime any graphic or sound, edit `pipeline/cues.json` and copy it to `motion/src/data/`.

## Notes and limitations
- **Logo:** no official logo or brand guide was supplied. "فروج الحلو" is set as a *proposed typographic wordmark* (Tajawal Black) in `motion/src/components/Wordmark.tsx`. Replace it with the official file when you have one. The red / white / ink palette is also a proposal.
- **Source:** the actual file is 720×1280 at 30 fps (not 464×832 at 60 fps). It is upscaled to 1080×1920 with Lanczos, light denoise and sharpening. Upscaling adds no real detail.
- **Occlusion:** the "10" and the offer panel rise from *behind* the real cans. The can-wall edge is detected for every frame from the footage (`analyze_plate.py`). The held can is colour-tracked, the track is smoothed, and the graphics follow its position and angle.
- **Music:** original, synthesised in `sound_design.py`. No third-party audio is used.
- The landmark after "مقابل برج…" in the address was not intelligible enough to verify, so it is left off the graphics.
