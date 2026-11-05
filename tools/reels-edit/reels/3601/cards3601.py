import json,os,math
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
_d=ImageDraw.Draw(Image.new("L",(8,8)))
OV=[]
def save_seq(name,start,D,fn,y=40,w=948):
    os.makedirs(f"cards/{name}",exist_ok=True)
    for i in range(int(D*30)+1): fn(i/30,D).save(f"cards/{name}/{i+1:04d}.png")
    OV.append(dict(kind="seq",pattern=f"cards/{name}/%04d.png",start=round(start,3),dur=round(D,3),y=y,w=w))
def lines_card(title,items,W=860,big=56,gap=82,icon="check"):
    H=96+gap*len(items)+20
    room=W-200
    while big>30 and max(_d.textlength(t,font=F("ExtraBold",big)) for t,_ in items)>room: big-=2
    def fn(t,D):
        c,d=base(W,H);d.text((W/2,52),title,font=F("Bold",30),fill=MUT,anchor="mm")
        for k,(txt,t0) in enumerate(items):
            q=ease((t-t0)/0.26)
            if q<=0: continue
            y=96+gap*k+gap/2+int((1-q)*20);ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov);a=int(255*q)
            if icon=="check":
                od.ellipse((70,y-22,114,y+22),fill=(255,212,0,a));od.line([(80,y),(90,y+11),(106,y-11)],fill=(22,22,27,a),width=6)
            elif icon=="pin":
                od.ellipse((72,y-26,112,y+10),fill=(255,90,80,a));od.polygon([(76,y-4),(108,y-4),(92,y+24)],fill=(255,90,80,a));od.ellipse((85,y-15,99,y-1),fill=(22,22,27,a))
            elif icon=="num":
                od.ellipse((70,y-22,114,y+22),fill=(255,212,0,a));od.text((92,y),str(k+1),font=F("ExtraBold",28),fill=(22,22,27,a),anchor="mm")
            if icon=="none": od.text((W/2,y),txt,font=F("ExtraBold",big),fill=(255,212,0,a),anchor="mm")
            else: od.text((140,y),txt,font=F("ExtraBold",big),fill=(255,255,255,a),anchor="lm")
            c.alpha_composite(ov)
        return finish(c,t,D)
    return fn
def chat_card(title,msgs,W=860,mine=False):
    H=100+76*len(msgs)+16
    def fn(t,D):
        c,d=base(W,H)
        for k in range(3): d.ellipse((40+k*26,32,76+k*26,68),fill=[(255,150,120,255),(120,190,255,255),(150,220,150,255)][k],outline=BG,width=3)
        d.text((136,50),title,font=F("Bold",30),fill=MUT,anchor="lm")
        for k,(txt,t0) in enumerate(msgs):
            q=ease((t-t0)/0.22)
            if q<=0: continue
            f=F("Bold",36);tw=int(_d.textlength(txt,font=f))+56;y=100+76*k+int((1-q)*18)
            ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov);a=int(255*q)
            od.rounded_rectangle((40,y,40+tw,y+62),radius=26,fill=(242,243,246,a))
            od.text((68,y+31),txt,font=f,fill=(21,23,28,a),anchor="lm");c.alpha_composite(ov)
        return finish(c,t,D)
    return fn
# 1 chat with customer requests
c0=W_("сайт,")["s"]-1.45;c1=W_("угодно.")["e"]+0.6
msgs=[("Нужен сайт",W_("сайт,")["s"]-0.45-c0),("Нужна картинка для поста",W_("картинка")["s"]-0.45-c0),("Нужны ролики",W_("ролики,")["s"]-0.45-c0),("Нужны статьи",W_("статьи,")["s"]-0.45-c0)]
save_seq("chat",c0,c1-c0,chat_card("Чат заказчиков в Telegram",msgs))
# 2 maps of the city
m0=W_("карту")["s"]-0.3;m1=starts[9]-0.1
save_seq("maps",m0,m1-m0,lines_card("Карты вашего города: есть ли сайт?",[("Салоны красоты",W_("салонов")["s"]-0.3-m0),("Мастерские",W_("мастерских,")["s"]-0.3-m0),("Стоматологии",W_("стоматологий,")["s"]-0.3-m0)],icon="pin"))
# 3 b-roll: example site while he says "create a draft site in 5 minutes"
OV.append(dict(kind="broll",pattern="../build/scrollx/%04d.jpg",start=round(starts[9],3),dur=round(starts[10]-starts[9],3)))
# 4 steps: call, offer, ask payment
s0=starts[10]-0.05;s1=W_("оплату.")["e"]+0.35
save_seq("steps",s0,s1-s0,lines_card("Дальше",[("Позвонить по номеру с карт",0.1),("Предложить решение",W_("предложить")["s"]-0.3-s0),("Попросить оплату",W_("попросив")["s"]-0.3-s0)],icon="num"))
# 5 prices on separate lines
p0=55.79-0.35;p1=58.09+0.9
save_seq("price",p0,p1-p0,lines_card("В среднем платят за сайт",[("20 000 ₽",0.35),("30 000 ₽",56.36-p0),("40 000 ₽",56.84-p0)],W=720,big=82,gap=92,icon="none"),w=808)
# 6 DMs
d0=W_("личные")["s"]-0.3;d1=W_("решение.")["e"]+0.6
save_seq("dm",d0,d1-d0,chat_card("Мне пишут в личку",[("Помоги разобраться",W_("разобраться")["s"]-0.45-d0),("Сделай сервис",W_("сервис,")["s"]-0.45-d0),("Нужно решение",W_("решение.")["s"]-0.45-d0)]))
# 7 CTA
e0=W_("Если",after=70)["s"]-0.1;e1=TOT
def cta_fn(t,D):
    W,H=860,210;c,d=base(W,H)
    d.rounded_rectangle((44,46,164,126),radius=26,fill=Y);d.polygon([(72,118),(72,158),(110,124)],fill=Y)
    for k in range(3): d.ellipse((70+k*30,78,86+k*30,94),fill=(24,24,28,255))
    d.text((200,84),"Напишите в комментариях",font=F("ExtraBold",42),fill=WH,anchor="lm")
    d.text((200,140),"или мне в директ",font=F("Bold",34),fill=Y,anchor="lm")
    return finish(c,t,D)
save_seq("cta",e0,e1-e0,cta_fn)
json.dump(OV,open("overlays.json","w"),ensure_ascii=False,indent=1)
for o in OV: print(o["kind"],o["pattern"].split("/")[-2],o["start"],o["dur"])
