import json
from cardlib import *
ov=json.load(open("overlays.json"));ov=[o for o in ov if "hours" not in o["pattern"]]
h0=W_("тратят")["s"]-0.25;h1=TOT-0.05
save_seq("hours",h0,h1-h0,lines_card("Времени на сайт",[("1–2 часа",0.35)],W=620,big=86,gap=110,icon="none"))
k0=0.25;k1=W_("попросить")["s"]-0.3
save_seq("hook",k0,k1-k0,lines_card("Первый заказ на сайт",[("Карты: бизнес без сайта",W_("карты,")["s"]-0.3-k0)],icon="pin"))
json.dump(ov+OV,open("overlays.json","w"),ensure_ascii=False,indent=1);print(OV)
