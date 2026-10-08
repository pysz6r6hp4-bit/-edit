"""Original, procedurally synthesised sound design + music bed, cued from pipeline/cues.json.
Outputs: sound/stems/*.wav (individual SFX), sound/sfx_bus.wav, sound/music_bed.wav, render/mix.wav"""
import numpy as np, json, os, subprocess, wave
SR=48000; rng=np.random.default_rng(7); cues=json.load(open("pipeline/cues.json")); FPS=30
T=cues["total"]/FPS; N=int(T*SR); os.makedirs("sound/stems",exist_ok=True)
def write(p,x):
    x=np.clip(x,-1,1); w=wave.open(p,"wb"); w.setnchannels(2 if x.ndim==2 else 1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
def bp(x,lo,hi):  # FFT band-pass
    X=np.fft.rfft(x); fr=np.fft.rfftfreq(len(x),1/SR); X[(fr<lo)|(fr>hi)]=0; return np.fft.irfft(X,len(x))
def lp_sweep(x,f0,f1):  # time-varying one-pole lowpass
    y=np.zeros_like(x); s=0; fc=np.geomspace(f0,f1,len(x))
    a=np.exp(-2*np.pi*fc/SR)
    for i in range(len(x)): s=a[i]*s+(1-a[i])*x[i]; y[i]=s
    return y
def whoosh(d=0.45,up=True):
    n=int(d*SR); t=np.linspace(0,1,n); e=np.sin(np.pi*t**0.7)**2
    x=lp_sweep(rng.standard_normal(n),400 if up else 6000,6000 if up else 400)*e
    return x/np.abs(x).max()*0.5
def tick(f=2400,d=0.05):
    t=np.arange(int(d*SR))/SR; return 0.35*np.sin(2*np.pi*f*t)*np.exp(-t*90)
def can_clink():
    t=np.arange(int(0.18*SR))/SR
    x=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*k) for f,a,k in [(3150,.25,40),(4820,.15,55),(6900,.08,70)])
    return x+0.15*bp(rng.standard_normal(len(t)),2000,9000)*np.exp(-t*160)
def impact():
    t=np.arange(int(0.9*SR))/SR; f=55*np.exp(-t*2.2)+38
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*4.5)
    trans=bp(rng.standard_normal(len(t)),80,1800)*np.exp(-t*45)*0.6
    return 0.8*(body+trans)
def riser(d=0.75):
    n=int(d*SR); t=np.linspace(0,1,n)
    x=bp(rng.standard_normal(n),1500,9000)*t**2.5*0.35+0.15*np.sin(2*np.pi*np.cumsum(np.geomspace(200,900,n))/SR)*t**2
    return x
def shimmer():
    t=np.arange(int(0.6*SR))/SR
    return sum(0.06*np.sin(2*np.pi*f*t)*np.exp(-t*5) for f in [1568,2093,2637,3136])
sfx=np.zeros(N); placed=[]
def put(name,x,frame,gain=1.0,offset=0.0):
    i=int((frame/FPS+offset)*SR); x=x*gain; j=min(N,i+len(x)); sfx[i:j]+=x[:j-i]
    write(f"sound/stems/{name}_{frame:04d}.wav",x); placed.append((round(frame/FPS+offset,3),name))
c=cues
put("whoosh_hook10",whoosh(0.35),c["hookTen"],0.8,-0.12); put("impact_hook10",impact(),c["hookTen"]+6,0.45)
put("whoosh_wipe",whoosh(0.5),c["cut1"],0.9,-0.25)
put("tick_brandchip",tick(1800),c["brandChipIn"],0.6)
for k,b in enumerate(c["counts"]): put(f"clink_count{k+1}",can_clink(),b,0.55); put(f"tick_count{k+1}",tick(2000+k*180),b,0.5)
put("whoosh_strike",whoosh(0.25,False),c["notFifteen"][0]+2,0.7)
put("riser_offer",riser(),c["offerRiser"],0.9)
put("whoosh_offer",whoosh(0.45),c["offerIn"],0.8,-0.1)
put("impact_offer",impact(),c["offerImpact"],0.9)
put("tick_shekel",tick(1600),c["offerShekel"],0.6)
put("whoosh_badge",whoosh(0.3,False),c["offerToBadge"],0.6,-0.05)
put("shimmer_hero",shimmer(),c["heroSweep"],1.0); put("tick_herolabel",tick(2600),c["heroLabel"],0.5)
put("whoosh_brand",whoosh(0.4),c["brandIn"],0.7,-0.1); put("impact_brand",impact(),c["brandIn"]+8,0.35)
put("tick_address",tick(2200),c["addressIn"]+18,0.5)
put("whoosh_end",whoosh(0.5),c["endIn"],0.7,-0.2); put("impact_end",impact(),c["endIn"]+12,0.55)
write("sound/sfx_bus.wav",sfx)
# ---- original music bed: 112 BPM, A minor, kick / sub / hats / pad ----
bpm=112; beat=60/bpm; mus=np.zeros(N); t=np.arange(N)/SR
kick_t=np.arange(int(0.35*SR))/SR; kick=np.sin(2*np.pi*np.cumsum(120*np.exp(-kick_t*28)+45)/SR)*np.exp(-kick_t*9)
hat_t=np.arange(int(0.05*SR))/SR; hat=bp(rng.standard_normal(len(hat_t)),7000,15000)*np.exp(-hat_t*120)
roots=[110.0,87.31,130.81,98.0]   # Am F C G
for b in range(int(T/beat)+1):
    i=int(b*beat*SR)
    if i>=N: break
    k=kick[:N-i]; mus[i:i+len(k)]+=0.55*k
    h=int((b+0.5)*beat*SR); hh=hat[:max(0,N-h)]; mus[h:h+len(hh)]+=0.18*hh
for bar in range(int(T/(4*beat))+1):
    i0=int(bar*4*beat*SR); i1=min(N,int((bar+1)*4*beat*SR)); 
    if i0>=N: break
    r=roots[bar%4]; tt=np.arange(i1-i0)/SR
    pad=sum(np.sin(2*np.pi*r*m*tt+np.sin(2*np.pi*0.3*tt)*0.4) for m in [2,2*1.189,3,4])*0.03
    sub=np.sin(2*np.pi*r/2*tt)*0.12*(0.6+0.4*np.cos(2*np.pi*tt/beat))
    env_=np.minimum(1,tt/0.05)*np.minimum(1,(tt[::-1])/0.05)
    mus[i0:i1]+=(pad+sub)*env_
# arrangement: thin intro, full from offer, lift at brand, tail on end card
lvl=np.interp(t,[0,2.6,2.7,c["offerIn"]/FPS,c["offerImpact"]/FPS,T-0.8,T],[0.7,0.7,0.45,0.5,0.85,0.85,0])
mus*=lvl
# brief music drop (silence) right before offer impact for contrast
d0,d1=c["offerImpact"]/FPS-0.35,c["offerImpact"]/FPS; m=(t>d0)&(t<d1); mus[m]*=0.15
write("sound/music_bed.wav",mus*0.6)
json.dump(placed,open("sound/cue_sheet.json","w"),indent=0)
# ---- mix: voice (already cleaned in build_base) + sidechain-ducked music + sfx, then loudness normalise ----
subprocess.run(["ffmpeg","-v","error","-y","-i","render/voice.wav","-i","sound/music_bed.wav","-i","sound/sfx_bus.wav","-filter_complex",
 "[0:a]aresample=48000,asplit[v][vk];[1:a][vk]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=300[md];"
 "[md]volume=0.55[m];[2:a]volume=0.8[s];[v][m][s]amix=inputs=3:normalize=0,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=9[a]",
 "-map","[a]","-ar","48000","-ac","2","render/mix.wav"],check=True)
print(len(placed),"sfx placed")
