import sys,json
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
for n in sys.argv[2:]:
    import wave,numpy as np; w=wave.open(f"{sys.argv[1]}/{n}.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768; segs,_=m.transcribe(a,language="ru",vad_filter=False,beam_size=3)
    with open(f"{sys.argv[1]}/{n}.txt","w") as f:
        for s in segs: f.write(f"[{s.start:6.1f}-{s.end:6.1f}] {s.text.strip()}\n")
    print("done",n,flush=True)
