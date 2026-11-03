"""Проверка стыков: каждая граница куска должна стоять в тишине.
Запуск: python3 check_cuts.py audio/XXXX.wav  (читает pieces.py: первый кадр, число кадров, масштаб)
Флаг START/END значит: точка резки попала в звук, слово будет обрезано."""
import sys,wave,numpy as np
from pieces import PIECES,FPS
w=wave.open(sys.argv[1]);sr=w.getframerate()
A=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
rms=lambda a,b:float(np.sqrt(np.mean(A[int(a*sr):int(b*sr)]**2))) if b>a else 0
for k,(f0,n,z) in enumerate(PIECES):
    a=f0/FPS;b=(f0+n)/FPS
    contig_prev=k>0 and PIECES[k-1][0]+PIECES[k-1][1]==f0
    contig_next=k+1<len(PIECES) and PIECES[k+1][0]==f0+n
    fl=[]
    if not contig_prev and rms(a-0.06,a)>0.008: fl.append("START режет звук")
    if not contig_next and rms(b,b+0.06)>0.008: fl.append("END режет звук")
    print(f"{k+1:2} {a:8.3f}-{b:8.3f}  {' | '.join(fl) or 'ok'}")
