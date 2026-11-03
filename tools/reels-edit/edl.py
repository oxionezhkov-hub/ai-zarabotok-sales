import json, wave, numpy as np
SRC="src/IMG_3600.MOV"
# (start, end, zoom, text)   start/end in source seconds (already snapped to silence / low energy)
w=wave.open("audio/3600.wav"); A=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
def rms_min(t,lo,hi):
    a=int((t-lo)*16000); b=int((t+hi)*16000); fr=160
    best=None
    for i in range(a,b-fr,fr//2):
        v=float(np.sqrt(np.mean(A[i:i+fr]**2)))
        if best is None or v<best[0]: best=(v,i/16000+fr/32000)
    return best
if __name__=="__main__":
    for t in (109.4,):
        print("energy-min near",t,rms_min(t,0.1,0.7))
    for t in (87.97,96.93):
        print("check",t,rms_min(t,0.15,0.15))
