"""Render single frames to PNG: python3 preview.py out_dir t1 t2 ..."""
import subprocess, sys
import cairo
import render as R

out = sys.argv[1]
for ts in sys.argv[2:]:
    t = float(ts)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", R.FOOTAGE, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "bgra", "-"], capture_output=True).stdout
    src = cairo.ImageSurface.create_for_data(bytearray(raw), cairo.FORMAT_ARGB32, R.W, R.H, R.W * 4)
    frame = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    ctx = cairo.Context(frame)
    R.draw_footage(ctx, t, src)
    ctx.save(); ctx.rectangle(0, 0, R.W, R.SEAM); ctx.clip()
    R.draw_top(ctx, t, int(t * 30)); ctx.restore()
    R.draw_seam(ctx, t); R.draw_captions(ctx, t)
    frame.write_to_png(f"{out}/p_{t:05.2f}.png")
