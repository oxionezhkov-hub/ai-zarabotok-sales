import math
from PIL import Image,ImageDraw,ImageFont,ImageFilter
FD="/usr/share/fonts/opentype/inter/"
def F(w,s): return ImageFont.truetype(FD+f"Inter-{w}.otf",s)
INK=(21,23,28,255);MUT=(112,118,132,255);WH=(255,255,255,255)
def rr_mask(w,h,r):
    m=Image.new("L",(w,h),0);ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255);return m
def shadow(im,blur=26,off=14,alpha=90):
    w,h=im.size;pad=blur*2;out=Image.new("RGBA",(w+pad*2,h+pad*2),(0,0,0,0))
    sh=Image.new("RGBA",(w,h),(0,0,0,alpha));sh.putalpha(Image.eval(im.split()[3],lambda a:min(a,alpha)))
    out.paste(sh,(pad,pad+off));out=out.filter(ImageFilter.GaussianBlur(blur));out.alpha_composite(im,(pad,pad));return out
def fade(im,f): 
    a=im.split()[3].point(lambda v:int(v*f));im=im.copy();im.putalpha(a);return im
def env(t,d,i=0.15,o=0.2): return min(1,t/i,(d-t)/o) if True else 1
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
# ============ Card A: prompt typing ============
TXT="Сделай сайт для салона красоты"
def cardA(t,D=3.4):
    W,H=900,300
    c=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(c)
    d.rounded_rectangle((0,0,W-1,H-1),radius=40,fill=(255,255,255,255))
    d.ellipse((34,30,78,74),fill=(217,119,87,255));d.text((56,52),"✻",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",28),fill=WH,anchor="mm")
    d.text((96,52),"Нейросеть",font=F("Bold",30),fill=MUT,anchor="lm")
    # input
    d.rounded_rectangle((30,100,W-30,H-34),radius=36,fill=(241,242,246,255),outline=(220,223,230,255),width=2)
    t0,per=0.25,0.055
    n=int(max(0,min(len(TXT),(t-t0)/per)))
    sent=t>=2.2
    txt=TXT[:n] if not sent else ""
    f=F("SemiBold",40)
    if not sent:
        d.text((62,176),txt if txt else " ",font=f,fill=INK,anchor="lm")
        if n==0: d.text((62,176),"Опишите, что нужно сделать",font=f,fill=(160,165,178,255),anchor="lm") if (t<t0) else None
        cx=62+d.textlength(txt,font=f)+3
        if int(t*2.2)%2==0 or n<len(TXT): d.rectangle((cx,150,cx+3,204),fill=INK)
    # send button
    scl=0.88 if 2.1<=t<2.3 else 1.0
    r=int(36*scl);cx,cy=W-30-52,176
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(217,119,87,255) if n>0 or sent else (200,203,212,255))
    d.polygon([(cx,cy-16),(cx-15,cy+2),(cx-5,cy+2),(cx-5,cy+16),(cx+5,cy+16),(cx+5,cy+2),(cx+15,cy+2)],fill=WH)
    if sent:
        dots="."*(1+int((t-2.2)*4)%3)
        d.text((62,176),"Создаю сайт"+dots,font=f,fill=INK,anchor="lm")
        p=ease((t-2.3)/1.0)
        d.rounded_rectangle((62,222,62+int((W-124)*0.0+ (W-250)*p),232),radius=5,fill=(217,119,87,255))
        d.rounded_rectangle((62,222,W-188,232),radius=5,outline=(215,218,226,255),width=2)
    c=shadow(c)
    return fade(c,env(t,D))
for i in range(0): cardA(i/30).save(f"build/A/{i+1:04d}.png")
# ============ Card B: browser + button colour ============
def cursor(d,x,y,s=1.0):
    pts=[(0,0),(0,34),(9,26),(15,40),(22,37),(16,24),(28,24)]
    P=[(x+px*s*1.3,y+py*s*1.3) for px,py in pts]
    d.polygon([(a+2,b+3) for a,b in P],fill=(0,0,0,70))
    d.polygon(P,fill=(255,255,255,255),outline=(20,20,24,255))
CW=760
def cardB(i,D=3.6):
    t=i/30
    src=Image.open(f"site/hero/{min(i+1,110):04d}.png").convert("RGBA")   # 1080x1280
    crop=src.crop((0,200,1080,1280)).resize((CW,int(1080*CW/1080)),Image.LANCZOS)
    ch=62;H=ch+crop.height
    c=Image.new("RGBA",(CW,H),(0,0,0,0));d=ImageDraw.Draw(c)
    d.rounded_rectangle((0,0,CW-1,H-1),radius=30,fill=(238,239,243,255))
    for k,col in enumerate([(255,95,87),(254,188,46),(40,200,64)]): d.ellipse((24+k*30,22,42+k*30,40),fill=col+(255,))
    d.rounded_rectangle((130,12,CW-30,50),radius=19,fill=(255,255,255,255));d.text((160,31),"lotos-studio.ru",font=F("Medium",22),fill=MUT,anchor="lm")
    c.alpha_composite(crop,(0,ch))
    m=rr_mask(CW,H,30);mask=Image.new("L",(CW,H),0);mask.paste(m)
    a=c.split()[3];c.putalpha(Image.composite(a,Image.new("L",(CW,H),0),mask))
    d=ImageDraw.Draw(c)
    sc=CW/1080
    bx,by=127*2*sc,ch+(546*2-200)*sc    # button centre in card coords
    # chat chip
    if t>=0.2:
        f=F("SemiBold",28);txt="Поменяй цвет кнопки с розового на синий"
        w=int(d.textlength(txt,font=f))+60;cx0=(CW-w)//2
        q=ease((t-0.2)/0.25);y0=H-80+int((1-q)*20)
        chip=Image.new("RGBA",(w,64),(0,0,0,0));cd=ImageDraw.Draw(chip)
        cd.rounded_rectangle((0,0,w-1,63),radius=32,fill=(21,23,28,255));cd.text((w/2,32),txt,font=f,fill=WH,anchor="mm")
        c.alpha_composite(fade(chip,q),(cx0,y0))
    # cursor path: from right-bottom to button, click at 1.25
    p=ease((t-0.45)/0.8);sx,sy=bx+260,by+170
    cxp=sx+(bx+34-sx)*p;cyp=sy+(by+8-sy)*p
    if t>=0.45: cursor(d,cxp,cyp,0.62 if 1.25<=t<1.4 else 0.7)
    # ripple
    if 1.25<=t<1.75:
        rr=(t-1.25)/0.5;rad=int(18+90*rr);al=int(200*(1-rr))
        ov=Image.new("RGBA",c.size,(0,0,0,0));od=ImageDraw.Draw(ov);od.ellipse((bx+34-rad,by+8-rad,bx+34+rad,by+8+rad),outline=(255,255,255,al),width=6);c.alpha_composite(ov)
    c=shadow(c,blur=30,off=18,alpha=110)
    return fade(c,env(t,D))
for i in range(108): cardB(i).save(f"build/B/{i+1:04d}.png")
# ============ Card D: comments (static) ============
def cardD():
    W,H=900,300
    c=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(c)
    d.rounded_rectangle((0,0,W-1,H-1),radius=40,fill=(24,24,28,246),outline=(255,255,255,40),width=2)
    d.rounded_rectangle((44,46,164,126),radius=26,fill=(255,212,0,255));d.polygon([(72,118),(72,158),(110,124)],fill=(255,212,0,255))
    for k in range(3): d.ellipse((70+k*30,78,86+k*30,94),fill=(24,24,28,255))
    d.text((200,86),"Напишите в комментариях",font=F("ExtraBold",44),fill=WH,anchor="lm")
    f=F("Medium",31);lines=["Пользовались нейросетью, но не просили","сделать подобные задачи?"]
    for k,l in enumerate(lines): d.text((46,180+k*44),l,font=f,fill=(255,255,255,215),anchor="lm")
    return shadow(c,blur=20,off=10,alpha=120)
cardD().save("build/cardD2.png")
# ============ B-roll: scrolling site, chip baked in ============
chipf=F("Bold",30);txt="Пример: сайт для салона красоты"
tmp=Image.new("RGBA",(10,10));w=int(ImageDraw.Draw(tmp).textlength(txt,font=chipf))+56
chip=Image.new("RGBA",(w,64),(0,0,0,0));cd=ImageDraw.Draw(chip);cd.rounded_rectangle((0,0,w-1,63),radius=32,fill=(21,23,28,230));cd.text((w/2,32),txt,font=chipf,fill=WH,anchor="mm")
for i in range(150):
    im=Image.open(f"site/scroll/{i+1:04d}.jpg").convert("RGBA");im.alpha_composite(chip,(40,150));im.convert("RGB").save(f"build/scrollx/{i+1:04d}.jpg",quality=90)
print("cards ok")
