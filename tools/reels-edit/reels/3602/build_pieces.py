"""IMG_3602 v2: tighter start, no 'и на этом сфокусироваться', initial 'и' removed, cough removed, B&W question."""
import wave,numpy as np
w=wave.open("../audio/3602.wav");A=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768;sr=16000
e=np.sqrt(np.convolve(A**2,np.ones(160)/160,mode="same"))
def split(a,b,thr=0.010,gap=0.14,m0=0.04,m1=0.05):
    """split a stretch of speech at internal pauses longer than `gap`, keep small margins (removes the pauses)"""
    seg=e[int(a*sr):int(b*sr)]>thr;out=[];st=None;last=None
    for i,v in enumerate(seg):
        t=a+i/sr
        if v:
            if st is None: st=t
            last=t
        elif st is not None and t-last>gap: out.append((max(a,st-m0),min(b,last+m1)));st=None
    if st is not None: out.append((max(a,st-m0),min(b,last+m1)))
    return out
# (audio start, end, parent id, split?, bw)
plan=[(35.23,39.50,1,True,True),(40.47,42.00,2,True,False),(44.433,46.70,3,False,False),(46.82,54.03,4,True,False),
      (54.21,56.45,5,False,False),(67.54,74.64,6,True,False),(74.85,78.88,7,False,False),(79.467,80.18,8,False,False),
      (80.39,81.66,9,False,False),(81.84,84.03,10,False,False),(92.65,95.64,11,False,False),(95.90,98.25,12,False,False),
      (98.41,99.79,13,False,False),(100.02,105.20,14,False,False),(136.78,140.93,15,True,False),(141.08,143.42,16,False,False),
      (147.85,150.45,17,False,False),(150.65,153.95,18,False,False),(158.05,159.38,19,False,False),(159.51,161.33,20,False,False),
      (161.68,162.58,21,False,False),(187.833,194.0,22,False,False),(215.80,217.50,23,False,False)]
P=[];ZR=[];BW=[];AST=[]
for k,(a,b,pid,sp,bw) in enumerate(plan):
    parts=split(a,b) if sp else [(a,b)]
    zs,ze=(1.00,1.05) if k%2==0 else (1.13,1.08)
    tot=sum(y-x for x,y in parts);acc=0
    for (x,y) in parts:
        f0=int(x*30);n=max(1,round((y-x)*30))           # video starts at the frame containing x
        z0=zs+(ze-zs)*acc/tot;acc+=y-x;z1=zs+(ze-zs)*acc/tot
        P.append((f0,n,1.0));ZR.append((round(z0,4),round(z1,4)));AST.append(round(x,3))
        if bw: BW.append(len(P)-1)
open("pieces.py","w").write("# IMG_3602 v2: (first video frame, frames, zoom-unused); AST = exact audio start (s); ZR = camera zoom start/end; BW = black-and-white pieces\nFPS=30\nPIECES=[\n"
  +"\n".join(f" {p}," for p in P)+"\n]\nAST="+repr(AST)+"\nZR="+repr(ZR)+"\nBW="+repr(BW)+"\n")
print(len(P),"pieces",round(sum(n for f0,n,z in P)/30,2),"s; BW",BW)
