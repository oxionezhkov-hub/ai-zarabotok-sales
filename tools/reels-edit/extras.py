import numpy as np, wave, json
from pieces import PIECES
SR=48000
dur=sum(b-a for a,b,z in PIECES)+1.0
N=int(SR*dur); t=np.arange(N)/SR
rng=np.random.default_rng(3)
# ---- music: soft pad, Am - F - C - G, 8 s per chord
chords=[(110.0,164.81,220.0,261.63),(87.31,174.61,220.0,261.63),(130.81,196.0,261.63,329.63),(98.0,196.0,246.94,293.66)]
mus=np.zeros(N)
seg=8.0
for k in range(int(dur/seg)+2):
    f=chords[k%4]; t0=k*seg
    env=np.clip((t-t0)/3.0,0,1)*np.clip((t0+seg+3.0-t)/3.0,0,1)
    env=np.where((t>=t0)&(t<t0+seg+3.0),env,0)
    for fr in f:
        for dt in (-0.4,0.4):
            mus+=env*np.sin(2*np.pi*(fr+dt)*t)*0.25
mus*=0.6+0.4*np.sin(2*np.pi*0.12*t)
# soft lowpass via moving average
ker=np.ones(24)/24; mus=np.convolve(mus,ker,mode="same")
mus/=np.max(np.abs(mus)); 
fade=np.clip(t/2.0,0,1)*np.clip((dur-t)/2.5,0,1); mus*=fade
# target about -36 dBFS rms
mus*=10**(-36/20)/np.sqrt(np.mean(mus**2))
# ---- sfx
sfx=np.zeros(N)
def add(buf,t0,x,g):
    i=int(t0*SR); j=min(N,i+len(x)); buf[i:j]+=x[:j-i]*g
def pop(freq=880,L=0.22):
    tt=np.arange(int(SR*L))/SR; f=freq*(1+0.5*np.exp(-tt*30))
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*18)
def whoosh(L=0.28):
    tt=np.arange(int(SR*L))/SR; n=rng.standard_normal(len(tt))
    n=np.convolve(n,np.ones(40)/40,mode="same")  # darker noise
    return n*np.sin(np.pi*tt/L)**2
A=json.load(open("build/aligned.json"))
def tw(word): 
    for x in A:
        if x["w"]==word: return x["s"]
cuts=[];c=0
for a,b,z in PIECES[:-1]:
    c+=b-a; cuts.append(c)
for c in cuts: add(sfx,c-0.06,whoosh(),0.10)
cards={"A":tw("сделай"),"B":tw("поменяй"),"C":tw("25,")-0.2,"D":tw("напишите")}
for k,tt in cards.items(): add(sfx,tt,pop(),0.20)
sfx*=1.0
json.dump(cards,open("build/cards_t.json","w"))
st=np.stack([mus,mus],axis=1)
st=np.clip(st,-1,1)
with wave.open("build/music.wav","wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((st*32767).astype(np.int16).tobytes())
print("dur",dur,"cards",cards,"cuts",[round(x,2) for x in cuts])
