from faster_whisper import WhisperModel
import json
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
segs,_=m.transcribe("analysis/audio16k.wav",language="ar",word_timestamps=True,beam_size=5)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end} for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}",flush=True)
json.dump(out,open("analysis/transcript.json","w"),ensure_ascii=False,indent=1)
