"""r07-dental-story: main part M from validated IMG_3602 v2 pieces (reordered), words and cards shifted from r3602."""
import json,os,sys
sys.path.insert(0,"../r3602");import pieces as p
A=json.load(open("../r3602/aligned.json"));O=json.load(open("../r3602/overlays.json"))
st=[0]
for f0,n,z in p.PIECES: st.append(st[-1]+n/30)
ORDER=[20,21,13,14,15,16,17,18,22,23,24,25,26,27,28,29,30,31]
P=[];AST=[];ZR=[];W=[];OV=[];t=0
for k,i in enumerate(ORDER):
    f0,n,z=p.PIECES[i];a=p.AST[i];s0,s1=st[i],st[i+1];cut=0.0
    if i==20:   # drop «Либо»: start at 98.69 (checked by transcription)
        f0=int(98.69*30);n=n-(f0-p.PIECES[i][0]);cut=98.69-a;a=98.69
    P.append((f0,n,1.0));AST.append(a);ZR.append(p.ZR[i])
    for w in A:
        if s0-0.02<=w["s"]<s1-0.02 and w["e"]>s0+cut+0.08:
            W.append({"w":w["w"],"s":round(max(w["s"]-s0-cut,0.03)+t,3),"e":round(w["e"]-s0-cut+t,3)})
    for o in O:
        if s0-0.01<=o["start"]<s1-0.01:
            o2=dict(o);o2["start"]=round(o["start"]-s0-cut+t,3);OV.append((o2,o["start"]))
    t+=n/30
D=t
# clip overlays so they end inside their run
for o2,_ in OV: o2["dur"]=round(min(o2["dur"],D-o2["start"]),3)
W[0]["w"]=W[0]["w"].capitalize()
os.chdir("M")
open("pieces.py","w").write("FPS=30\nPIECES="+repr(P)+"\nAST="+repr(AST)+"\nZR="+repr(ZR)+"\nBW=[]\n")
json.dump(W,open("aligned.json","w"),ensure_ascii=False)
ov=[o for o,_ in OV]
for o in ov:
    if not o["pattern"].startswith("/"): o["pattern"]="../../r3602/"+o["pattern"]
json.dump(ov,open("overlays.json","w"),ensure_ascii=False,indent=1)
print("dur",round(D,3));print(" ".join(w["w"] for w in W));print(ov)
