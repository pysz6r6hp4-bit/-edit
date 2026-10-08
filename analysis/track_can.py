# Tracks the hand-held Coca-Cola can (src 27.6–31.0s): red blob above the display, continuity-constrained.
import cv2, numpy as np, json
cap=cv2.VideoCapture("source/raw.mov"); fps=30
t0,t1=28.0,31.0; cap.set(cv2.CAP_PROP_POS_MSEC,t0*1000)
prev=np.array([270.,470.]); out=[]
for i in range(int((t1-t0)*fps)):
    ok,f=cap.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=cv2.inRange(hsv,(0,120,70),(9,255,255))|cv2.inRange(hsv,(170,120,70),(180,255,255))
    m[640:]=0; m[:250]=0  # exclude display + ceiling
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None;bs=-1e9
    for k in range(1,n):
        a=st[k,4]
        if a<1500: continue
        d=np.hypot(*(cen[k]-prev))
        if d>60: continue
        s=a-d*40
        if s>bs: bs,best=s,k
    if best is None: out.append(None); continue
    cnts,_=cv2.findContours((lab==best).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    (cx,cy),(w,h),ang=cv2.minAreaRect(max(cnts,key=cv2.contourArea))
    if w>h: w,h,ang=h,w,ang+90
    if ang>45: ang-=180
    if ang<-45: ang+=180
    prev=np.array([cx,cy]); out.append([round(t0+i/fps,4),cx,cy,w,h,ang,int(st[best,4])])
# smooth (centered moving average, 7 frames)
arr=np.array([o for o in out if o]); sm=arr.copy()
for c in range(1,6): sm[:,c]=np.convolve(np.pad(arr[:,c],3,mode='edge'),np.ones(7)/7,'valid')
json.dump([dict(t=r[0],x=r[1],y=r[2],w=r[3],h=r[4],a=r[5]) for r in sm],open("analysis/can_track.json","w"),indent=0)
print(len(sm)); print(sm[::10].round(1))
