"""Split every piece of a reel spec at pauses (>MIN_GAP s) and drop listed source ranges.
usage: tighten.py SPEC_IN SPEC_OUT [--show]
spec may contain "drop": [[src, a, b], ...]  -> source ranges removed (false starts, repeats)
pieces become [src, a, b, group] where group = original piece index (overlay anchors keep working)
"""
import json, sys, wave, numpy as np
from faster_whisper import WhisperModel

MIN_GAP, PAD_L, PAD_R = 0.30, 0.05, 0.07
spec = json.load(open(sys.argv[1])); show = "--show" in sys.argv
W = spec["wavdir"]; cache = {}
def snd(n):
    if n not in cache:
        w = wave.open(f"{W}/{n}.wav"); cache[n] = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return cache[n]
def env(n, a, b):
    x = snd(n)[int(a * 16000):int(b * 16000)]; fr = 320
    return np.array([20 * np.log10(np.sqrt((x[i:i + fr] ** 2).mean()) + 1e-9) for i in range(0, max(0, len(x) - fr), fr)])

m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
PROMPT = "Ну, э-э, вот, то есть, то есть, мне кажется, мне кажется, ну это, как бы. Повторы и запинки записываем дословно."
drops = spec.get("drop", [])
out = []
for g, p in enumerate(spec["pieces"]):
    src, a, b = p[0], p[1], p[2]
    x = snd(src)[int(a * 16000):int(b * 16000)]
    segs, _ = m.transcribe(x, language="ru", beam_size=5, word_timestamps=True, condition_on_previous_text=False, initial_prompt=PROMPT)
    words = [(a + wd.start, a + wd.end, wd.word.strip()) for s in segs for wd in s.words]
    if not words: continue
    from faster_whisper.vad import get_speech_timestamps, VadOptions
    ts = get_speech_timestamps(x, VadOptions(threshold=0.3, neg_threshold=0.2, min_silence_duration_ms=300, speech_pad_ms=110, min_speech_duration_ms=80))
    if not ts: continue
    keep = [[max(a, a + t["start"] / 16000), min(b, a + t["end"] / 16000)] for t in ts]
    # merge pieces separated by < 0.12 s (pads overlapping)
    mk = [keep[0]]
    for ka, kb in keep[1:]:
        if ka - mk[-1][1] < 0.12: mk[-1][1] = kb
        else: mk.append([ka, kb])
    keep = mk
    # also split at clear energy dips (>=0.3 s, 13 dB under speech level)
    e = env(src, a, b); es = np.convolve(e, np.ones(3) / 3, mode="same"); thr = np.percentile(es, 80) - 13
    nk = []
    for ka, kb in keep:
        i0, i1 = int((ka - a) / 0.02), min(len(es), int((kb - a) / 0.02)); cur = ka; j = i0
        while j < i1:
            if es[j] < thr:
                k = j
                while k < i1 and es[k] < thr: k += 1
                if (k - j) * 0.02 >= 0.30 and j > i0 + 4 and k < i1 - 4:
                    nk.append([cur, a + j * 0.02 + 0.09]); cur = a + k * 0.02 - 0.07
                j = k
            else: j += 1
        nk.append([cur, kb])
    keep = nk
    # trim the very start / end of the piece to the speech itself
    above = np.where(es >= thr)[0]
    if len(above):
        first, last = a + above[0] * 0.02 - 0.12, a + (above[-1] + 1) * 0.02 + 0.14
        keep[0][0] = max(keep[0][0], first); keep[-1][1] = min(keep[-1][1], last)
    # never split inside protected ranges (quiet short words like "не")
    for ns, na, nb in spec.get("nosplit", []):
        if ns != src: continue
        mk = [keep[0]]
        for ka, kb in keep[1:]:
            if mk[-1][1] >= na - 0.05 and ka <= nb + 0.05: mk[-1][1] = kb
            else: mk.append([ka, kb])
        keep = mk
    if g in spec.get("keep_end", []): keep[-1][1] = b
    if g in spec.get("keep_start", []): keep[0][0] = a
    # apply drops
    for ds, da, db in drops:
        if ds != src: continue
        nk = []
        for ka, kb in keep:
            if db <= ka or da >= kb: nk.append([ka, kb]); continue
            if da > ka: nk.append([ka, da])
            if db < kb: nk.append([db, kb])
        keep = nk
    keep = [k for k in keep if k[1] - k[0] > 0.15]
    for ka, kb in keep: out.append([src, round(ka, 2), round(kb, 2), g])
    if show:
        import re
        y = np.concatenate([snd(src)[int(ka * 16000):int(kb * 16000)] for ka, kb in keep])
        s2, _ = m.transcribe(y, language="ru", beam_size=5, condition_on_previous_text=False, initial_prompt=PROMPT)
        norm = lambda t: re.sub(r"[^а-яёa-z0-9 ]", "", t.lower()).split()
        t_before = norm(" ".join(w[2] for w in words)); t_after = norm(" ".join(z.text for z in s2))
        print("   AFTER:", " ".join(t_after), "" if t_before[:2] == t_after[:2] and t_before[-2:] == t_after[-2:] else "   <<< CHECK")
    if show:
        print(f"--- p{g} {src} {a}-{b}")
        print("   " + " ".join(f"{s:.2f}|{t}" for s, e_, t in words))
        print("   keep:", [(round(k[0], 2), round(k[1], 2)) for k in keep], f"{sum(k[1]-k[0] for k in keep):.1f}s of {b-a:.1f}s")
spec["pieces"] = out
json.dump(spec, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
