"""Per-frame can-wall skyline (for occlusion) + hero-can track in output coordinates -> motion/src/data/*.json"""
import cv2, numpy as np, json, os
os.makedirs("motion/src/data",exist_ok=True)
R=json.load(open("pipeline/edl_resolved.json")); fps=R["fps"]
cap=cv2.VideoCapture("render/base.mp4"); COLS=54; sky=[]
while True:
    ok,f=cap.read()
    if not ok: break
    hsv=cv2.cvtColor(f[700:],cv2.COLOR_BGR2HSV)
    m=(cv2.inRange(hsv,(0,90,60),(10,255,255))|cv2.inRange(hsv,(168,90,60),(180,255,255)))>0
    rows=m.reshape(m.shape[0],COLS,-1).mean(2)              # (H, COLS) red ratio per column bin
    rows=cv2.blur(rows.astype(np.float32),(1,25))           # vertical smoothing
    top=[]
    for c in range(COLS):
        r=(rows[:,c]>0.3).astype(np.float32)
        run=np.convolve(r,np.ones(220),'full')[219:][:len(r)]   # red rows in the next 220px
        idx=np.where((r>0)&(run>0.7*220))[0]                    # wall = tall continuous red run
        top.append(700+idx[0] if len(idx) else 1920)
    sky.append(top)
sky=np.array(sky,np.float32)
from scipy.ndimage import median_filter, uniform_filter1d
sky=median_filter(sky,size=(7,3)); sky=uniform_filter1d(sky,5,axis=1)
json.dump(dict(cols=COLS,sky=np.round(sky).astype(int).tolist()),open("motion/src/data/skyline.json","w"))
# hero can track -> output frames
seg=[s for s in R["segments"] if s["id"]=="HERO"][0]; tr=json.load(open("analysis/can_track.json")); S=1080/720
can={}
for r in tr:
    of=round((r["t"]-seg["src_in"]+seg["out_in"])*fps)
    can[of]=dict(x=r["x"]*S,y=r["y"]*S,w=r["w"]*S,h=r["h"]*S,a=r["a"])
json.dump(can,open("motion/src/data/can_track.json","w"))
json.dump(R,open("motion/src/data/edl.json","w"),ensure_ascii=False)
print(len(sky),"frames; can frames",min(map(int,can)),"-",max(map(int,can)))
