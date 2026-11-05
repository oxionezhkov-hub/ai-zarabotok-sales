"""Публикует одобренные посты из threads/queue/*.json, когда подошло их время.

Пост выходит, если status == "approved", у него ещё нет published_id
и scheduled_at уже наступил, но прошло не больше MAX_LATE_HOURS.
Опоздавшие посты помечаются status = "missed" и не публикуются.
"""
import datetime as dt
import glob
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
MAX_LATE_HOURS = 3
TOKEN = os.environ.get("THREADS_TOKEN", "").strip()
DRY_RUN = os.environ.get("DRY_RUN") == "1"


def post(path, params):
    data = urllib.parse.urlencode({**params, "access_token": TOKEN}).encode()
    req = urllib.request.Request(f"{API}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")


def publish_text(text):
    container = post("me/threads", {"media_type": "TEXT", "text": text})["id"]
    time.sleep(5)  # Meta советует подождать, пока контейнер обработается
    return post("me/threads_publish", {"creation_id": container})["id"]


def check_token():
    url = f"{API}/me?" + urllib.parse.urlencode({"fields": "id,username", "access_token": TOKEN})
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            me = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Токен не принят Threads: HTTP {e.code} {e.read().decode(errors='replace')}")
    print(f"Токен в порядке, аккаунт @{me.get('username')}")


def main():
    if not TOKEN and not DRY_RUN:
        sys.exit("Нет секрета THREADS_TOKEN")
    if not DRY_RUN:
        check_token()
    now = dt.datetime.now(dt.timezone.utc)
    failed = 0
    for path in sorted(glob.glob("threads/queue/*.json")):
        posts = json.load(open(path, encoding="utf-8"))
        changed = False
        for p in posts:
            if p.get("status") != "approved" or p.get("published_id"):
                continue
            at = dt.datetime.fromisoformat(p["scheduled_at"])
            if at > now:
                continue
            if now - at > dt.timedelta(hours=MAX_LATE_HOURS):
                p["status"] = "missed"
                changed = True
                print(f"{p['id']}: пропущен, опоздание больше {MAX_LATE_HOURS} ч")
                continue
            text = p.get("final_text") or p["text"]
            if DRY_RUN:
                print(f"[dry-run] {p['id']} {p['scheduled_at']}: {text[:60]}…")
                continue
            try:
                p["published_id"] = publish_text(text)
                p["published_at"] = now.isoformat(timespec="seconds")
                p["status"] = "published"
                print(f"{p['id']}: опубликован, id {p['published_id']}")
            except Exception as e:  # пост остаётся approved, попробуем в следующий запуск
                failed += 1
                print(f"{p['id']}: ошибка: {e}")
            changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
                f.write("\n")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
