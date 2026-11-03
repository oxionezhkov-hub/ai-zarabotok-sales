import json,subprocess,numpy as np,wave,csv
SR=48000
ev=json.load(open("build/sfx_events.json"))
from pieces import PIECES
total=sum(b-a for a,b,z in PIECES)
N=int(SR*(total+1.0))
def load(fn,t0=0,t1=None):
    cmd=["ffmpeg","-v","error","-i","sfx/"+fn,"-f","f32le","-ac","1","-ar",str(SR),"-"]
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,dtype=np.float32).copy()
    x=x[int(t0*SR):int((t1 or len(x)/SR)*SR)]
    x/=np.max(np.abs(x))+1e-9
    return x
def fade_out(x,d): 
    n=int(d*SR); x[-n:]*=np.linspace(1,0,n); return x
def db(g): return 10**(g/20)
lib={
 "whoosh_a":(load("whoosh_3.mp3"),0.06,-19),
 "whoosh_b":(load("whoosh_2.mp3"),0.07,-19),
 "typing":(fade_out(load("typing_3.mp3",0.12,2.5),0.25),0.0,-23),
 "click":(load("click_3.mp3"),0.0,-17),
 "ding":(load("ding_1.mp3"),0.0,-16),
 "notify":(load("notify_1.mp3"),0.10,-18),
}
L=np.zeros(N,dtype=np.float32)
log=[];w=0
for e in ev:
    k=e["kind"]
    if k=="whoosh": key="whoosh_a" if w%2==0 else "whoosh_b"; w+=1
    else: key={"typing":"typing","click":"click","ding":"ding","notify":"notify"}[k]
    x,pk,g=lib[key]
    start=e["t"]-pk if k=="whoosh" else e["t"]
    i=int(max(0,start)*SR); y=x*db(g); j=min(N,i+len(y)); L[i:j]+=y[:j-i]
    log.append((e["id"],e["t"],k,key))
L=np.clip(L,-1,1)
st=np.stack([L,L],axis=1)
for fn in ("build/sfx.wav","out/sfx_track.wav"):
    with wave.open(fn,"wb") as wv:
        wv.setnchannels(2);wv.setsampwidth(2);wv.setframerate(SR);wv.writeframes((st*32767).astype(np.int16).tobytes())
print("ok",len(log))
