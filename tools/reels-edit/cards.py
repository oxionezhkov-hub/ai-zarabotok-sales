from PIL import Image, ImageDraw, ImageFont
F="/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FB="/usr/share/fonts/opentype/inter/Inter-Bold.otf"
Y=(255,212,0,255); WH=(255,255,255,255); DK=(24,24,28,238)
def f(p,s): return ImageFont.truetype(p,s)
def card(w,h): 
    im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,w-1,h-1),radius=44,fill=DK,outline=(255,255,255,40),width=2); return im,d
def ctext(d,xy,t,font,fill): d.text(xy,t,font=font,fill=fill,anchor="mm")
# A: prompt
im,d=card(940,190)
d.ellipse((44,62,110,128),fill=(217,119,87,255)); ctext(d,(77,95),"✻" if False else "*",f(F,64),WH)
d.text((136,95),"Сделай сайт для салона красоты",font=f(F,43),fill=WH,anchor="lm")
d.rounded_rectangle((44,150,896,156),radius=3,fill=(255,255,255,30))
im.save("build/cardA.png")
# B: button colour
im,d=card(940,300)
d.text((470,56),"Поменяй цвет кнопки",font=f(FB,40),fill=(255,255,255,200),anchor="mm")
d.rounded_rectangle((70,120,390,240),radius=60,fill=(255,105,180,255)); ctext(d,(230,180),"Записаться",f(F,40),WH)
d.polygon([(425,168),(500,168),(500,146),(545,180),(500,214),(500,192),(425,192)],fill=Y)
d.rounded_rectangle((550,120,870,240),radius=60,fill=(38,120,255,255)); ctext(d,(710,180),"Записаться",f(F,40),WH)
im.save("build/cardB.png")
# C: price
im,d=card(940,300)
ctext(d,(470,112),"25 · 40 · 60 тыс. ₽",f(F,96),Y)
ctext(d,(470,214),"за один сайт для салона красоты",f(FB,40),(255,255,255,215))
im.save("build/cardC.png")
# D: comment
im,d=card(940,200)
d.rounded_rectangle((52,48,172,128),radius=26,fill=Y); d.polygon([(80,120),(80,160),(118,126)],fill=Y)
for k in range(3): d.ellipse((78+k*30,80,94+k*30,96),fill=(24,24,28,255))
d.text((206,92),"Напишите в комментариях",font=f(F,46),fill=WH,anchor="lm")
d.text((206,146),"интересно будет обсудить",font=f(FB,30),fill=(255,255,255,170),anchor="lm")
im.save("build/cardD.png")
print("ok")
