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
                elif icon=="num":
                    od.ellipse((cx-r,y-r,cx+r,y+r),fill=Y+(a,));od.text((cx,y),str(k+1),font=F("ExtraBold",28*sc),fill=(22,22,27,a),anchor="mm")
                od.text((140,y),txt,font=F("ExtraBold",big*sc),fill=WH+(a,),anchor="lm")
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
# 1 chat with customer requests
c0=W_("сайт,")["s"]-1.45;c1=W_("угодно.")["e"]+0.6
msgs=[("Нужен сайт",W_("сайт,")["s"]-0.45-c0),("Нужна картинка для поста",W_("картинка")["s"]-0.45-c0),("Нужны ролики",W_("ролики,")["s"]-0.45-c0),("Нужны статьи",W_("статьи,")["s"]-0.45-c0)]
save_seq("chat",c0,c1-c0,chat_card("Чат заказчиков в Telegram",msgs))
# 2 maps of the city
m0=W_("карту")["s"]-0.3;m1=W_("сайт.")["e"]+0.5
save_seq("maps",m0,m1-m0,lines_card("Карты вашего города: есть ли сайт?",[("Салоны красоты",W_("салонов")["s"]-0.3-m0),("Мастерские",W_("мастерских,")["s"]-0.3-m0),("Стоматологии",W_("стоматологий,")["s"]-0.3-m0)],icon="pin"))
# 3 b-roll: example site while he says "create a draft site in 5 minutes"
b0=W_("просто",after=W_("указан,")["s"] if any(x["w"]=="указан," for x in A) else 40)["s"]-0.15
OV.append(dict(kind="broll",pattern="../build/scrollx/%04d.jpg",start=round(b0,3),dur=round(W_("сайта,")["e"]+0.15-b0,3)))
# 4 steps: call, offer, ask payment
s0=W_("позвонить")["s"]-0.25;s1=W_("оплату.")["e"]+0.35
save_seq("steps",s0,s1-s0,lines_card("Дальше",[("Позвонить по номеру с карт",0.25),("Предложить решение",W_("предложить")["s"]-0.3-s0),("Попросить оплату",W_("попросив")["s"]-0.3-s0)],icon="num"))
# 5 prices on separate lines, counting up
p0=W_("20,")["s"]-0.35;p1=W_("рублей.")["e"]+0.9
save_seq("price",p0,p1-p0,lines_card("В среднем платят за сайт",[("20 000 ₽",0.35),("30 000 ₽",W_("30,")["s"]-p0),("40 000 ₽",W_("40")["s"]-p0)],W=720,big=82,gap=92,icon="none",count=True))
# 6 DMs
d0=W_("личные")["s"]-0.3;d1=W_("решение.")["e"]+0.6
save_seq("dm",d0,d1-d0,chat_card("Мне пишут в личку",[("Помоги разобраться",W_("разобраться")["s"]-0.45-d0),("Сделай сервис",W_("сервис,")["s"]-0.45-d0),("Нужно решение",W_("решение.")["s"]-0.45-d0)]))
# 7 CTA
e0=W_("Если",after=60)["s"]-0.1;e1=TOT
def cta_fn(t,D):
    W,H=860,210;c,d=base(W,H)
    b=1.0+0.08*math.sin(max(0,t-0.4)*5.0)*max(0,1-max(0,t-0.4)/2.5)     # gentle wobble of the icon
    cx,cy=104,88;r=60*b
    d.rounded_rectangle((cx-r,cy-40*b,cx+r,cy+40*b),radius=26,fill=Y+(255,));d.polygon([(cx-32*b,cy+30*b),(cx-32*b,cy+70*b),(cx+6*b,cy+36*b)],fill=Y+(255,))
    for k in range(3):
        on=int(((t*3.0)-k)%3<1)   # typing dots
        rr=8+3*on;d.ellipse((cx-30+k*30-rr,cy-rr,cx-30+k*30+rr,cy+rr),fill=(24,24,28,255))
    d.text((200,84),"Напишите в комментариях",font=F("ExtraBold",42),fill=WH+(255,),anchor="lm")
    d.text((200,140),"или мне в директ",font=F("Bold",34),fill=Y+(255,),anchor="lm")
    return finish(c,t,D)
save_seq("cta",e0,e1-e0,cta_fn)
json.dump(OV,open("overlays.json","w"),ensure_ascii=False,indent=1)
for o in OV: print(o["kind"],o["pattern"].split("/")[-2],o["start"],o["dur"],o.get("y"),o.get("w"))
