"""Send reels to the owner's Telegram bot through the MyBrand worker.

  python3 tg_send.py video  <file.mp4> <reel_id> <version> "<title>" ["<note>"]
  python3 tg_send.py photo  <cover.jpg> ["<caption html>"]
  python3 tg_send.py copy   "<label>" <text-file>        # one copy-ready block (<pre>)
  python3 tg_send.py text   "<html text>"
  python3 tg_send.py events                               # collect approvals/edits waiting in the bot (and clear them)

Needs the env var REELS_API_TOKEN (set in the Claude environment settings; same value
as the worker secret). Videos over 45 MB are re-encoded first (Telegram bot limit is 50 MB).
Prints the worker's JSON answer (message_id is needed in reels-queue.md)."""
import html,json,os,subprocess,sys,tempfile
BASE=os.environ.get("REELS_WORKER","https://tasktracker.oxion-ezhkov.workers.dev")
TOKEN=os.environ.get("REELS_API_TOKEN","")
LIMIT=45*1024*1024
def curl(path,args):
    if not TOKEN: sys.exit("REELS_API_TOKEN is not set: send the file with SendUserFile instead")
    r=subprocess.run(["curl","-sS","-m","600","-H",f"Authorization: Bearer {TOKEN}",*args,f"{BASE}/reels/{path}"],capture_output=True,text=True)
    print(r.stdout or r.stderr);return r.stdout
def shrink(src):
    if os.path.getsize(src)<=LIMIT: return src
    dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",src],capture_output=True,text=True).stdout)
    kbps=int((LIMIT*8/1024)/dur*0.92)-160
    out=os.path.join(tempfile.mkdtemp(),os.path.basename(src))
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-c:v","libx264","-preset","medium","-b:v",f"{kbps}k","-maxrate",f"{int(kbps*1.3)}k","-bufsize",f"{kbps*2}k",
                    "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",out],check=True)
    return out
cmd=sys.argv[1]
if cmd=="video":
    f=shrink(sys.argv[2]);args=["-F",f"reel_id={sys.argv[3]}","-F",f"version={sys.argv[4]}","-F",f"title={sys.argv[5]}","-F",f"file=@{f};type=video/mp4"]
    if len(sys.argv)>6: args+=["-F",f"note={sys.argv[6]}"]
    curl("send-video",args)
elif cmd=="photo":
    args=["-F",f"file=@{sys.argv[2]};type=image/jpeg"]
    if len(sys.argv)>3: args+=["-F",f"caption={sys.argv[3]}"]
    curl("send-photo",args)
elif cmd=="copy":
    body=open(sys.argv[3],encoding="utf-8").read().strip()
    text=f"<b>{html.escape(sys.argv[2])}</b>\n<pre>{html.escape(body)}</pre>"
    curl("send-text",["-H","Content-Type: application/json","--data-binary",json.dumps({"text":text},ensure_ascii=False)])
elif cmd=="text":
    curl("send-text",["-H","Content-Type: application/json","--data-binary",json.dumps({"text":sys.argv[2]},ensure_ascii=False)])
elif cmd=="events":
    curl("events",["-X","POST"])
else: sys.exit(__doc__)
