"""Cut + grade + upscale source per EDL -> render/base.mp4 (silent) and render/voice.wav."""
import json, subprocess
E=json.load(open("pipeline/edl.json")); fps=E["fps"]; SRC="source/raw.mov"
GRADE=("hqdn3d=1.5:1.5:4:4,"
       "curves=master='0/0 0.25/0.22 0.75/0.76 1/0.96',"          # gentle S, tame clipped whites
       "eq=contrast=1.05:saturation=1.06:gamma=0.98,"
       "colorbalance=rs=-0.02:bs=0.03:rh=-0.02:bh=0.02,"            # neutralise warm fluorescent cast
       "scale=1080:1920:flags=lanczos,unsharp=5:5:0.45:5:5:0.0,"
       "vignette=angle=PI/5:mode=forward,format=yuv420p")
vparts=[];aparts=[];f=[];t=0;out=[]
for i,s in enumerate(E["segments"]):
    n=round((s["src_out"]-s["src_in"])*fps); d=n/fps
    f+=["-ss",str(s["src_in"]),"-t",f"{d:.4f}","-i",SRC]
    vparts.append(f"[{i}:v]fps={fps},trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
    aparts.append(f"[{i}:a]atrim=0:{d:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.02:.4f}:d=0.02[a{i}]")
    out.append(dict(id=s["id"],src_in=s["src_in"],src_out=s["src_in"]+d,out_in=round(t,4),out_out=round(t+d,4),frames=n,note=s["note"])); t+=d
k=len(E["segments"])
# end card: hold last frame (graphics cover it)
fc=";".join(vparts+aparts)+";"+"".join(f"[v{i}]" for i in range(k))+f"concat=n={k}:v=1:a=0[vc];[vc]tpad=stop_mode=clone:stop_duration={E['endcard_seconds']},{GRADE}[v];"
fc+="".join(f"[a{i}]" for i in range(k))+f"concat=n={k}:v=0:a=1,apad=pad_dur={E['endcard_seconds']},"
fc+="highpass=f=85,afftdn=nf=-30:nr=10,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.5:g=3,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3[a]"
subprocess.run(["ffmpeg","-v","error","-y",*f,"-filter_complex",fc,"-map","[v]","-c:v","libx264","-crf","12","-preset","slow","-an","render/base.mp4",
                "-map","[a]","-ar","48000","-ac","1","render/voice.wav"],check=True)
total=t+E["endcard_seconds"]
json.dump(dict(fps=fps,total=round(total,4),total_frames=round(total*fps),segments=out),open("pipeline/edl_resolved.json","w"),indent=1,ensure_ascii=False)
for o in out: print(o["id"],o["src_in"],"->",round(o["src_out"],3),"| out",o["out_in"],"->",o["out_out"])
print("total",total)
