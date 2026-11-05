"""r05 «Раньше и сейчас» from IMG_3599: B&W «раньше», colour from «то сейчас»."""
import wave,numpy as np
w=wave.open("../audio/3599.wav");A=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768;sr=16000
e=np.sqrt(np.convolve(A**2,np.ones(160)/160,mode="same"))
def split(a,b,thr=0.010,gap=0.14,m0=0.04,m1=0.05):
    seg=e[int(a*sr):int(b*sr)]>thr;out=[];st=None;last=None
    for i,v in enumerate(seg):
        t=a+i/sr
        if v:
            if st is None: st=t
            last=t
        elif st is not None and t-last>gap: out.append((max(a,st-m0),min(b,last+m1)));st=None
    if st is not None: out.append((max(a,st-m0),min(b,last+m1)))
    return out
# (start, end, split?, bw)
plan=[(123.52,132.92,True,True),     # Если раньше ... в коде, в дизайне, в разработке
      (133.09,133.76,False,False),   # то сейчас
      (133.97,135.96,False,False),   # просто нужно открыть нейросеть
      (136.21,138.28,False,False),   # и сказать, что вы хотите сделать
      (138.59,140.30,False,False),   # и получить за это оплату
      (144.667,147.533,False,False), # Так можно брать любые заказы по сайтам
      (149.633,152.300,False,False), # по картинкам, по рилсам, по статьям
      (164.733,168.733,False,False)] # И это на самом деле проще делать, чем многим кажется
P=[];ZR=[];BW=[];AST=[]
for k,(a,b,sp,bw) in enumerate(plan):
    parts=split(a,b) if sp else [(a,b)]
    zs,ze=(1.00,1.06) if k%2==0 else (1.14,1.08)
    tot=sum(y-x for x,y in parts);acc=0
    for (x,y) in parts:
        f0=int(x*30);n=max(1,round((y-x)*30))
        z0=zs+(ze-zs)*acc/tot;acc+=y-x;z1=zs+(ze-zs)*acc/tot
        P.append((f0,n,1.0));ZR.append((round(z0,4),round(z1,4)));AST.append(round(x,3))
        if bw: BW.append(len(P)-1)
open("pieces.py","w").write("# r05 (IMG_3599): (first video frame, frames, -); AST exact audio start; ZR camera zoom; BW black-and-white\nFPS=30\nPIECES=[\n"
  +"\n".join(f" {p}," for p in P)+"\n]\nAST="+repr(AST)+"\nZR="+repr(ZR)+"\nBW="+repr(BW)+"\n")
print(len(P),"pieces",round(sum(n for f0,n,z in P)/30,2),"s; BW",BW)
