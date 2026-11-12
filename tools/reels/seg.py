import sys,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
for spec in sys.argv[2:]:
    n,a,b=spec.split(':');a=float(a);b=float(b)
    w=wave.open(f"{sys.argv[1]}/{n}.wav");w.setpos(int(a*16000))
    x=np.frombuffer(w.readframes(int((b-a)*16000)),np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(x,language="ru",beam_size=5,condition_on_previous_text=False)
    print(spec,"->"," ".join(s.text.strip() for s in segs))
