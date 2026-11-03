import json,re,subprocess,sys
from pieces import PIECES
SC=float(sys.argv[1]); OUT=sys.argv[2]
W,H=int(1080*SC),int(1920*SC)
A=json.load(open("build/aligned.json")); E=json.load(open("build/events2.json"))["cards"]
tot=sum(b-a for a,b,z in PIECES)
# ---------- ASS (same style as v1)
def clean(w): return re.sub(r"[,.:;«»?]","",w)
FUNC={"и","в","на","с","не","я","а","но","то","что","к","у","о","за","для","по","от","из","до","ни","же","ли","или","как","это","вот"}
chunks=[];cur=[]
for x in A:
    cur.append(x); t=x["w"]; L=sum(len(clean(c["w"])) for c in cur)+len(cur)-1
    end_sent=t.endswith(("?",".","!"))
    soft=(len(cur)>=3 or L>=17) and not end_sent and not t.endswith((",",":")) and clean(t).lower() in FUNC and len(cur)<5
    brk=(end_sent or (t.endswith((",",":")) and len(cur)>=2) or len(cur)>=3 or L>=17) and not soft
    if brk: chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def ts(t):
    t=max(t,0);h=int(t//3600);m=int(t%3600//60);s=t%60;return f"{h}:{m:02d}:{s:05.2f}"
ev=[]
for ci,ch in enumerate(chunks):
    nxt=chunks[ci+1][0]["s"] if ci+1<len(chunks) else 1e9
    for wi,x in enumerate(ch):
        s=x["s"];e=ch[wi+1]["s"] if wi+1<len(ch) else min(x["e"]+0.18,nxt);e=max(e,s+0.08)
        parts=[("{\\c&H00D4FF&}"+clean(y["w"])+"{\\c&HFFFFFF&}") if wj==wi else clean(y["w"]) for wj,y in enumerate(ch)]
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
# ---------- inputs
n=len(PIECES);args=["ffmpeg","-y","-v","error"]
for a,b,z in PIECES: args+=["-ss",str(a),"-t",str(b-a),"-i","src/IMG_3600.MOV"]
args+=["-i","build/music.wav","-i","build/sfx.wav"]; mi=n; fi=n+1; k=n+2
starts=[0];
for a,b,z in PIECES: starts.append(starts[-1]+b-a)
p4s,p4e=starts[3],starts[4]
imgs=[]  # (label,args,start,dur,kind,y,scale)
def seq(pat,frames): return ["-framerate","30","-start_number","1","-i",pat]
fc=[]
# colour: neutralise warm cast measured on the white t-shirt (R x0.904, B x1.071), no saturation boost
grade="colorchannelmixer=rr=0.904:gg=1:bb=1.071,eq=contrast=1.04:saturation=0.98"
ins=[]
for i,(a,b,z) in enumerate(PIECES):
    zf=f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.30," if z>1 else ""
    fc.append(f"[{i}:v]{zf}scale={W}:{H}:flags=lanczos,setsar=1,fps=30,{grade},format=yuv420p[v{i}]");ins.append(f"[v{i}]")
fc.append("".join(ins)+f"concat=n={n}:v=1:a=0[base]")
# voice chain: remove boominess, add presence and air, light compression, loudness
vo=[]
for i,(a,b,z) in enumerate(PIECES):
    d=b-a
    fc.append(f"[{i}:a]atrim=0:{d:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]");vo.append(f"[a{i}]")
voice=("highpass=f=90,equalizer=f=170:t=o:w=1.3:g=-3.5,equalizer=f=330:t=o:w=1.0:g=-2,"
       "equalizer=f=2800:t=o:w=1.2:g=5,equalizer=f=5400:t=o:w=1.0:g=4.5,highshelf=f=8000:g=3,"
       "acompressor=threshold=-21dB:ratio=2.2:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo")
fc.append("".join(vo)+f"concat=n={n}:v=0:a=1,{voice}[voice]")
fc.append(f"[{mi}:a]volume=1.0[mu]");fc.append(f"[{fi}:a]volume=1.0[fx]")
fc.append("[voice][mu][fx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[aout]")
cur="base"
def add(inargs,label,start,dur,y,wid,fade_in=0.0,fade_out=0.0,baked=False,center=True):
    global k,cur
    args.extend(inargs);ch=f"[{k}:v]scale={wid}:-1:flags=lanczos,format=rgba"
    if not baked:
        if fade_in: ch+=f",fade=t=in:st=0:d={fade_in}:alpha=1"
        if fade_out: ch+=f",fade=t=out:st={dur-fade_out:.2f}:d={fade_out}:alpha=1"
    ch+=f",setpts=PTS+{start:.3f}/TB[{label}]";fc.append(ch)
    fc.append(f"[{cur}][{label}]overlay=x=(W-w)/2:y={y}:eof_action=pass:enable='between(t,{start:.3f},{start+dur:.3f})'[{label}o]")
    cur=f"{label}o";k+=1
# B-roll scroll (full screen) over piece 4
add(["-framerate","30","-t",f"{p4e-p4s:.2f}","-i","build/scrollx/%04d.jpg"],"sc",p4s,p4e-p4s,0,W,fade_in=0.12,fade_out=0.12)
add(["-framerate","30","-i","build/A/%04d.png"],"cA",E["A"],3.4,int(130*SC),int(1004*SC),baked=True)
add(["-framerate","30","-i","build/B/%04d.png"],"cB",E["B"],3.6,int(110*SC),int(880*SC),baked=True)
add(["-loop","1","-framerate","30","-t","4.8","-i","build/cardC.png"],"cC",E["C"],4.6,int(200*SC),int(820*SC),fade_in=0.18,fade_out=0.2)
dD=min(3.6,tot-E["D"]-0.02)
add(["-loop","1","-framerate","30","-t",f"{dD+0.4:.2f}","-i","build/cardD2.png"],"cD",E["D"],dD,int(160*SC),int(980*SC),fade_in=0.18,fade_out=0.2)
fc.append(f"[{cur}]ass=build/subs.ass:fontsdir=/usr/share/fonts/opentype/inter[vout]")
args+=["-filter_complex",";\n".join(fc),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-t",f"{tot:.2f}",OUT]
r=subprocess.run(args,capture_output=True,text=True);print(r.returncode,r.stderr[-1800:])
