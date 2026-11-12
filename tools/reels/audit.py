import sys, wave, json, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
for f in sys.argv[1:]:
    w = wave.open(f); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    fr = 320; e = np.array([20*np.log10(np.sqrt((x[i:i+fr]**2).mean())+1e-9) for i in range(0, len(x)-fr, fr)])
    thr = np.percentile(e, 70) - 20
    low = e < thr; gaps = []; i = 0
    while i < len(low):
        if low[i]:
            j = i
            while j < len(low) and low[j]: j += 1
            if (j - i) * 0.02 >= 0.35: gaps.append((round(i*0.02, 2), round(j*0.02, 2)))
            i = j
        else: i += 1
    segs, _ = m.transcribe(x, language="ru", beam_size=5, word_timestamps=True, condition_on_previous_text=False,
        initial_prompt="Ну, э-э, вот, то есть, то есть, мне кажется, мне кажется, ну это, как бы, короче, повторы и запинки записываем дословно.")
    words = [(round(wd.start, 2), wd.word.strip()) for s in segs for wd in s.words]
    print("=====", f.split('/')[-3], "thr", round(thr, 1), "dur", round(len(x)/16000, 1))
    from faster_whisper.vad import get_speech_timestamps, VadOptions
    ts = get_speech_timestamps(x, VadOptions(threshold=0.3, neg_threshold=0.2, min_silence_duration_ms=300, speech_pad_ms=0))
    vg = [(round(ts[i]["end"]/16000, 2), round(ts[i+1]["start"]/16000, 2)) for i in range(len(ts)-1) if (ts[i+1]["start"]-ts[i]["end"])/16000 >= 0.4]
    if ts: vg = [(0, round(ts[0]["start"]/16000, 2))] * (ts[0]["start"] > 0.4*16000) + vg
    print("ENERGY GAPS:", gaps); print("VAD GAPS >=0.4s:", vg)
    print(" ".join(f"{a}|{t}" for a, t in words))
