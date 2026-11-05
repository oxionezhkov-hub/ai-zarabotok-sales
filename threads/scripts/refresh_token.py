"""Продлевает долгоживущий токен Threads ещё на 60 дней и печатает новый в stdout."""
import json
import os
import sys
import urllib.parse
import urllib.request

token = os.environ["THREADS_TOKEN"].strip()
url = "https://graph.threads.net/refresh_access_token?" + urllib.parse.urlencode(
    {"grant_type": "th_refresh_token", "access_token": token}
)
with urllib.request.urlopen(url, timeout=60) as r:
    data = json.load(r)
days = int(data.get("expires_in", 0)) // 86400
print(f"Токен продлён, действует ещё {days} дн.", file=sys.stderr)
print(data["access_token"])
