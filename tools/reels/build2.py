"""Generic reel builder.
usage: build2.py SPEC.json OUT.mp4
spec: {srcdir, wavdir, assets, pieces:[[src,a,b],...], overlays:[[png, start, end, y],...],
       fixes:{word:repl}, grade:{src:"eq=..."}}
start/end anchors: number (s) | "p3" (start of piece 3) | "p3e" (end) | "w:слово:n[:+off]" (n-th word on output)
"""
import json, os, re, subprocess, sys, wave
import numpy as np

spec = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SRC, WAV, A = spec["srcdir"], spec["wavdir"], spec["assets"]
P = [tuple(p[:3]) for p in spec["pieces"]]
G = [p[3] if len(p) > 3 else i for i, p in enumerate(spec["pieces"])]
tmp = os.path.abspath(OUT) + ".work"; os.makedirs(tmp, exist_ok=True)

def snd(src):
    w = wave.open(f"{WAV}/{src}.wav")
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
cache = {}
def lvl(src, a, b):
    x = cache.setdefault(src, snd(src))[int(a * 16000):int(b * 16000)]
    fr = x[: len(x) // 800 * 800].reshape(-1, 800); e = np.sqrt((fr ** 2).mean(1))
    return 20 * np.log10(np.sqrt((e[e > np.percentile(e, 50)] ** 2).mean()))
lv = [lvl(*p) for p in P]; ref = float(np.median(lv))

offs, t = [], 0.0
for s, a, b in P: offs.append(t); t += b - a
HOLD = float(spec.get("hold", 0))
TOTAL = t + HOLD
srcs = sorted(set(p[0] for p in P)); idx = {s: i for i, s in enumerate(srcs)}
ins = []
for s in srcs: ins += ["-i", f"{SRC}/IMG_{s}.MOV"]

afc = []
for k, (s, a, b) in enumerate(P):
    afc.append(f"[{idx[s]}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,volume={ref - lv[k]:.2f}dB,"
               f"afade=t=in:d=0.03,afade=t=out:st={b - a - 0.04:.3f}:d=0.04[a{k}]")
afc.append("".join(f"[a{k}]" for k in range(len(P))) + f"concat=n={len(P)}:v=0:a=1,"
           f"apad=pad_dur={HOLD},highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
apath = f"{tmp}/audio.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(afc), "-map", "[aout]", apath], check=True)
final_audio = apath
mus = spec.get("music")
if mus:  # very quiet background: ~25 dB under the voice, ducked further while speaking
    final_audio = f"{tmp}/audio_mix.wav"
    gap = float(mus.get("under_db", 25)); start = float(mus.get("start", 0))
    mfc = (f"[1:a]aresample=48000,atrim={start}:{start + TOTAL + 1},asetpts=PTS-STARTPTS,loudnorm=I={-14 - gap}:TP=-9,aresample=48000,"
           f"afade=t=in:d=1.0,afade=t=out:st={max(0, TOTAL - 1.8):.2f}:d=1.8,atrim=0:{TOTAL:.3f}[m];"
           f"[0:a]asplit[v1][v2];[m][v2]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=500[md];"
           f"[v1][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=0[mix]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", apath, "-stream_loop", "-1", "-i", mus["file"], "-filter_complex", mfc,
                    "-map", "[mix]", "-ar", "48000", final_audio], check=True)

# --- transcribe the assembled audio for exact subtitle timing
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
w16 = f"{tmp}/a16.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", apath, "-ac", "1", "-ar", "16000", w16], check=True)
x = snd_out = np.frombuffer(wave.open(w16).readframes(10 ** 9), np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(x, language="ru", beam_size=5, word_timestamps=True, condition_on_previous_text=False)
fixes = spec.get("fixes", {})
words = []
for sg in segs:
    for wd in sg.words:
        tok = wd.word.strip().strip(",.?!…").lower()
        if not tok: continue
        tok = fixes.get(tok, tok)
        if tok == "": continue
        words.append([wd.start, wd.end, tok])
for src_seq, dst_seq in spec.get("seq_fixes", []):
    i = 0
    while i <= len(words) - len(src_seq):
        if [w[2] for w in words[i:i + len(src_seq)]] == src_seq:
            st, en = words[i][0], words[i + len(src_seq) - 1][1]
            step = (en - st) / max(1, len(dst_seq))
            words[i:i + len(src_seq)] = [[st + k * step, st + (k + 1) * step, t] for k, t in enumerate(dst_seq)]
        i += 1
words = [w for w in words if w[0] < TOTAL - HOLD - 0.05]
# typical whisper hallucinations on silence / music
HALL = {"субтитры", "субтитров", "редактор", "продолжение", "следует", "корректор"}
words = [w for w in words if w[2] not in HALL]
drops = spec.get("drop_before", [])
words = [w for i, w in enumerate(words)
         if not any(w[2] == a and i + 1 < len(words) and words[i + 1][2].startswith(b) for a, b in drops)]
words = [w for i, w in enumerate(words) if not (i and w[2] == "да" and words[i - 1][2] == "тогда")]
json.dump(words, open(f"{tmp}/words.json", "w"), ensure_ascii=False)

def piece_of(tm):
    for k in range(len(P) - 1, -1, -1):
        if tm >= offs[k] - 0.02: return G[k]
    return G[0]
caps, cur = [], []
for wd in words:
    if wd[2].startswith("-") and cur:
        cur[-1] = [cur[-1][0], wd[1], cur[-1][2] + wd[2]]; continue
    if cur and (len(cur) == 3 or len(" ".join(c[2] for c in cur + [wd])) > 19 or wd[0] - cur[-1][1] > 0.6
                or piece_of(wd[0] + 0.05) != piece_of(cur[-1][0] + 0.05)):
        caps.append(cur); cur = []
    cur.append(wd)
if cur: caps.append(cur)
def ts(v): return f"{int(v // 3600)}:{int(v % 3600 // 60):02d}:{v % 60:05.2f}"
ass = ["[Script Info]", "PlayResX: 1080", "PlayResY: 1920", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: S,Inter ExtraBold,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,2,5,40,40,0,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
SUBY = spec.get("sub_y", 1450)
for i, c in enumerate(caps):
    st = c[0][0]; nxt = caps[i + 1][0][0] if i + 1 < len(caps) else TOTAL
    en = nxt if nxt - c[-1][1] < 0.6 else c[-1][1] + 0.25
    txt = " ".join(z[2] for z in c)
    for pat, rep in spec.get("text_fixes", []): txt = re.sub(pat, rep, txt, flags=re.I)
    prev_end = caps[i - 1][-1][1] if i else -9
    if i == 0 or (piece_of(st + 0.05) != piece_of(prev_end - 0.05) and c[0][2] not in ("или", "либо", "что", "а", "чтобы")): txt = txt[0].upper() + txt[1:]
    ass.append(f"Dialogue: 0,{ts(st)},{ts(min(en, TOTAL))},S,,0,0,0,,{{\\pos(540,{SUBY})}}{txt}")
open(f"{tmp}/subs.ass", "w").write("\n".join(ass) + "\n")

def anchor(v):
    if isinstance(v, (int, float)): return float(v)
    if v == "end": return TOTAL
    mm = re.fullmatch(r"p(\d+)(e?)([+-][\d.]+)?", v)
    if mm:
        g = int(mm.group(1)); ks = [i for i in range(len(P)) if G[i] == g]
        base = offs[ks[-1]] + P[ks[-1]][2] - P[ks[-1]][1] if mm.group(2) else offs[ks[0]]
        return base + (float(mm.group(3)) if mm.group(3) else 0)
    _, wd, n, *off = v.split(":")
    hits = [z[0] for z in words if z[2] == wd]
    return hits[int(n)] + (float(off[0]) if off else 0)

# --- video: encode each piece on its own (low memory), then concat, then overlays
grade = spec.get("grade", {}); lst = []
for k, (s_, a, b) in enumerate(P):
    new_src = k == 0 or P[k - 1][0] != s_
    run = 0 if new_src else run + 1
    z = 1.08 if run % 2 else 1.0
    W0 = int(1210 * z) // 2 * 2
    sc = (f"scale=w='trunc({W0}*(1+0.08*pow(max(0,1-t/0.3),2))/2)*2':h=-2:eval=frame" if new_src and k > 0
          else f"scale={W0}:-2")
    g = grade.get(s_, "")
    pf = f"{tmp}/v{k:02d}.mp4"; lst.append(f"file '{pf}'")
    hold = HOLD if k == len(P) - 1 else 0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", f"{SRC}/IMG_{s_}.MOV", "-an",
                    "-vf", f"setpts=PTS-STARTPTS,{g + ',' if g else ''}{sc},crop=1080:1920:(iw-1080)/2:(ih-1920)*0.25,setsar=1,fps=30,format=yuv420p{f',tpad=stop_mode=clone:stop_duration={hold}' if hold else ''}",
                    "-frames:v", str(round((b - a + hold) * 30)), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", pf], check=True)
open(f"{tmp}/list.txt", "w").write("\n".join(lst) + "\n")
vc = f"{tmp}/vc.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", vc], check=True)
fc = []; n = 1; last = "0:v"; vins = []
for j, (f, a) in enumerate(spec.get("inserts", [])):
    a = anchor(a)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{A}/{f}"],
                             capture_output=True, text=True).stdout)
    print(f"  insert {f} {a:6.2f} -> {a + d:6.2f}")
    vins += ["-i", f"{A}/{f}"]
    fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{a:.3f}/TB[ins{j}];[{last}][ins{j}]overlay=0:0:eof_action=pass:enable='between(t,{a:.3f},{a + d - 0.02:.3f})'[i{j}]")
    last = f"i{j}"; n += 1
for j, (png, a, b, y) in enumerate(spec.get("overlays", [])):
    a, b = anchor(a), anchor(b)
    print(f"  {png:10s} {a:6.2f} -> {b:6.2f}")
    vins += ["-i", f"{A}/{png}.png"]
    fc.append(f"[{last}][{n}:v]overlay=x=(W-w)/2:y={y}:enable='between(t,{a:.3f},{b:.3f})'[o{j}]")
    last = f"o{j}"; n += 1
fc.append(f"[{last}]ass={tmp}/subs.ass[vout]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vc, *vins, "-i", final_audio, "-filter_complex", ";".join(fc),
                "-map", "[vout]", "-map", f"{n}:a", "-t", f"{TOTAL:.3f}", "-c:v", "libx264", "-preset", "medium",
                "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
print("OK", OUT, f"{TOTAL:.1f}s")
print("TEXT:", " ".join(z[2] for z in words))
