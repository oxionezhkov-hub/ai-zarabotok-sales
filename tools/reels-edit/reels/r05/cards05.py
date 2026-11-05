import json,os,math,glob,shutil,functools
from PIL import Image,ImageDraw,ImageFont,ImageFilter
A=json.load(open("aligned.json"))
from pieces import PIECES
starts=[0]
for f0,n,z in PIECES: starts.append(starts[-1]+n/30)
TOT=starts[-1]
def W_(word,after=0.0):
    for x in A:
        if x["w"]==word and x["s"]>=after: return x
    raise KeyError(word)
FD="/usr/share/fonts/opentype/inter/"
@functools.lru_cache(None)
def F(w,s): return ImageFont.truetype(FD+f"Inter-{w}.otf",max(6,int(s)))
Y=(255,212,0);WH=(255,255,255);BG=(22,22,27,244)
def clamp(x): return max(0.0,min(1.0,x))
def ease(x): x=clamp(x);return x*x*(3-2*x)
def out_cubic(x): x=clamp(x);return 1-(1-x)**3
def out_back(x,k=1.9): x=clamp(x);c3=k+1;return 1+c3*(x-1)**3+k*(x-1)**2
def shadow(im,blur=22,off=10,alpha=110):
    w,h=im.size;pad=blur*2;out=Image.new("RGBA",(w+pad*2,h+pad*2),(0,0,0,0))
    sh=Image.new("RGBA",(w,h),(0,0,0,alpha));sh.putalpha(im.split()[3].point(lambda a:min(a,alpha)))
    out.paste(sh,(pad,pad+off));out=out.filter(ImageFilter.GaussianBlur(blur));out.alpha_composite(im,(pad,pad));return out
PADF=0.07
def finish(c,t,D):
    """Spring entrance (scale 0.8 -> overshoot -> 1, slide down), shrink + fade on exit; fixed canvas size."""
    c=shadow(c);w,h=c.size;P=int(max(w,h)*PADF);cw,ch=w+2*P,h+2*P
    s=0.80+0.20*out_back(t/0.38);dy=-46*(1-out_cubic(t/0.38));a=clamp(t/0.12)
    if t>D-0.24: q=clamp((t-(D-0.24))/0.24);s*=1-0.10*q;a*=1-q;dy+=-18*q
    sw,sh_=max(1,int(w*s)),max(1,int(h*s));im=c.resize((sw,sh_),Image.LANCZOS)
    if a<1: im.putalpha(im.split()[3].point(lambda v:int(v*a)))
    canvas=Image.new("RGBA",(cw,ch),(0,0,0,0));canvas.alpha_composite(im,((cw-sw)//2,int((ch-sh_)//2+dy)));return canvas
def base(W,H):
    c=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(c);d.rounded_rectangle((0,0,W-1,H-1),radius=40,fill=BG,outline=(255,255,255,38),width=2);return c,d
def pop(t,t0,dur=0.34): return out_back((t-t0)/dur,2.2)
_d=ImageDraw.Draw(Image.new("L",(8,8)))
OV=[]
def save_seq(name,start,D,fn,top=40):
    d=f"cards/{name}"
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d)
    for i in range(int(D*30)+1): fr=fn(i/30,D);fr.save(f"{d}/{i+1:04d}.png")
    P=int(max(fr.size)/(1+2*PADF)*PADF)
    OV.append(dict(kind="seq",pattern=f"{d}/%04d.png",start=round(start,3),dur=round(D,3),y=top-P,w=fr.size[0]))
def count_text(txt,q):
    digits="".join(ch for ch in txt if ch.isdigit())
    if not digits or q>=1: return txt
    v=int(int(digits)*q/1000)*1000;s=f"{v:,}".replace(","," ")
    return txt.replace(f"{int(digits):,}".replace(","," "),s)
def lines_card(title,items,W=860,big=56,gap=82,icon="check",count=False):
    H=96+gap*len(items)+20
    while big>30 and max(_d.textlength(t,font=F("ExtraBold",big)) for t,_ in items)>W-200: big-=2
    def fn(t,D):
        c,d=base(W,H);d.text((W/2,52),title,font=F("Bold",30),fill=(255,255,255,165),anchor="mm")
        for k,(txt,t0) in enumerate(items):
            if t<t0: continue
            sc=0.55+0.45*pop(t,t0);a=int(255*clamp((t-t0)/0.12));y=96+gap*k+gap/2
            ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov)
            if icon!="none":
                ic=1.0+0.35*max(0,1-(t-t0)/0.45)*math.sin(clamp((t-t0)/0.45)*math.pi)   # icon pulse
                r=22*sc*ic;cx=92
                if icon=="check":
                    od.ellipse((cx-r,y-r,cx+r,y+r),fill=Y+(a,));od.line([(cx-12*sc,y),(cx-2*sc,y+11*sc),(cx+14*sc,y-11*sc)],fill=(22,22,27,a),width=max(2,int(6*sc)))
                elif icon=="pin":
                    od.ellipse((cx-20*sc*ic,y-26*sc*ic,cx+20*sc*ic,y+10*sc*ic),fill=(255,90,80,a));od.polygon([(cx-16*sc*ic,y-4*sc),(cx+16*sc*ic,y-4*sc),(cx,y+24*sc*ic)],fill=(255,90,80,a));od.ellipse((cx-7*sc,y-15*sc,cx+7*sc,y-1*sc),fill=(22,22,27,a))
                elif icon=="x":
                    od.ellipse((cx-r,y-r,cx+r,y+r),fill=(120,120,128,a));q2=13*sc
                    od.line([(cx-q2,y-q2),(cx+q2,y+q2)],fill=(22,22,27,a),width=max(2,int(6*sc)));od.line([(cx-q2,y+q2),(cx+q2,y-q2)],fill=(22,22,27,a),width=max(2,int(6*sc)))
                elif icon=="num":
                    od.ellipse((cx-r,y-r,cx+r,y+r),fill=Y+(a,));od.text((cx,y),str(k+1),font=F("ExtraBold",28*sc),fill=(22,22,27,a),anchor="mm")
                od.text((140,y),txt,font=F("ExtraBold",big*sc),fill=((190,190,196) if icon=="x" else WH)+(a,),anchor="lm")
            else:
                shown=count_text(txt,clamp((t-t0)/0.45)) if count else txt
                od.text((W/2,y),shown,font=F("ExtraBold",big*sc),fill=Y+(a,),anchor="mm")
            c.alpha_composite(ov)
        return finish(c,t,D)
    return fn
def chat_card(title,msgs,W=860):
    H=100+76*len(msgs)+16
    def fn(t,D):
        c,d=base(W,H)
        for k in range(3): d.ellipse((40+k*26,32,76+k*26,68),fill=[(255,150,120,255),(120,190,255,255),(150,220,150,255)][k],outline=BG,width=3)
        d.text((136,50),title,font=F("Bold",30),fill=(255,255,255,165),anchor="lm")
        for k,(txt,t0) in enumerate(msgs):
            if t<t0: continue
            sc=0.5+0.5*pop(t,t0,0.30);a=int(255*clamp((t-t0)/0.10))
            f=F("Bold",36*sc);tw=_d.textlength(txt,font=F("Bold",36))+56;y=100+76*k
            bw,bh=tw*sc,62*sc;x0,y0=40,y+62-bh            # grows from bottom-left corner
            ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov)
            od.rounded_rectangle((x0,y0,x0+bw,y0+bh),radius=max(4,26*sc),fill=(242,243,246,a))
            od.text((x0+28*sc,y0+bh/2),txt,font=f,fill=(21,23,28,a),anchor="lm");c.alpha_composite(ov)
        return finish(c,t,D)
    return fn

b0=W_("десятки")["s"]-0.9;b1=W_("разработке,")["e"]+0.25
save_seq("before",b0,b1-b0,lines_card("Раньше, чтобы сделать сайт",[("Десятки курсов",W_("десятки")["s"]-0.3-b0),("Регистрации",W_("регистрироваться,")["s"]-0.3-b0),("Код, дизайн, разработка",W_("коде,")["s"]-0.3-b0)],icon="x"))
n0=W_("сейчас")["s"]-0.1;n1=W_("оплату.")["e"]+0.4
save_seq("now",n0,n1-n0,lines_card("Сейчас",[("Открыть нейросеть",W_("открыть")["s"]-0.3-n0),("Сказать, что нужно",W_("сказать,")["s"]-0.3-n0),("Получить оплату",W_("получить")["s"]-0.3-n0)],icon="check"))
l0=W_("сайтам.")["s"]-0.35;l1=W_("статьям.")["e"]+0.8
save_seq("orders",l0,l1-l0,lines_card("Можно брать заказы",[("Сайты",0.35),("Картинки",W_("картинкам,")["s"]-0.3-l0),("Рилсы",W_("рилсам,")["s"]-0.3-l0),("Статьи",W_("статьям.")["s"]-0.3-l0)],big=54,gap=74,icon="check"))
json.dump(OV,open("overlays.json","w"),ensure_ascii=False,indent=1)
for o in OV: print(o["pattern"].split("/")[-2],o["start"],o["dur"],o["y"])
