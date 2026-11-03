import json,subprocess,numpy as np,wave
from pieces import PIECES
SR=48000
A=json.load(open("build/aligned.json"))
def tw(word):
    for x in A:
        if x["w"].lower().strip(",.:?") == word: return x["s"]
    raise KeyError(word)
total=sum(b-a for a,b,z in PIECES);N=int(SR*(total+1.0))
rng=np.random.default_rng(11)
def db(g): return 10**(g/20)
def norm(x): return x/(np.max(np.abs(x))+1e-9)
def lowpass_sweep(x,f0,f1):
    n=len(x);fc=f0*(f1/f0)**(np.arange(n)/n);a=1-np.exp(-2*np.pi*fc/SR);y=np.zeros(n);p=0.0
    for i in range(n): p+=a[i]*(x[i]-p);y[i]=p
    return y
def swipe(L=0.34,up=True,seed=0):
    r=np.random.default_rng(seed);t=np.arange(int(SR*L))/SR;x=r.standard_normal(len(t))
    y=lowpass_sweep(x,350,5200) if up else lowpass_sweep(x,5200,350)
    y-=lowpass_sweep(y,120,120)*0.0
    hp=y-np.convolve(y,np.ones(60)/60,mode="same")           # roll off low rumble
    env=np.sin(np.pi*np.clip(t/L,0,1))**2.2
    glide=np.sin(2*np.pi*np.cumsum(500+900*(t/L if up else 1-t/L))/SR)*0.06
    return norm((hp*env)+glide*env)
def click():
    t=np.arange(int(SR*0.12))/SR
    tick=(np.random.default_rng(2).standard_normal(len(t)))*np.exp(-t*900)
    tick=tick-np.convolve(tick,np.ones(14)/14,mode="same")
    tock=np.sin(2*np.pi*np.cumsum(1100*np.exp(-t*30)+260)/SR)*np.exp(-t*45)
    return norm(0.55*tick/ (np.max(np.abs(tick))+1e-9)+0.9*tock)
def bell(f,L=1.1,dec=4.2):
    t=np.arange(int(SR*L))/SR;y=np.zeros_like(t)
    for r,a in ((1,1),(2.01,.38),(3.02,.18),(4.21,.08)): y+=a*np.sin(2*np.pi*f*r*t)*np.exp(-t*dec*(1+0.3*(r-1)))
    return y*np.minimum(t/0.003,1)
def pay():
    y=np.zeros(int(SR*1.3))
    for k,(f,off,g) in enumerate(((1046.5,0.0,1.0),(1318.5,0.075,0.9),(1568.0,0.15,0.85),(2093.0,0.24,0.6))):
        b=bell(f)*g;i=int(off*SR);y[i:i+len(b)]+=b[:len(y)-i]
    th=np.sin(2*np.pi*70*np.arange(int(SR*0.12))/SR)*np.exp(-np.arange(int(SR*0.12))/SR*35)
    y[:len(th)]+=th*0.6
    return norm(y)
def load(fn,t0,t1):
    x=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",fn,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,dtype=np.float32).copy()
    x=x[int(t0*SR):int(t1*SR)];x/=np.max(np.abs(x))+1e-9
    n=int(0.2*SR);x[-n:]*=np.linspace(1,0,n);x[:int(0.01*SR)]*=np.linspace(0,1,int(0.01*SR));return x
typingA=load("sfx/typing_3.mp3",0.12,1.78)
typingD=load("sfx/typing_3.mp3",1.9,3.5)
L=np.zeros(N,dtype=np.float32);ev=[]
def put(t,x,g,name,kind,why,pk=0.0):
    i=int(max(0,t-pk)*SR);y=x*db(g);j=min(N,i+len(y));L[i:j]+=y[:j-i];ev.append(dict(t=round(t,2),kind=kind,name=name,why=why))
# cuts
c=0;sw=[swipe(0.34,True,1),swipe(0.30,False,2),swipe(0.36,True,3)]
for k,(a,b,z) in enumerate(PIECES[:-1],1):
    c+=b-a;put(c,sw[k%3],-19,"swipe","whoosh",f"склейка между кусками {k} и {k+1}",pk=0.16)
tA=tw("сделай")-0.05;tB=tw("поменяй")+0.65;tC=tw("25")-0.2 if False else None
for x in A:
    if x["w"].startswith("25"): tC=x["s"]-0.2;break
tD=tw("напишите")-0.05
put(tA+0.25,typingA,-21,"typing","typing","карточка с запросом: печатается «Сделай сайт для салона красоты»")
put(tB+1.25,click(),-15,"click","click","курсор нажимает кнопку, цвет меняется с розового на синий")
put(tC+0.2,pay(),-17,"payment","ding","карточка с ценой 25 · 40 · 60 тыс. ₽")
put(tD+0.1,typingD,-22,"typing","typing","карточка «Напишите в комментариях»")
ev.sort(key=lambda e:e["t"])
L=np.clip(L,-1,1);st=np.stack([L,L],axis=1)
for fn in ("build/sfx.wav","out/sfx_track.wav"):
    with wave.open(fn,"wb") as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes())
json.dump(dict(events=ev,cards=dict(A=tA,B=tB,C=tC,D=tD)),open("build/events2.json","w"),ensure_ascii=False,indent=1)
print({k:round(v,2) for k,v in dict(A=tA,B=tB,C=tC,D=tD).items()},len(ev),"events")
