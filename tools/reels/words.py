import sys,json,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
d=sys.argv[1]
for spec in sys.argv[2:]:
    n,a,b=spec.split(':'); a=float(a); b=float(b)
    w=wave.open(f"{d}/{n}.wav"); w.setpos(int(a*16000))
    x=np.frombuffer(w.readframes(int((b-a)*16000)),np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(x,language="ru",word_timestamps=True,beam_size=5)
    out=[]
    for s in segs:
        for wd in s.words: out.append([round(wd.start+a,2),round(wd.end+a,2),wd.word.strip()])
    json.dump(out,open(f"{d}/w_{n}_{int(a)}.json","w"),ensure_ascii=False)
    print("==",spec); print(" ".join(f"{t0:.2f}|{t}" for t0,t1,t in out))
