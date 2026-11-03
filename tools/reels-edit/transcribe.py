import json,sys,wave
import numpy as np
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device="cpu",compute_type="int8",cpu_threads=4)
out={}
for n in ["3599","3600","3601","3602"]:
    w=wave.open(f"audio/{n}.wav");a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    segs,info=m.transcribe(a,language="ru",word_timestamps=True,vad_filter=False,beam_size=5,condition_on_previous_text=False)
    L=[]
    for s in segs:
        L.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end} for w in (s.words or [])]})
    out[n]=L
    json.dump(out,open("transcript.json","w"),ensure_ascii=False)
    print(n,"done",len(L),flush=True)
