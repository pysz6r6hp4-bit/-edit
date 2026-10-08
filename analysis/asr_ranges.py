import sherpa_onnx, numpy as np, wave, sys
M="/tmp/claude-0/-home-user--edit/2c694ac7-7487-591c-86e6-f7ab35253791/scratchpad/models/sherpa-onnx-whisper-turbo/turbo-"
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+"encoder.int8.onnx",decoder=M+"decoder.int8.onnx",tokens=M+"tokens.txt",language="ar",task="transcribe",num_threads=4)
w=wave.open("analysis/audio16k.wav");a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
for arg in sys.argv[1:]:
    t0,t1=map(float,arg.split(':'));s=r.create_stream(); s.accept_waveform(16000,np.concatenate([a[int(t0*16000):int(t1*16000)],np.zeros(8000,np.float32)])); r.decode_stream(s)
    print(f"{t0:5.2f}-{t1:5.2f} {s.result.text}",flush=True)
