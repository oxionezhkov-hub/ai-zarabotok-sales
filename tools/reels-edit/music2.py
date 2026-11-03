import numpy as np, wave, sys
from pieces import PIECES
SR=48000; BPM=96; dur=sum(b-a for a,b,z in PIECES)+1.0
N=int(SR*dur); rng=np.random.default_rng(7)
beat=60/BPM; step=beat/2   # 8th note
def place(buf,t,x,g=1.0):
    i=int(t*SR)
    if i<0 or i>=len(buf): return
    j=min(len(buf),i+len(x)); buf[i:j]+=x[:j-i]*g
def sine(f,L,ph=0): t=np.arange(int(SR*L))/SR; return np.sin(2*np.pi*f*t+ph)
def lp(x,k): return np.convolve(x,np.ones(k)/k,mode="same")
# --- drum sounds
tk=np.arange(int(SR*0.28))/SR
kick=np.sin(2*np.pi*np.cumsum(45+95*np.exp(-tk*28))/SR)*np.exp(-tk*11)
kick+=0.25*np.sin(2*np.pi*1500*tk)*np.exp(-tk*400)
ts=np.arange(int(SR*0.22))/SR
snr=(lp(rng.standard_normal(len(ts)),2)-lp(rng.standard_normal(len(ts)),40))*np.exp(-ts*20)
snr=snr/np.max(np.abs(snr))+0.5*np.sin(2*np.pi*190*ts)*np.exp(-ts*30)
th=np.arange(int(SR*0.05))/SR
hat=(rng.standard_normal(len(th))-lp(rng.standard_normal(len(th)),6))*np.exp(-th*90)
hat/=np.max(np.abs(hat))
# --- keys (soft electric piano, two-op FM)
def ep(f,L=0.9):
    t=np.arange(int(SR*L))/SR
    mod=np.sin(2*np.pi*f*2*t)*np.exp(-t*7)*1.4
    x=np.sin(2*np.pi*f*t+mod)*np.exp(-t*3.2)+0.25*np.sin(2*np.pi*f*2*t)*np.exp(-t*6)
    a=np.minimum(t/0.004,1); return x*a
def bass(f,L=0.42):
    t=np.arange(int(SR*L))/SR
    x=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)
    return x*np.exp(-t*5.5)*np.minimum(t/0.006,1)
# chords C - G - Am - F, one bar each (4 beats)
roots=[130.81,98.0,110.0,87.31]
chords=[[261.63,329.63,392.0],[246.94,293.66,392.0],[261.63,329.63,440.0],[261.63,349.23,440.0]]
dr=np.zeros(N);ks=np.zeros(N);bs=np.zeros(N);kk=np.zeros(N)
nb=int(dur/beat)+4
for b in range(nb):
    bar=(b//4)%4;pos=b%4;t0=b*beat
    if pos in (0,2) or (pos==3 and bar%2==1): 
        place(dr,t0,kick,0.9);place(kk,t0,np.ones(int(SR*0.12)),1.0)
    if pos in (1,3): place(dr,t0,snr,0.55)
    for s in (0,1):
        sw=0.018 if s==1 else 0
        place(dr,t0+s*step+sw,hat,0.28 if s==0 else 0.42)
    # bass: root on 1, fifth-ish pickup
    if pos==0: place(bs,t0,bass(roots[bar]),0.9)
    if pos==2: place(bs,t0+step,bass(roots[bar]*1.5 if bar%2==0 else roots[bar]),0.7)
    if pos==3 and bar in (1,3): place(bs,t0+step,bass(roots[bar]*2),0.5)
    # keys on the off-beats (syncopated)
    if pos in (0,2):
        for f in chords[bar]: place(ks,t0+step*1.0+0.01*rng.random(),ep(f),0.22)
    if pos==3: 
        for f in chords[bar]: place(ks,t0+step*0.0+0.02,ep(f*2,0.5),0.07)
# duck keys+bass under kick
duck=1-0.45*lp(kk,int(SR*0.09));duck=np.clip(duck,0.55,1)
mix=dr*0.85+(bs*1.0+ks*1.0)*duck
# gentle lowpass for warmth + fades
mix=lp(mix,3)
t=np.arange(N)/SR
fade=np.clip(t/1.2,0,1)*np.clip((dur-t)/2.5,0,1);mix*=fade
mix*=10**(-31/20)/np.sqrt(np.mean(mix**2))
mix=np.clip(mix,-0.95,0.95)
st=np.stack([mix,mix],axis=1)
with wave.open("build/music.wav","wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes())
print("music ok",round(dur,1))
