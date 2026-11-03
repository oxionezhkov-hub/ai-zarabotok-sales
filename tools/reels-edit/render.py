import json,re,subprocess,sys
from pieces import PIECES
SC=float(sys.argv[1]); OUT=sys.argv[2]
W,H=int(1080*SC),int(1920*SC)
A=json.load(open("build/aligned.json")); cards=json.load(open("build/cards_t.json"))
# ---------- ASS
def clean(w): return re.sub(r"[,.:;«»]","",w)
chunks=[];cur=[]
for i,x in enumerate(A):
    cur.append(x); t=x["w"]
    L=sum(len(clean(c["w"])) for c in cur)+len(cur)-1
    end_sent=t.endswith(("?",".","!"))
    FUNC={"и","в","на","с","не","я","а","но","то","что","к","у","о","за","для","по","от","из","до","ни","же","ли","или","как","это","вот","же"}
    last=clean(t).lower()
    soft=(len(cur)>=3 or L>=17) and not end_sent and not t.endswith((",",":")) and last in FUNC and len(cur)<5
    brk=(end_sent or (t.endswith((",",":")) and len(cur)>=2) or len(cur)>=3 or L>=17) and not soft
    if brk: chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def ts(t): 
    t=max(t,0);h=int(t//3600);m=int(t%3600//60);s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"
ev=[]
for ci,ch in enumerate(chunks):
    nxt=chunks[ci+1][0]["s"] if ci+1<len(chunks) else 1e9
    for wi,x in enumerate(ch):
        s=x["s"]; 
        e=ch[wi+1]["s"] if wi+1<len(ch) else min(x["e"]+0.18,nxt)
        e=max(e,s+0.08)
        parts=[]
        for wj,y in enumerate(ch):
            c=clean(y["w"]).upper() if False else clean(y["w"])
            parts.append(("{\\c&H00D4FF&}"+c+"{\\c&HFFFFFF&}") if wj==wi else c)
        pop="{\\fscx88\\fscy88\\t(0,110,\\fscx100\\fscy100)}" if wi==0 else ""
        ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Tik,,0,0,0,,{pop}"+" ".join(parts))
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
# ---------- video
fc=[];ins=[];args=["ffmpeg","-y","-v","error"]
for i,(a,b,z) in enumerate(PIECES):
    args+=["-ss",str(a),"-t",str(b-a),"-i","src/IMG_3600.MOV"]
    zf=f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.30," if z>1 else ""
    fc.append(f"[{i}:v]{zf}scale={W}:{H}:flags=lanczos,setsar=1,fps=30,eq=contrast=1.06:saturation=1.08:brightness=0.01,format=yuv420p[v{i}]")
    ins.append(f"[v{i}]")
fc.append("".join(ins)+f"concat=n={len(PIECES)}:v=1:a=0[base]")
n=len(PIECES)
# audio inputs
args+=["-i","build/music.wav","-i","build/sfx.wav"]; ex=n
vo=[]
for i,(a,b,z) in enumerate(PIECES):
    d=b-a
    fc.append(f"[{i}:a]atrim=0:{d:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
    vo.append(f"[a{i}]")
fc.append("".join(vo)+f"concat=n={n}:v=0:a=1,highpass=f=70,afftdn=nf=-32,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo[voice]")
fc.append(f"[{ex}:a]volume=1.0[mu]")
fc.append(f"[{ex+1}:a]volume=1.0[fx]")
fc.append("[voice][mu][fx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[aout]")
# cards
cardspec=[("A",cards["A"],cards["A"]+3.2,190),("B",cards["B"],cards["B"]+3.6,190),("C",cards["C"],cards["C"]+4.6,190),("D",cards["D"],cards["D"]+3.6,190)]
cur="base";k=ex+2
for name,s,e,y in cardspec:
    args+=["-loop","1","-framerate","30","-t",f"{e-s+0.4:.2f}","-i",f"build/card{name}.png"]
    d=e-s
    fc.append(f"[{k}:v]scale={int(820*SC)}:-1,format=rgba,fade=t=in:st=0:d=0.18:alpha=1,fade=t=out:st={d-0.2:.2f}:d=0.2:alpha=1,setpts=PTS+{s}/TB[c{name}]")
    fc.append(f"[{cur}][c{name}]overlay=x=(W-w)/2:y={int(y*SC)}:eof_action=pass:enable='between(t,{s},{e+0.3})'[o{name}]")
    cur=f"o{name}";k+=1
fc.append(f"[{cur}]ass=build/subs.ass:fontsdir=/usr/share/fonts/opentype/inter[vout]")
args+=["-filter_complex",";\n".join(fc),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-t",f"{sum(b-a for a,b,z in PIECES):.2f}",OUT]
open("build/cmd.txt","w").write(" ".join(map(repr,args)))
r=subprocess.run(args,capture_output=True,text=True)
print(r.returncode,r.stderr[-1500:])
