#!/usr/bin/env python3
"""Kosher Tek site backend (stdlib only), listens on 127.0.0.1:8099.
Public:  POST /api/contact   GET /api/products   GET /api/services
Admin:   POST /api/admin/login|logout, GET|PUT /api/admin/data,
         GET /api/admin/messages, POST /api/admin/messages/delete, POST /api/admin/upload
Env: KT_ADMIN_PASS (required for admin), KT_SMTP_USER, KT_SMTP_PASS, KT_MAIL_TO
"""
import base64, hashlib, hmac, json, os, secrets, smtplib, sys, threading, time, uuid
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market

PORT = int(os.environ.get("KT_PORT", "8099"))
DIR = os.environ.get("KT_DIR", "/var/lib/kt-contact")
LOG = os.path.join(DIR, "messages.jsonl")
DATA = os.path.join(DIR, "data.json")
UPLOADS = os.path.join(DIR, "uploads")
SECRET_FILE = os.path.join(DIR, "secret")
SMTP_USER = os.environ.get("KT_SMTP_USER", "")
SMTP_PASS = os.environ.get("KT_SMTP_PASS", "")
MAIL_TO = os.environ.get("KT_MAIL_TO", SMTP_USER)
ADMIN_PASS = os.environ.get("KT_ADMIN_PASS", "")
SESSION_SECONDS = 12 * 3600
MAX = {"name": 100, "contact": 150, "subject": 80, "message": 4000}
lock = threading.Lock()
hits, login_fail = {}, {}

DEFAULT = {
    "services": {"android": "מחיר סימלי", "computers": "מחיר סימלי", "software": "מחיר סימלי",
                 "websites": "מחיר סימלי", "shop": "לפי דגם", "request": "מחיר אוטומטי",
                 "apps": "במחיר רצפה", "players": "במחיר רצפה", "translate": "במחיר רצפה", "design": "במחיר רצפה", "scripts": "במחיר רצפה"},
    "products": [
        {"id": "m393", "name": "נגן הכינור",
         "desc": "נגן אנדרואיד 13 קומפקטי, מגיע מוכשר ומוכן לשמיעה וללימוד.\nמסך 3.99 אינץ' חד (400×960)\nמעבד 8 ליבות, 3GB זיכרון ו-16GB אחסון\nכרטיס זיכרון עד 1TB\nBluetooth 5.0 ורדיו FM, מגיע בלי אינטרנט\nשמע איכותי (DAC) וחיישן תנועה\nסוללה 1250mAh\nבקופסה: אוזניות, כבל USB-C וכיסוי מגן",
         "price": "", "status": "out", "image": "/assets/products/kinor-set.jpg",
         "gallery": ["/assets/products/kinor-set.jpg", "/assets/products/kinor-front.jpg"], "visible": True},
        {"id": "m36plus", "name": "נגן הנבל",
         "desc": "נגן אנדרואיד עם פנס, מגיע מוכשר ומוכן לשמיעה וללימוד.\n32GB אחסון\nכרטיס זיכרון\nמצלמה ופנס (אפשר גם בלי מצלמה)\nכפתור ייעודי בצד המכשיר",
         "price": "", "status": "order", "image": "/assets/products/nevel-back.jpg",
         "gallery": ["/assets/products/nevel-back.jpg"], "visible": True},
        {"id": "other", "name": "דגמים נוספים", "desc": "יש דגמים נוספים בהזמנה מיוחדת. אפשר לברר זמינות ומחיר.",
         "price": "לפי דגם", "status": "order", "image": "", "visible": True},
    ],
}
CATALOG = 3  # bump to roll new default products into an existing data file

def secret():
    os.makedirs(DIR, exist_ok=True)
    if not os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "w") as f:
            f.write(secrets.token_hex(32))
        os.chmod(SECRET_FILE, 0o600)
    return open(SECRET_FILE).read().strip().encode()

SECRET = None

def load_data():
    try:
        with open(DATA, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = json.loads(json.dumps(DEFAULT))
    d.setdefault("services", {}); d.setdefault("products", [])
    for k, v in DEFAULT["services"].items():
        d["services"].setdefault(k, v)
    if d.get("catalog", 0) < CATALOG:
        # new built-in products replace the old ones with the same id; stock and price set in the admin panel stay
        old = {p.get("id"): p for p in d["products"]}
        fresh = []
        for p in DEFAULT["products"]:
            q = dict(p)
            if p["id"] in old:
                q["status"] = old[p["id"]].get("status", q["status"])
                q["price"] = old[p["id"]].get("price") or q["price"]
            fresh.append(q)
        ids = {p["id"] for p in fresh}
        d["products"] = fresh + [p for p in d["products"] if p.get("id") not in ids]
        d["catalog"] = CATALOG
    return d

def save_data(d):
    os.makedirs(DIR, exist_ok=True)
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DATA)

def clip(v, n):
    return str(v if v is not None else "").strip()[:n]

def clean_products(items):
    out = []
    for p in (items or [])[:200]:
        if not isinstance(p, dict):
            continue
        status = p.get("status") if p.get("status") in ("in", "out", "order") else "in"
        img = clip(p.get("image"), 200)
        if img and not (img.startswith("/uploads/") or img.startswith("/assets/products/")):
            img = ""
        gal = [clip(x, 200) for x in (p.get("gallery") or [])[:8] if isinstance(x, str)]
        gal = [x for x in gal if x.startswith("/uploads/") or x.startswith("/assets/products/")]
        out.append({"id": clip(p.get("id"), 40) or uuid.uuid4().hex[:8], "name": clip(p.get("name"), 120),
                    "desc": clip(p.get("desc"), 600), "price": clip(p.get("price"), 60), "status": status,
                    "image": img, "gallery": gal, "visible": bool(p.get("visible", True))})
    return out

def clean_services(d):
    out = {}
    for k in DEFAULT["services"]:
        out[k] = clip((d or {}).get(k, DEFAULT["services"][k]), 60)
    return out

def make_token():
    exp = str(int(time.time()) + SESSION_SECONDS)
    sig = hmac.new(SECRET, exp.encode(), hashlib.sha256).hexdigest()
    return exp + "." + sig

def check_token(tok):
    try:
        exp, sig = tok.split(".", 1)
        good = hmac.new(SECRET, exp.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, good) and int(exp) > time.time()
    except Exception:
        return False

def rate(table, ip, limit, window):
    now = time.time()
    with lock:
        recent = [t for t in table.get(ip, []) if now - t < window]
        if len(recent) >= limit:
            table[ip] = recent
            return True
        recent.append(now)
        table[ip] = recent
    return False

def send_mail(d):
    if not (SMTP_USER and SMTP_PASS and MAIL_TO):
        return
    m = EmailMessage()
    m["Subject"] = "פנייה חדשה מהאתר: " + d["subject"]
    m["From"] = SMTP_USER
    m["To"] = MAIL_TO
    m.set_content("שם: %s\nדרך קשר: %s\nנושא: %s\n\n%s\n" % (d["name"], d["contact"], d["subject"], d["message"]))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(m)

def read_messages():
    out = []
    try:
        with open(LOG, encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return out

def write_messages(msgs):
    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    os.replace(tmp, LOG)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def ip(self):
        return self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip() or self.client_address[0]
    def reply(self, code, obj, headers=None):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)
    def body(self, limit=30000):
        n = int(self.headers.get("Content-Length", "0"))
        if n <= 0 or n > limit:
            raise ValueError("size")
        return json.loads(self.rfile.read(n).decode("utf-8"))
    def authed(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "kt_admin" and check_token(v):
                return True
        return False
    def cross_site(self):
        # writes must come from our own pages: a foreign Origin is refused even if a browser sent cookies
        o = self.headers.get("Origin")
        if not o:
            return False
        host = (self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or "").lower()
        return o.lower().split("://", 1)[-1].rstrip("/") != host
    def path_only(self):
        return self.path.split("?", 1)[0].rstrip("/")

    def do_GET(self):
        p = self.path_only()
        if p.startswith("/market/p/"):
            return market.profile_page(self, p[len("/market/p/"):])
        if p == "/api/products":
            d = load_data()
            return self.reply(200, [x for x in d["products"] if x.get("visible", True)])
        if p == "/api/services":
            return self.reply(200, load_data()["services"])
        if p.startswith("/api/m/"):
            return market.handle(self, "GET", p)
        if p.startswith("/api/admin/m/"):
            return market.admin(self, "GET", p)
        if p.startswith("/api/admin"):
            if not ADMIN_PASS:
                return self.reply(503, {"error": "admin disabled"})
            if not self.authed():
                return self.reply(401, {"error": "login"})
            if p == "/api/admin/data":
                return self.reply(200, load_data())
            if p == "/api/admin/messages":
                return self.reply(200, list(reversed(read_messages())))
            if p == "/api/admin/me":
                return self.reply(200, {"ok": True})
        return self.reply(404, {"error": "not found"})

    def do_PUT(self):
        p = self.path_only()
        if self.cross_site():
            return self.reply(403, {"error": "origin"})
        if p.startswith("/api/m/"):
            return market.handle(self, "PUT", p)
        if p.startswith("/api/admin/m/"):
            return market.admin(self, "PUT", p)
        if p == "/api/admin/data":
            if not ADMIN_PASS or not self.authed():
                return self.reply(401, {"error": "login"})
            try:
                d = self.body(200000)
            except Exception:
                return self.reply(400, {"error": "bad"})
            new = {"products": clean_products(d.get("products")), "services": clean_services(d.get("services"))}
            with lock:
                save_data(new)
            return self.reply(200, {"ok": True})
        return self.reply(404, {"error": "not found"})

    def do_POST(self):
        p = self.path_only()
        if self.cross_site():
            return self.reply(403, {"error": "origin"})
        if p.startswith("/api/m/"):
            return market.handle(self, "POST", p)
        if p.startswith("/api/admin/m/"):
            return market.admin(self, "POST", p)
        try:
            if p == "/api/contact":
                return self.contact()
            if p == "/api/admin/login":
                return self.login()
            if p == "/api/admin/logout":
                return self.reply(200, {"ok": True}, {"Set-Cookie": "kt_admin=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"})
            if p in ("/api/admin/messages/delete", "/api/admin/upload"):
                if not ADMIN_PASS or not self.authed():
                    return self.reply(401, {"error": "login"})
                return self.messages_delete() if p.endswith("delete") else self.upload()
        except ValueError:
            return self.reply(400, {"error": "bad"})
        return self.reply(404, {"error": "not found"})

    def contact(self):
        ip = self.ip()
        d = self.body(20000)
        if d.get("website"):
            return self.reply(200, {"ok": True})
        c = {k: clip(d.get(k), mx) for k, mx in MAX.items()}
        if not c["name"] or not c["contact"] or not c["message"]:
            return self.reply(400, {"error": "missing"})
        if rate(hits, ip, 8, 3600):
            return self.reply(429, {"error": "slow down"})
        c.update({"id": uuid.uuid4().hex[:10], "time": time.strftime("%Y-%m-%d %H:%M:%S"), "ip": ip})
        try:
            os.makedirs(DIR, exist_ok=True)
            with lock, open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        except Exception:
            return self.reply(500, {"error": "save failed"})
        try:
            send_mail(c)
        except Exception:
            pass
        return self.reply(200, {"ok": True})

    def login(self):
        if not ADMIN_PASS:
            return self.reply(503, {"error": "admin disabled"})
        ip = self.ip()
        if rate(login_fail, ip, 10, 900):
            return self.reply(429, {"error": "slow down"})
        d = self.body(2000)
        if not hmac.compare_digest(clip(d.get("password"), 200).encode(), ADMIN_PASS.encode()):
            time.sleep(1)
            return self.reply(401, {"error": "wrong"})
        ck = "kt_admin=%s; Path=/; Max-Age=%d; HttpOnly; Secure; SameSite=Strict" % (make_token(), SESSION_SECONDS)
        return self.reply(200, {"ok": True}, {"Set-Cookie": ck})

    def messages_delete(self):
        d = self.body(5000)
        ids = set(str(x) for x in d.get("ids", []))
        with lock:
            msgs = [m for m in read_messages() if m.get("id") not in ids]
            write_messages(msgs)
        return self.reply(200, {"ok": True})

    def upload(self):
        d = self.body(4_500_000)
        raw = base64.b64decode(str(d.get("data", "")).split(",")[-1], validate=False)
        if len(raw) < 100 or len(raw) > 3_000_000:
            return self.reply(400, {"error": "size"})
        if raw[:8] == b"\x89PNG\r\n\x1a\n":
            ext = "png"
        elif raw[:3] == b"\xff\xd8\xff":
            ext = "jpg"
        elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
            ext = "webp"
        else:
            return self.reply(400, {"error": "type"})
        os.makedirs(UPLOADS, exist_ok=True)
        name = uuid.uuid4().hex[:12] + "." + ext
        with open(os.path.join(UPLOADS, name), "wb") as f:
            f.write(raw)
        return self.reply(200, {"url": "/uploads/" + name})

if __name__ == "__main__":
    SECRET = secret()
    os.makedirs(UPLOADS, exist_ok=True)
    market.init(SECRET, DIR)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
