import json,os,math
from PIL import Image,ImageDraw,ImageFont,ImageFilter
A=json.load(open("aligned.json"))
from pieces import PIECES
starts=[0]
for f0,n,z in PIECES: starts.append(starts[-1]+n/30)
TOT=starts[-1]
def W_(word,after=None):
    for x in A:
        if x["w"]==word and (after is None or x["s"]>after): return x
    raise KeyError(word)
FD="/usr/share/fonts/opentype/inter/";F=lambda w,s:ImageFont.truetype(FD+f"Inter-{w}.otf",s)
Y=(255,212,0,255);WH=(255,255,255,255);MUT=(255,255,255,165);BG=(22,22,27,244)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def shadow(im,blur=22,off=10,alpha=110):
    w,h=im.size;pad=blur*2;out=Image.new("RGBA",(w+pad*2,h+pad*2),(0,0,0,0))
    sh=Image.new("RGBA",(w,h),(0,0,0,alpha));sh.putalpha(im.split()[3].point(lambda a:min(a,alpha)))
    out.paste(sh,(pad,pad+off));out=out.filter(ImageFilter.GaussianBlur(blur));out.alpha_composite(im,(pad,pad));return out
def finish(c,t,D):
    c=shadow(c);f=max(0,min(1,t/0.18,(D-t)/0.22));c.putalpha(c.split()[3].point(lambda v:int(v*f)));return c
def base(W,H):
    c=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(c);d.rounded_rectangle((0,0,W-1,H-1),radius=40,fill=BG,outline=(255,255,255,38),width=2);return c,d
OV=[]
def save_seq(name,start,D,fn,y,w):
    os.makedirs(f"cards/{name}",exist_ok=True)
    for i in range(int(D*30)+1): fn(i/30,D).save(f"cards/{name}/{i+1:04d}.png")
    OV.append(dict(kind="seq",pattern=f"cards/{name}/%04d.png",start=round(start,3),dur=round(D,3),y=y,w=w))
def lines_card(title,items,W=860,big=60,gap=88,check=False):
    H=96+gap*len(items)+20
    _d=ImageDraw.Draw(Image.new("L",(8,8)))
    room=(W-140-60) if check else (W-80)
    while big>30 and max(_d.textlength(t,font=F("ExtraBold",big)) for t,_ in items)>room: big-=2
    def fn(t,D):
        c,d=base(W,H);d.text((W/2,52),title,font=F("Bold",30),fill=MUT,anchor="mm")
        for k,(txt,t0) in enumerate(items):
            q=ease((t-t0)/0.26)
            if q<=0: continue
            y=96+gap*k+gap/2+int((1-q)*20)
            ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov);a=int(255*q)
            if check:
                od.ellipse((70,y-22,114,y+22),fill=(255,212,0,a));od.line([(80,y),(90,y+11),(106,y-11)],fill=(22,22,27,a),width=6)
                od.text((140,y),txt,font=F("ExtraBold",big),fill=(255,255,255,a),anchor="lm")
            else: od.text((W/2,y),txt,font=F("ExtraBold",big),fill=(255,212,0,a),anchor="mm")
            c.alpha_composite(ov)
        return finish(c,t,D)
    return fn
# 1 title: the trainer
t0=W_("тренажёр")["s"]-0.2; t1=starts[2]-0.15
def title_fn(t,D):
    W,H=860,250;c,d=base(W,H)
    d.text((W/2,50),"Мой сервис",font=F("Bold",30),fill=MUT,anchor="mm")
    d.text((W/2,122),"Тренажёр приёма пациентов",font=F("ExtraBold",48),fill=WH,anchor="mm")
    d.text((W/2,190),"для студентов-медиков",font=F("ExtraBold",44),fill=Y,anchor="mm")
    return finish(c,t,D)
save_seq("T",t0,t1-t0,title_fn,50,948)
# 2 stats
s0=W_("больше")["s"]-0.25;s1=W_("нравится.")["e"]+0.6
save_seq("S",s0,s1-s0,lines_card("Сервис по подписке",[("Больше 100 человек",0.25),("Платят за подписку",W_("подписку,")["s"]-0.35-s0),("Положительные отзывы",W_("отзывы,")["s"]-0.35-s0)],big=58,gap=86,check=True),50,948)
# 3 voice message
v0=W_("открыл")["s"]-0.2;v1=W_("голосовыми.")["e"]+0.5;vt=W_("надиктовал")["s"]-v0 if any(x["w"]=="надиктовал" for x in A) else 1.5
def voice_fn(t,D):
    W,H=860,250;c,d=base(W,H)
    d.ellipse((40,30,84,74),fill=(217,119,87,255));d.text((62,52),"*",font=F("ExtraBold",40),fill=WH,anchor="mm")
    d.text((102,52),"Нейросеть",font=F("Bold",30),fill=MUT,anchor="lm")
    q=ease((t-vt)/0.3)
    if q>0:
        bub=Image.new("RGBA",(W,H),(0,0,0,0));bd=ImageDraw.Draw(bub);a=int(255*q)
        bd.rounded_rectangle((40,104,W-40,206),radius=50,fill=(255,212,0,a))
        bd.ellipse((60,118,134,192),fill=(22,22,27,a))
        bd.rounded_rectangle((88,134,106,166),radius=9,fill=(255,212,0,a));bd.arc((80,140,114,176),0,180,fill=(255,212,0,a),width=4);bd.line([(97,176),(97,184)],fill=(255,212,0,a),width=4)
        for k in range(30):
            amp=0.35+0.65*abs(math.sin(k*1.7+t*9))*(0.6+0.4*math.sin(k*0.5))
            h=int(8+44*amp);x=160+k*19
            bd.rounded_rectangle((x,155-h//2,x+9,155+h//2),radius=4,fill=(22,22,27,a))
        c.alpha_composite(bub)
    return finish(c,t,D)
save_seq("V",v0,v1-v0,voice_fn,50,948)
# 4 checklist: what the AI did
k0=W_("технические")["s"]-0.3;k1=starts[9]-0.1
save_seq("K",k0,k1-k0,lines_card("Нейросеть сделала сама",[("Технические моменты",0.3),("Дизайн",W_("дизайн.")["s"]-0.3-k0),("Готовый результат",W_("готовый")["s"]-0.3-k0)],big=56,gap=86,check=True),50,948)
# 5 prompt typing
TXT="Я хочу сделать сайт для стоматологии"
p0=W_("«Я")["s"]-0.3;pend=W_("стоматологии».")["e"];bro=W_("Вы")["s"]-0.08
per=(pend-p0-0.35)/len(TXT)
def prompt_fn(t,D):
    W,H=900,230;c=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(c)
    d.rounded_rectangle((0,0,W-1,H-1),radius=40,fill=(255,255,255,255))
    d.ellipse((34,24,74,64),fill=(217,119,87,255));d.text((54,44),"*",font=F("ExtraBold",36),fill=WH,anchor="mm")
    d.text((90,44),"Нейросеть",font=F("Bold",28),fill=(112,118,132,255),anchor="lm")
    d.rounded_rectangle((26,88,W-26,H-26),radius=34,fill=(241,242,246,255),outline=(220,223,230,255),width=2)
    n=int(max(0,min(len(TXT),(t-0.25)/per)));txt=TXT[:n];f=F("SemiBold",36)
    d.text((56,152),txt or " ",font=f,fill=(21,23,28,255),anchor="lm")
    cx=56+d.textlength(txt,font=f)+3
    if n<len(TXT) or int(t*2.2)%2==0: d.rectangle((cx,128,cx+3,176),fill=(21,23,28,255))
    r=32;bx,by=W-26-48,152;d.ellipse((bx-r,by-r,bx+r,by+r),fill=(217,119,87,255) if n else (200,203,212,255))
    d.polygon([(bx,by-14),(bx-13,by+2),(bx-4,by+2),(bx-4,by+14),(bx+4,by+14),(bx+4,by+2),(bx+13,by+2)],fill=WH)
    return finish(c,t,D)
save_seq("P",p0,bro-p0+0.1,prompt_fn,50,988)
# 6 b-roll: dental site
b1=W_("проверите,")["e"]+0.15
OV.append(dict(kind="broll",pattern="dscrollx/%04d.jpg",start=round(bro,3),dur=round(b1-bro,3)))
# 7 price
c0=W_("25")["s"]-0.35;c1=W_("рублей.")["e"]+0.9
def price_fn(t,D):
    W,H=760,250;c,d=base(W,H)
    d.text((W/2,52),"Сайт для стоматологии",font=F("Bold",30),fill=MUT,anchor="mm")
    q=ease((t-0.35)/0.26)
    if q>0:
        ov=Image.new("RGBA",(W,H),(0,0,0,0));ImageDraw.Draw(ov).text((W/2,150+int((1-q)*20)),"от 25 000 ₽",font=F("ExtraBold",92),fill=(255,212,0,int(255*q)),anchor="mm");c.alpha_composite(ov)
    return finish(c,t,D)
save_seq("C",c0,c1-c0,price_fn,50,848)
# 8 list of orders
l0=W_("сайтам.")["s"]-0.35;l1=W_("статьям.")["e"]+0.8
save_seq("L",l0,l1-l0,lines_card("Можно брать заказы",[("Сайты",0.35),("Картинки",W_("картинкам,")["s"]-0.3-l0),("Рилсы",W_("рилсам,")["s"]-0.3-l0),("Статьи",W_("статьям.")["s"]-0.3-l0)],big=54,gap=74,check=True),50,948)
json.dump(OV,open("overlays.json","w"),ensure_ascii=False,indent=1)
for o in OV: print(o["kind"],o["pattern"].split("/")[1] if o["kind"]=="seq" else "broll",o["start"],o["dur"])
