import json,re,subprocess,sys
from pieces import PIECES,FPS
SRC=sys.argv[3] if len(sys.argv)>3 else "src/IMG_3600.MOV"
SC=float(sys.argv[1]); OUT=sys.argv[2]
W,H=int(1080*SC),int(1920*SC)
A=json.load(open("build/aligned.json")); CT=json.load(open("build/cardC_t.json"))
starts=[0.0]
for f0,n,z in PIECES: starts.append(starts[-1]+n/FPS)
tot=starts[-1]
def tw(word,last=False):
    L=[x for x in A if x["w"].strip("«»,.:?").lower()==word]
    return (L[-1] if last else L[0])["s"]
# ---------- subtitles: groups of three plain white words
def clean(w): return re.sub(r"[,.:;«»?]","",w)
FUNC={"и","в","на","с","не","я","а","но","то","что","к","у","о","за","для","по","от","из","до","ни","же","ли","или","как","это","вот"}
from PIL import ImageFont,Image,ImageDraw
_F=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",84);_D=ImageDraw.Draw(Image.new("L",(8,8)))
LIBASS=0.823          # measured: libass width / PIL width for Inter ExtraBold at size 84
LIMIT=900             # max line width in px at 1080 wide (outline included below)
def wpx(words): return _D.textlength(" ".join(clean(w["w"]) for w in words),font=_F)*LIBASS+18
chunks=[];cur=[]
for x in A:
    if cur and (len(cur)>=3 or wpx(cur+[x])>LIMIT):
        chunks.append(cur);cur=[]
    cur.append(x)
    if x["w"].endswith(("?",".","!")): chunks.append(cur);cur=[]
if cur: chunks.append(cur)
# do not leave a lone short function word at the end of a line if the next word fits
i=0
while i<len(chunks)-1:
    a,b=chunks[i],chunks[i+1]
    if len(a)>=2 and clean(a[-1]["w"]).lower() in FUNC and not a[-1]["w"].endswith((",",".","?","!",":")) and wpx(b[:0]+[a[-1]]+b)<=LIMIT and len(b)<=2:
        b.insert(0,a.pop())
    i+=1
WIDTHS=[round(wpx(c)) for c in chunks]
def ts(t):
    t=max(t,0);h=int(t//3600);m=int(t%3600//60);s=t%60;return f"{h}:{m:02d}:{s:05.2f}"
ev=[]
for ci,ch in enumerate(chunks):
    s=ch[0]["s"];nxt=chunks[ci+1][0]["s"] if ci+1<len(chunks) else tot
    e=min(ch[-1]["e"]+0.28,nxt) if ci+1<len(chunks) else min(ch[-1]["e"]+0.28,tot)
    wd=wpx(ch);fs="" if wd<=LIMIT else "{\\fs%d}"%int(84*LIMIT/wd)
    ev.append(f"Dialogue: 0,{ts(s)},{ts(max(e,s+0.2))},Tik,,0,0,0,,"+fs+" ".join(clean(y["w"]) for y in ch))
hdr=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Tik,Inter ExtraBold,{int(84*SC)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{max(2,int(9*SC))},{max(1,int(3*SC))},2,{int(70*SC)},{int(70*SC)},{int(420*SC)},1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
open("build/subs.ass","w",encoding="utf-8").write(hdr+"\n".join(ev)+"\n")
# ---------- inputs: frame-exact pieces (video N frames, audio N*1600 samples)
n=len(PIECES);args=["ffmpeg","-y","-v","error"]
for f0,nf,z in PIECES: args+=["-ss",f"{f0/FPS:.6f}","-i",SRC]
k=n;fc=[]
grade="colorchannelmixer=rr=0.904:gg=1:bb=1.071,eq=contrast=1.04:saturation=0.98"
vi=[];ai=[]
for i,(f0,nf,z) in enumerate(PIECES):
    zf=f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.30," if z>1 else ""
    fc.append(f"[{i}:v]fps={FPS},trim=end_frame={nf},setpts=PTS-STARTPTS,{zf}scale={W}:{H}:flags=lanczos,setsar=1,{grade},format=yuv420p[v{i}]");vi.append(f"[v{i}]")
    fc.append(f"[{i}:a]asetpts=PTS-STARTPTS,atrim=end_sample={nf*1600},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={nf/FPS-0.012:.4f}:d=0.012[a{i}]");ai.append(f"[a{i}]")
fc.append("".join(vi)+f"concat=n={n}:v=1:a=0[base]")
voice=("highpass=f=90,equalizer=f=170:t=o:w=1.3:g=-3.5,equalizer=f=330:t=o:w=1.0:g=-2,"
       "equalizer=f=2800:t=o:w=1.2:g=5,equalizer=f=5400:t=o:w=1.0:g=4.5,highshelf=f=8000:g=3,"
       "acompressor=threshold=-21dB:ratio=2.2:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo,alimiter=limit=0.95")
fc.append("".join(ai)+f"concat=n={n}:v=0:a=1,{voice}[aout]")
cur="base"
def add(inargs,label,start,dur,y,wid,fade_in=0.0,fade_out=0.0,baked=False):
    global k,cur
    args.extend(inargs);ch=f"[{k}:v]scale={wid}:-1:flags=lanczos,format=rgba"
    if not baked:
        if fade_in: ch+=f",fade=t=in:st=0:d={fade_in}:alpha=1"
        if fade_out: ch+=f",fade=t=out:st={dur-fade_out:.2f}:d={fade_out}:alpha=1"
    ch+=f",setpts=PTS+{start:.3f}/TB[{label}]";fc.append(ch)
    fc.append(f"[{cur}][{label}]overlay=x=(W-w)/2:y={y}:eof_action=pass:enable='between(t,{start:.3f},{start+dur:.3f})'[{label}o]")
    cur=f"{label}o";k+=1
# B-roll: full-screen site scroll over the piece "нейросеть сама делает ... дизайн"
bs,be=starts[4],starts[5]
add(["-framerate","30","-t",f"{be-bs:.2f}","-i","build/scrollx/%04d.jpg"],"sc",bs,be-bs,0,W,fade_in=0.12,fade_out=0.12)
tA=tw("сделай")-0.05
add(["-framerate","30","-i","build/A/%04d.png"],"cA",tA,3.4,int(130*SC),int(1004*SC),baked=True)
tB=tw("синий")-1.4
add(["-framerate","30","-i","build/B/%04d.png"],"cB",tB,3.6,int(110*SC),int(880*SC),baked=True)
add(["-framerate","30","-i","build/C/%04d.png"],"cC",CT["start"],CT["end"]-CT["start"],int(70*SC),int(808*SC),baked=True)
tD=tw("если",last=True)-0.05
add(["-loop","1","-framerate","30","-t",f"{tot-tD+0.3:.2f}","-i","build/cardD2.png"],"cD",tD,tot-tD,int(160*SC),int(980*SC),fade_in=0.2,fade_out=0.25)
fc.append(f"[{cur}]ass=build/subs.ass:fontsdir=/usr/share/fonts/opentype/inter[vout]")
args+=["-filter_complex",";\n".join(fc),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart","-frames:v",str(sum(nf for f0,nf,z in PIECES)),OUT]
print("max subtitle width",max(WIDTHS),"of",LIMIT,"| lines",len(chunks));print("tot",round(tot,3),"cards",dict(A=round(tA,2),B=round(tB,2),C=round(CT['start'],2),D=round(tD,2),bs=round(bs,2),be=round(be,2)),flush=True)
r=subprocess.run(args,capture_output=True,text=True);print(r.returncode,r.stderr[-1500:])
