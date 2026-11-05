from PIL import Image,ImageDraw,ImageFont
import os,shutil,math,json
F=lambda wt,s:ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{wt}.otf",max(6,int(s)))
def out_back(q,k=2.2):
    q=min(max(q,0),1);q-=1;return 1+q*q*((k+1)*q+k)
CW,CH=900,300;FPS=30;START=29.6;DUR=33.567-START
d="cards/end";shutil.rmtree(d,ignore_errors=True);os.makedirs(d)
L=["Снимать рилсы сложнее,","чем делать сайты с нейросетью"]
for i in range(int(round(DUR*FPS))):
    t=i/FPS;c=Image.new("RGBA",(CW,CH),(0,0,0,0))
    sc=out_back(t/0.45);
    b=Image.new("RGBA",(CW,CH),(0,0,0,0));dr=ImageDraw.Draw(b)
    dr.rounded_rectangle((20,20,CW-20,CH-20),radius=48,fill=(255,255,255,245))
    dr.text((CW/2,115),L[0],font=F("ExtraBold",46),fill=(22,22,27,255),anchor="mm")
    dr.text((CW/2,190),L[1],font=F("ExtraBold",46),fill=(255,79,154,255),anchor="mm")
    if sc>0.01:
        b=b.resize((max(1,int(CW*sc)),max(1,int(CH*sc))),Image.LANCZOS)
        if b.width<=CW: c.alpha_composite(b,((CW-b.width)//2,(CH-b.height)//2))
        else: c=b.crop(((b.width-CW)//2,(b.height-CH)//2,(b.width-CW)//2+CW,(b.height-CH)//2+CH))
    c.save(f"{d}/{i+1:04d}.png")
o=json.load(open("overlays.json"));o=[x for x in o if "end" not in x["pattern"]]
o.append(dict(kind="seq",pattern="cards/end/%04d.png",start=START,dur=round(DUR,3),y=930,w=CW))
json.dump(o,open("overlays.json","w"))
