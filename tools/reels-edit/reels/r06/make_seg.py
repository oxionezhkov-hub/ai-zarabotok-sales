"""Build one blooper segment: takes (chunks) from one source, counter card, aligned subtitles.
  python3 make_seg.py <name> <src_id> "<label>" "<text>" <a1>:<b1> <a2>:<b2> ...   (last take = the good one)"""
import sys,os,json,subprocess,wave,math,re
import numpy as np
name,src,label,text=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
takes=[tuple(map(float,x.split(":"))) for x in sys.argv[5:]]
os.makedirs(name,exist_ok=True);os.chdir(name)
P=[];AST=[];ZR=[]
for k,(a,b) in enumerate(takes):
    a-=0.04;b+=0.05
    f0=int(a*30);n=round((b-a)*30)
    zs,ze=(1.00,1.05) if k%2==0 else (1.12,1.07)
    P.append((f0,n,1.0));AST.append(round(a,3));ZR.append((zs,ze))
open("pieces.py","w").write("FPS=30\nPIECES="+repr(P)+"\nAST="+repr(AST)+"\nZR="+repr(ZR)+"\nBW=[]\n")
fc=[];ins=[]
for i,((f0,n,z),a) in enumerate(zip(P,AST)):
    s0=round(a*48000);fc.append(f"[0:a]atrim=start_sample={s0}:end_sample={s0+n*1600},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={n/30-0.02:.4f}:d=0.02[a{i}]");ins.append(f"[a{i}]")
fc.append("".join(ins)+f"concat=n={len(P)}:v=0:a=1[out]")
open("voice.filter","w").write(";\n".join(fc))
subprocess.run(["ffmpeg","-y","-v","error","-i",f"../../src/IMG_{src}.MOV","-filter_complex_script","voice.filter","-map","[out]","-ac","1","-ar","16000","voice16.wav"],check=True)
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
w=wave.open("voice16.wav");x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs=list(m.transcribe(x,language="ru",word_timestamps=True,beam_size=5,condition_on_previous_text=False)[0])
words=[{"w":t.word.strip(),"s":t.start,"e":t.end} for s in segs for t in s.words]
json.dump(words,open("words.json","w"),ensure_ascii=False)
print(name,"|"," ".join(s.text.strip() for s in segs))
al=open("../../r3602/align.py",encoding="utf-8").read()
al=re.sub(r'TEXT="""(.*?)"""',lambda mm:'TEXT="""'+text+'"""',al,flags=re.S)
open("align.py","w",encoding="utf-8").write(al)
subprocess.run(["python3","align.py"],check=True)
# counter card: «Дубль N» per take, «✓ Получилось» on the last one
from PIL import Image,ImageDraw,ImageFont,ImageFilter
F=lambda wt,s:ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{wt}.otf",max(6,int(s)))
starts=[0]
for f0,n,z in P: starts.append(starts[-1]+n/30)
D=starts[-1];os.makedirs("cards/count",exist_ok=True)
def out_back(q,k=2.2):
    q=max(0,min(1,q));c3=k+1;return 1+c3*(q-1)**3+k*(q-1)**2
CW,CH=760,230
for i in range(int(D*30)):
    t=i/30;k=max(j for j in range(len(P)) if starts[j]<=t+1e-6);last=(k==len(P)-1)
    sc=0.75+0.25*out_back((t-starts[k])/0.3)
    c=Image.new("RGBA",(CW,CH),(0,0,0,0));d=ImageDraw.Draw(c)
    d.rounded_rectangle((60,20,CW-60,CH-20),radius=46,fill=(22,22,27,240),outline=(255,255,255,38),width=2)
    d.text((CW/2,64),label,font=F("Bold",28),fill=(255,255,255,170),anchor="mm")
    txt="✓ Получилось" if last else f"Дубль {k+1}"
    col=(120,230,140,255) if last else (255,212,0,255)
    ov=Image.new("RGBA",(CW,CH),(0,0,0,0));ImageDraw.Draw(ov).text((CW/2,140),txt,font=F("ExtraBold",76),fill=col,anchor="mm")
    ov=ov.resize((int(CW*sc),int(CH*sc)),Image.LANCZOS);c.alpha_composite(ov,((CW-ov.width)//2,(CH-ov.height)//2+int(20*(1-sc))))
    c.save(f"cards/count/{i+1:04d}.png")
json.dump([dict(kind="seq",pattern="cards/count/%04d.png",start=0.0,dur=round(D,3),y=40,w=CW)],open("overlays.json","w"))
print(name,"takes",len(P),"dur",round(D,2))
