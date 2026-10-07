import numpy as np, wave, json, sys
SR=44100
def w(name,x):
    x=np.clip(x,-1,1);d=(x*32767).astype('<i2')
    f=wave.open(name,'wb');f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(d.tobytes());f.close()
def t(d):return np.arange(int(SR*d))/SR
rng=np.random.default_rng(1)
def whoosh(d=0.5):
    x=t(d);n=rng.standard_normal(len(x));y=np.zeros_like(n);a0=0
    for i in range(len(n)):
        c=0.02+0.5*np.sin(np.pi*i/len(n))**2;a0+=c*(n[i]-a0);y[i]=a0
    env=np.sin(np.pi*x/d)**1.5;return y*env*2.2
def pop(d=0.12):
    x=t(d);f=900-5000*x;return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*30)*0.9
def ding(d=0.7):
    x=t(d);return (np.sin(2*np.pi*1318*x)+0.5*np.sin(2*np.pi*1975*x)+0.25*np.sin(2*np.pi*2637*x))*np.exp(-x*6)*0.5
def boing(d=0.45):
    x=t(d);f=300+250*np.sin(2*np.pi*9*x)*np.exp(-x*6);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*7)*0.8
def tick(d=0.05):
    x=t(d);return rng.standard_normal(len(x))*np.exp(-x*120)*0.5
S={'whoosh':whoosh(),'pop':pop(),'ding':ding(),'boing':boing(),'tick':tick()}
for k,v in S.items(): w(f'sfx_{k}.wav',v)
EV=[(0.15,'whoosh'),(0.15,'pop'),(0.33,'pop'),(0.51,'pop'),(0.9,'whoosh'),(1.2,'boing'),(1.7,'pop'),
    (11.5,'whoosh'),(11.55,'ding'),(15.5,'whoosh'),(15.55,'ding'),(20.5,'whoosh'),(20.55,'ding')]
try:
    for c in json.load(open('captions.json')):
        ws=c['t'].split();n=len(ws)
        for i in range(n):EV.append((c['s']+i/n*(c['e']-c['s']),'tick'))
        EV.append((c['s'],'whoosh'))
except Exception:pass
out=np.zeros(int(SR*37.6))
for tm,k in EV:
    i=int(tm*SR);s=S[k];out[i:i+len(s)]+=s[:len(out)-i]*(0.6 if k=='whoosh' else 1)
w('sfx_mix.wav',out*0.5)
