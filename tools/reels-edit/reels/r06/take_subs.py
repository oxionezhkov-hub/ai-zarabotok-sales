"""aligned.json from per-take texts: words spread over each take's real speech span (energy), by length."""
import sys,json,wave,numpy as np,importlib.util,os
seg=sys.argv[1];texts=json.load(open(sys.argv[2]))[seg]
spec=importlib.util.spec_from_file_location("p",f"{seg}/pieces.py");p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
w=wave.open(f"{seg}/voice16.wav");x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768;sr=16000
e=np.sqrt(np.convolve(x**2,np.ones(320)/320,mode="same"))
out=[];t0=0
for (f0,n,z),txt in zip(p.PIECES,texts):
    d=n/30;seg_e=e[int(t0*sr):int((t0+d)*sr)];idx=np.where(seg_e>0.015)[0]
    s=t0+(idx[0]/sr if len(idx) else 0.05);en=t0+(idx[-1]/sr if len(idx) else d-0.05)
    ws=txt.split();L=[len(q)+1 for q in ws];tot=sum(L);cur=s
    for q,l in zip(ws,L):
        dd=(en-s)*l/tot;out.append({"w":q,"s":round(cur,3),"e":round(cur+dd,3)});cur+=dd
    t0+=d
json.dump(out,open(f"{seg}/aligned.json","w"),ensure_ascii=False);print(seg,len(out),"words")
