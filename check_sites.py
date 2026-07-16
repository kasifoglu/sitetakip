import requests
import hashlib
import json
import os
import sys

# Takip edilecek siteler: {"isim": "url"}
SITES = {
    "hsk_mustemir": "https://www.hsk.gov.tr/Arsiv/mustemir",
    "hsk_duyurular": "https://www.hsk.gov.tr/Arsiv/duyuru",
}

STATE_FILE = "state.json"
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    resp = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    print(f"Telegram cevabı: {resp.status_code} - {resp.text}")

def get_hash(url):
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    return hashlib.sha256(r.text.encode()).hexdigest()

def main():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    else:
        state = {}

    changed = False
    for name, url in SITES.items():
        try:
            new_hash = get_hash(url)
        except Exception as e:
            print(f"Hata ({name}): {e}")
            continue

        old_hash = state.get(name)
        if old_hash is None:
            state[name] = new_hash
            changed = True
        elif old_hash != new_hash:
            send_telegram(f"🔔 Değişiklik algılandı: {name}\n{url}")
            state[name] = new_hash
            changed = True

    if changed:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

if __name__ == "__main__":
    main()
    sys.exit(0)
