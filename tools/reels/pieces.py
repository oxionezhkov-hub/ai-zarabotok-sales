"""Snap piece boundaries to the quietest point nearby and transcribe each piece.
usage: pieces.py WAVDIR src:a:b [src:a:b ...]
"""
import sys, wave, numpy as np
from faster_whisper import WhisperModel

D = sys.argv[1]
cache = {}
def audio(n):
    if n not in cache:
        w = wave.open(f"{D}/{n}.wav")
        cache[n] = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return cache[n]

def db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)

def snap(n, t, r=0.22):
    x = audio(n); fr = 320  # 20 ms
    lo, hi = int((t - r) * 16000), int((t + r) * 16000)
    best, bt = 1e9, t
    for s in range(max(0, lo), hi - fr, 80):
        e = db(x[s:s + fr]) + abs((s + fr / 2) / 16000 - t) * 3  # prefer close to t
        if e < best: best, bt = e, (s + fr / 2) / 16000
    return round(bt, 2), round(db(x[int(bt * 16000) - 160:int(bt * 16000) + 160]), 1)

m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
for spec in sys.argv[2:]:
    n, a, b = spec.split(":"); a = float(a); b = float(b)
    (sa, da), (sb, dbb) = snap(n, a), snap(n, b)
    x = audio(n)[int(sa * 16000):int(sb * 16000)]
    segs, _ = m.transcribe(x, language="ru", beam_size=5, condition_on_previous_text=False)
    txt = " ".join(s.text.strip() for s in segs)
    print(f"{n}:{sa}:{sb}  [{da}dB|{dbb}dB]  {sb - sa:.1f}s  -> {txt}", flush=True)
