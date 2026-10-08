import sherpa_onnx, numpy as np, wave, sys, json
M="/tmp/claude-0/-home-user--edit/2c694ac7-7487-591c-86e6-f7ab35253791/scratchpad/models/sherpa-onnx-whisper-turbo/turbo-"
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+"encoder.int8.onnx",decoder=M+"decoder.int8.onnx",tokens=M+"tokens.txt",language="ar",task="transcribe",num_threads=4)
w=wave.open("analysis/audio16k.wav");a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
step=float(sys.argv[1]); win=float(sys.argv[2]); t=0; out=[]
while t<len(a)/16000:
    s=r.create_stream(); s.accept_waveform(16000,a[int(t*16000):int((t+win)*16000)]); r.decode_stream(s)
    print(f"{t:5.1f}-{t+win:5.1f} {s.result.text}",flush=True); out.append([t,t+win,s.result.text]); t+=step
json.dump(out,open(f"analysis/asr_{step}_{win}.json","w"),ensure_ascii=False,indent=0)
