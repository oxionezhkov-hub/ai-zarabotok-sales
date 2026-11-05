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
BOTTOM=1365   # cards sit on the t-shirt, above the subtitles (face is in the upper part of this shot)
def save_seq(name,start,D,fn,top=None):
    d=f"cards/{name}"
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d)
    for i in range(int(D*30)+1): fr=fn(i/30,D);fr.save(f"{d}/{i+1:04d}.png")
    P=int(max(fr.size)/(1+2*PADF)*PADF)
    y=BOTTOM-(fr.size[1]-P) if top is None else top-P
    OV.append(dict(kind="seq",pattern=f"{d}/%04d.png",start=round(start,3),dur=round(D,3),y=y,w=fr.size[0]))
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

def prompt_card(TXT,t_type0,t_type1):
    per=(t_type1-t_type0)/len(TXT)
    def fn(t,D):
        W,H=900,230;c=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(c)
        d.rounded_rectangle((0,0,W-1,H-1),radius=40,fill=(255,255,255,255))
        d.ellipse((34,24,74,64),fill=(217,119,87,255));d.text((54,44),"*",font=F("ExtraBold",36),fill=WH+(255,),anchor="mm")
        d.text((90,44),"Нейросеть",font=F("Bold",28),fill=(112,118,132,255),anchor="lm")
        d.rounded_rectangle((26,88,W-26,H-26),radius=34,fill=(241,242,246,255),outline=(220,223,230,255),width=2)
        n=int(max(0,min(len(TXT),(t-t_type0)/per)));txt=TXT[:n];f=F("SemiBold",38)
        d.text((56,152),txt or " ",font=f,fill=(21,23,28,255),anchor="lm")
        cx=56+d.textlength(txt,font=f)+3
        if n<len(TXT) or int(t*2.2)%2==0: d.rectangle((cx,128,cx+3,176),fill=(21,23,28,255))
        sent=t>t_type1+0.2;bs=0.82 if t_type1+0.1<t<t_type1+0.25 else 1.0
        r=32*bs;bx,by=W-26-48,152;d.ellipse((bx-r,by-r,bx+r,by+r),fill=(217,119,87,255) if n else (200,203,212,255))
        d.polygon([(bx,by-14*bs),(bx-13*bs,by+2*bs),(bx-4*bs,by+2*bs),(bx-4*bs,by+14*bs),(bx+4*bs,by+14*bs),(bx+4*bs,by+2*bs),(bx+13*bs,by+2*bs)],fill=WH+(255,))
        return finish(c,t,D)
    return fn
pieces_end=[starts[i+1] for i in range(len(PIECES))]
# 1 the friend's question
q1=W_("начать?")["e"]+0.4
save_seq("question",0.15,q1-0.15,chat_card("Твой вопрос",[("Как заработать на нейросетях?",0.15),("С чего начать?",W_("чего")["s"]-0.4-0.15)]))
# 2 step 1: one direction
a0=W_("направление,")["s"]-0.6;a1=W_("угодно.")["e"]+0.5
save_seq("step1",a0,a1-a0,lines_card("Шаг 1. Выбери одно направление",[("Сайты",W_("сайты")["s"]-0.3-a0),("Картинки",W_("картинки,")["s"]-0.3-a0),("Тексты и статьи",W_("тексты,")["s"]-0.3-a0)],icon="check"))
# 3 step 2: the AI
b0=W_("зарегистрироваться")["s"]-0.3;b1=W_("попросить")["s"]
save_seq("step2",b0,b1-b0,lines_card("Шаг 2. Зарегистрируйся в нейросети",[("Claude",W_("Клоде,")["s"]-0.3-b0),("ChatGPT",W_("ChatGPT,")["s"]-0.3-b0)],icon="check"))
# 4 the prompt
TXT="Сделай сайт для стоматологии";p0=W_("попросить")["s"]-0.1;ts0=W_("сделай")["s"]-p0;ts1=W_("стоматологии.")["e"]-p0
pe=W_("Через")["s"]-0.1
save_seq("prompt",p0,pe-p0,prompt_card(TXT,ts0,ts1))
# 5 b-roll: the dental example site while "через 10-20 минут ... первая наработка"
br0=pe;br1=W_("наработка.")["e"]+0.2
OV.append(dict(kind="broll",pattern="dscrollx/%04d.jpg",start=round(br0,3),dur=round(br1-br0,3)))
# 6 step 3: find a client
c0=W_("знакомым.")["s"]-0.9;c1=W_("сайта.",after=40)["e"]+0.4
save_seq("step3",c0,c1-c0,lines_card("Шаг 3. Найди клиента",[("Знакомые",W_("знакомым.")["s"]-0.3-c0),("Карты: бизнес без сайта",W_("карты,")["s"]-0.3-c0)],icon="pin"))
# 7 the offer
o0=W_("купить")["s"]-0.7;o1=W_("оплатить.")["e"]+0.4
save_seq("offer",o0,o1-o0,lines_card("Что предложить бизнесу",[("Купить готовый сайт",W_("купить")["s"]-0.3-o0),("Или доработать и оплатить",W_("доработать")["s"]-0.3-o0)],icon="num"))
# 8 prices counting up
r0=W_("20,",after=W_("зарабатывают")["s"])["s"]-0.35;r1=W_("рублей")["e"]+0.7
save_seq("price",r0,r1-r0,lines_card("Знакомые берут за один сайт",[("20 000 ₽",0.35),("30 000 ₽",W_("30,",after=W_("зарабатывают")["s"])["s"]-r0),("40 000 ₽",W_("40",after=W_("зарабатывают")["s"])["s"]-r0)],W=720,big=80,gap=90,icon="none",count=True))
# 9 time spent
h0=W_("час,")["s"]-0.35;h1=W_("больше.")["e"]+0.5
save_seq("hours",h0,h1-h0,lines_card("Времени на сайт",[("1–2 часа",0.35)],W=620,big=86,gap=110,icon="none"))
# 10 where to find orders
f0_=W_("Telegram-чатах,")["s"]-0.6;f1_=W_("знакомых.",after=W_("Telegram-чатах,")["s"])["e"]+0.5
save_seq("where",f0_,f1_-f0_,lines_card("Где искать заказы",[("Telegram-чаты",W_("Telegram-чатах,")["s"]-0.3-f0_),("Фриланс-биржи",W_("фриланс-биржах,")["s"]-0.3-f0_),("Знакомые",W_("знакомых.",after=W_("Telegram-чатах,")["s"])["s"]-0.3-f0_)],icon="check"))
json.dump(OV,open("overlays.json","w"),ensure_ascii=False,indent=1)
for o in OV: print(o["kind"],o["pattern"].split("/")[-2],o["start"],o["dur"],o.get("y"))
