"""Requests and jobs board for Kosher Tek (stdlib only, SQLite).
Public API under /api/m/, admin API under /api/admin/m/ (called from app.py after the admin check).
Roles: client (registers freely) and pro (individual or company, active only after admin approval).
Everything a client posts waits for admin approval. A client's contact details and a pro's e-mail are
revealed to each other only after the client chooses a bid.
"""
import hashlib, hmac, json, os, re, sqlite3, threading, time

DIR = None
SECRET = b""
DB = None
SETTINGS_FILE = None
SESSION = 14 * 86400
lock = threading.Lock()
hits = {}

LEVEL_RANK = {"basic": 1, "pro": 2, "secure": 3}
LEVELS = {"basic": "בסיסי: מפתח AI, מהיר וחסכוני", "pro": "מקצועי", "secure": "מאובטח: לדרישות אבטחה גבוהות"}
CATS = {"software": "תוכנה וכלים", "website": "אתר", "device": "התאמת מכשיר או מחשב", "design": "עיצוב",
        "writing": "כתיבה ועריכה", "help": "הדרכה ועזרה טכנית", "other": "אחר"}
SIZES = {"small": "קטנה", "medium": "בינונית", "large": "גדולה"}
DEFAULT_SETTINGS = {
    "base": {"software": 300, "website": 400, "device": 150, "design": 200, "writing": 100, "help": 80, "other": 150},
    "level_mult": {"basic": 1.0, "pro": 1.8, "secure": 2.8},
    "size_mult": {"small": 1.0, "medium": 2.2, "large": 4.5},
    "reward": {"amount": 30.0},
}
UNIT = "קרדיטים"
STATUS_REQ = ("review", "open", "taken", "done", "closed")


def init(secret, directory):
    global DIR, SECRET, DB, SETTINGS_FILE
    DIR, SECRET = directory, secret
    DB = os.path.join(directory, "market.db")
    SETTINGS_FILE = os.path.join(directory, "market_settings.json")
    os.makedirs(directory, exist_ok=True)
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
          pw TEXT NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL, created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS pros(user_id INTEGER PRIMARY KEY, kind TEXT, field TEXT, bio TEXT, links TEXT,
          level TEXT NOT NULL DEFAULT 'basic', admin_rating REAL, rating_sum INTEGER NOT NULL DEFAULT 0,
          rating_count INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT, descr TEXT,
          category TEXT, level TEXT, size TEXT, budget TEXT, contact TEXT, status TEXT NOT NULL,
          chosen_bid INTEGER, taken_pro INTEGER, created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS bids(id INTEGER PRIMARY KEY, request_id INTEGER NOT NULL, pro_id INTEGER NOT NULL,
          price TEXT, days TEXT, note TEXT, created INTEGER NOT NULL, UNIQUE(request_id, pro_id));
        CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY, request_id INTEGER NOT NULL, client_id INTEGER NOT NULL,
          pro_id INTEGER NOT NULL, client_read INTEGER NOT NULL DEFAULT 0, pro_read INTEGER NOT NULL DEFAULT 0,
          created INTEGER NOT NULL, UNIQUE(request_id, pro_id));
        CREATE TABLE IF NOT EXISTS chat_msgs(id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, sender_id INTEGER NOT NULL,
          text TEXT NOT NULL, created INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS chat_msgs_chat ON chat_msgs(chat_id, id);
        CREATE TABLE IF NOT EXISTS credits(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, referred_id INTEGER NOT NULL,
          request_id INTEGER NOT NULL UNIQUE, amount REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS ratings(request_id INTEGER PRIMARY KEY, pro_id INTEGER NOT NULL, stars INTEGER NOT NULL,
          text TEXT, created INTEGER NOT NULL);
        """)
        for stmt in ("ALTER TABLE pros ADD COLUMN exp TEXT", "ALTER TABLE users ADD COLUMN terms_at INTEGER", "ALTER TABLE users ADD COLUMN ref_code TEXT", "ALTER TABLE pros ADD COLUMN founding_until INTEGER", "ALTER TABLE requests ADD COLUMN via_admin INTEGER NOT NULL DEFAULT 0", "ALTER TABLE users ADD COLUMN referred_by INTEGER", "ALTER TABLE pros ADD COLUMN photo INTEGER NOT NULL DEFAULT 0",
                     "ALTER TABLE requests ADD COLUMN tagged_pro INTEGER", "ALTER TABLE requests ADD COLUMN only_tagged INTEGER NOT NULL DEFAULT 0"):
            try:
                c.execute(stmt)
            except sqlite3.OperationalError:
                pass
    os.makedirs(os.path.join(directory, "market_photos"), exist_ok=True)


def db():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            s = json.load(f)
    except Exception:
        s = {}
    out = json.loads(json.dumps(DEFAULT_SETTINGS))
    for part in out:
        for k in out[part]:
            try:
                out[part][k] = float(s.get(part, {}).get(k, out[part][k]))
            except Exception:
                pass
    return out


def clip(v, n):
    return str(v if v is not None else "").strip()[:n]


def limited(key, limit, window):
    now = time.time()
    with lock:
        recent = [t for t in hits.get(key, []) if now - t < window]
        if len(recent) >= limit:
            hits[key] = recent
            return True
        recent.append(now)
        hits[key] = recent
    return False


def hash_pw(pw):
    salt = os.urandom(16)
    h = hashlib.scrypt(pw.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    return salt.hex() + ":" + h.hex()


def check_pw(pw, stored):
    try:
        salt, h = stored.split(":")
        got = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt), n=2 ** 14, r=8, p=1, dklen=32)
        return hmac.compare_digest(got.hex(), h)
    except Exception:
        return False


def new_code(c):
    import secrets
    while True:
        code = secrets.token_hex(4)
        if not c.execute("SELECT 1 FROM users WHERE ref_code=?", (code,)).fetchone():
            return code


def ensure_code(c, u):
    if u["ref_code"]:
        return u["ref_code"]
    code = new_code(c)
    c.execute("UPDATE users SET ref_code=? WHERE id=?", (code, u["id"]))
    return code


def admin_pass():
    return os.environ.get("KT_MARKET_ADMIN_PASS") or os.environ.get("KT_ADMIN_PASS", "")


def admin_token():
    exp = int(time.time()) + 12 * 3600
    return "%d.%s" % (exp, hmac.new(SECRET, ("madmin%d" % exp).encode(), hashlib.sha256).hexdigest())


def admin_ok(h):
    for part in (h.headers.get("Cookie") or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k != "kt_madmin":
            continue
        try:
            exp, sig = v.split(".")
            good = hmac.new(SECRET, ("madmin%s" % exp).encode(), hashlib.sha256).hexdigest()
            return hmac.compare_digest(sig, good) and int(exp) > time.time()
        except Exception:
            return False
    return False


def make_session(uid):
    exp = int(time.time()) + SESSION
    sig = hmac.new(SECRET, ("m%d.%d" % (uid, exp)).encode(), hashlib.sha256).hexdigest()
    return "%d.%d.%s" % (uid, exp, sig)


def cookie_for(uid):
    return "kt_user=%s; Path=/; Max-Age=%d; HttpOnly; Secure; SameSite=Strict" % (make_session(uid), SESSION)


def session_user(h):
    for part in (h.headers.get("Cookie") or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k != "kt_user":
            continue
        try:
            uid, exp, sig = v.split(".")
            good = hmac.new(SECRET, ("m%s.%s" % (uid, exp)).encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, good) or int(exp) < time.time():
                return None
            with db() as c:
                u = c.execute("SELECT * FROM users WHERE id=?", (int(uid),)).fetchone()
            return u if u and u["status"] != "blocked" else None
        except Exception:
            return None
    return None


AMB = ((15, "שגריר זהב"), (5, "שגריר מוביל"), (1, "שגריר"))


def amb_level(c, uid):
    n = c.execute("SELECT COUNT(*) FROM credits WHERE user_id=? AND status IN ('pending','approved','paid')", (uid,)).fetchone()[0]
    for need, label in AMB:
        if n >= need:
            return label
    return ""


def shown_rating(p):
    if p["rating_count"] >= 3:
        return round(p["rating_sum"] / p["rating_count"], 1)
    return p["admin_rating"]


def pro_card(p, u, c=None):
    return {"id": u["id"], "name": u["name"], "kind": p["kind"], "field": p["field"], "bio": p["bio"], "exp": p["exp"] or "",
            "photo": "/api/m/photo/%d" % u["id"] if p["photo"] == 2 else "", "photo_status": p["photo"],
            "links": [x for x in (p["links"] or "").split("\n") if x], "level": p["level"],
            "rating": shown_rating(p), "ratings": p["rating_count"],
            "founding": bool(p["founding_until"] and p["founding_until"] > time.time()),
            "ambassador": amb_level(c, u["id"]) if c is not None else ""}


def user_out(c, u):
    o = {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"], "status": u["status"]}
    if u["role"] == "pro":
        p = c.execute("SELECT * FROM pros WHERE user_id=?", (u["id"],)).fetchone()
        if p:
            o["profile"] = pro_card(p, u, c)
    return o


def estimate(cat, level, size):
    s = settings()
    base = s["base"].get(cat, s["base"]["other"]) * s["level_mult"].get(level, 1.0) * s["size_mult"].get(size, 1.0)
    return {"lo": int(base * 0.8 // 10 * 10), "hi": int(-(-base * 1.3 // 10) * 10)}


def photo_path(uid):
    return os.path.join(DIR, "market_photos", "%d.jpg" % int(uid))


def send_photo(h, uid):
    try:
        with open(photo_path(uid), "rb") as f:
            raw = f.read()
    except OSError:
        return h.reply(404, {"error": "not found"})
    h.send_response(200)
    h.send_header("Content-Type", "image/jpeg")
    h.send_header("Content-Length", str(len(raw)))
    h.send_header("Cache-Control", "private, max-age=300")
    h.send_header("X-Content-Type-Options", "nosniff")
    h.end_headers()
    h.wfile.write(raw)


def serve_photo(h, raw_id, viewer):
    try:
        uid = int(raw_id)
    except ValueError:
        return h.reply(404, {"error": "not found"})
    with db() as c:
        p = c.execute("SELECT p.photo, u.status FROM pros p JOIN users u ON u.id=p.user_id WHERE p.user_id=?", (uid,)).fetchone()
    own = viewer is not None and viewer["id"] == uid
    if not p or not p["photo"] or (not own and (p["photo"] != 2 or p["status"] != "active")):
        return h.reply(404, {"error": "not found"})
    return send_photo(h, uid)


def drop_photo(uid):
    try:
        os.remove(photo_path(uid))
    except OSError:
        pass
    with db() as c:
        c.execute("UPDATE pros SET photo=0 WHERE user_id=?", (uid,))


def save_photo(h, u, d):
    import base64
    try:
        raw = base64.b64decode(str(d.get("data") or "").split(",")[-1], validate=False)
    except Exception:
        return h.reply(400, {"error": "bad"})
    if len(raw) < 200 or len(raw) > 500000 or raw[:3] != b"\xff\xd8\xff":
        return h.reply(400, {"error": "type"})
    with open(photo_path(u["id"]), "wb") as f:
        f.write(raw)
    with db() as c:
        c.execute("UPDATE pros SET photo=1 WHERE user_id=?", (u["id"],))
    return h.reply(200, {"ok": True})


def clean_links(text):
    out = []
    for line in str(text or "").replace(",", "\n").split("\n"):
        line = line.strip()
        if re.match(r"^https?://[^\s<>\"']{3,200}$", line):
            out.append(line)
    return "\n".join(out[:5])


# ---------------------------------------------------------------- public API
def handle(h, method, path):
    try:
        return route(h, method, path)
    except ValueError:
        return h.reply(400, {"error": "bad"})
    except Exception:
        return h.reply(500, {"error": "server"})


def route(h, method, path):
    sub = path[len("/api/m/"):]
    if method == "POST" and sub == "photo":
        d = h.body(900000)
    else:
        d = h.body(20000) if method in ("POST", "PUT") else {}
    if method == "GET" and sub == "meta":
        return h.reply(200, {"cats": CATS, "levels": LEVELS, "sizes": SIZES})
    if method == "POST" and sub == "estimate":
        return h.reply(200, estimate(clip(d.get("category"), 20), clip(d.get("level"), 10), clip(d.get("size"), 10)))
    if method == "GET" and sub == "pros":
        with db() as c:
            rows = c.execute("SELECT p.*, u.name, u.id FROM pros p JOIN users u ON u.id=p.user_id "
                             "WHERE u.status='active' AND u.role='pro'").fetchall()
            res = [pro_card(r, {"id": r["id"], "name": r["name"]}, c) for r in rows]
        res.sort(key=lambda x: (-(x["rating"] or 0), -LEVEL_RANK.get(x["level"], 1)))
        return h.reply(200, res)
    if sub == "admin/login" and method == "POST":
        if not admin_pass():
            return h.reply(503, {"error": "admin disabled"})
        if limited("madm" + h.ip(), 10, 900):
            return h.reply(429, {"error": "slow down"})
        if not hmac.compare_digest(clip(d.get("password"), 200).encode(), admin_pass().encode()):
            time.sleep(1)
            return h.reply(401, {"error": "wrong"})
        return h.reply(200, {"ok": True}, {"Set-Cookie": "kt_madmin=%s; Path=/; Max-Age=%d; HttpOnly; Secure; SameSite=Strict" % (admin_token(), 12 * 3600)})
    if sub == "admin/logout" and method == "POST":
        return h.reply(200, {"ok": True}, {"Set-Cookie": "kt_madmin=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"})
    if sub == "admin/me" and method == "GET":
        return h.reply(200 if admin_ok(h) else 401, {"ok": admin_ok(h)})
    if method == "GET" and sub == "categories":
        live = "status IN ('open','taken','done')"
        with db() as c:
            cats = {}
            for k in CATS:
                n = c.execute("SELECT COUNT(*) FROM requests WHERE category=? AND " + live, (k,)).fetchone()[0]
                b = c.execute("SELECT COUNT(*) FROM bids b JOIN requests r ON r.id=b.request_id WHERE r.category=? AND r.status IN ('open','taken','done')", (k,)).fetchone()[0]
                last = c.execute("SELECT MAX(created) FROM requests WHERE category=? AND " + live, (k,)).fetchone()[0]
                cats[k] = {"requests": n, "bids": b, "last": last}
            pros = c.execute("SELECT COUNT(*) FROM users WHERE role='pro' AND status='active'").fetchone()[0]
            done = c.execute("SELECT COUNT(*) FROM requests WHERE status='done'").fetchone()[0]
        return h.reply(200, {"cats": cats, "pros": pros, "done": done})
    if method == "POST" and sub == "register":
        return register(h, d)
    if method == "POST" and sub == "login":
        return login(h, d)
    if method == "POST" and sub == "logout":
        return h.reply(200, {"ok": True}, {"Set-Cookie": "kt_user=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"})
    u = session_user(h)
    if method == "GET" and sub.startswith("photo/"):
        return serve_photo(h, sub[6:], u)
    if method == "GET" and (sub == "feed" or re.match(r"^requests/\d+$", sub)):
        return public_requests(h, sub, u)
    if method == "GET" and sub == "me":
        if not u:
            return h.reply(200, {"user": None})
        with db() as c:
            return h.reply(200, {"user": user_out(c, u)})
    if not u:
        return h.reply(401, {"error": "login"})
    if method == "POST" and sub == "photo" and u["role"] == "pro":
        return save_photo(h, u, d)
    if method == "POST" and sub == "photo/remove" and u["role"] == "pro":
        drop_photo(u["id"])
        return h.reply(200, {"ok": True})
    if method == "PUT" and sub == "profile" and u["role"] == "pro":
        with db() as c:
            c.execute("UPDATE pros SET kind=?, field=?, bio=?, exp=?, links=? WHERE user_id=?",
                      (d.get("kind") if d.get("kind") in ("individual", "company") else "individual",
                       clip(d.get("field"), 80), clip(d.get("bio"), 600), clip(d.get("exp"), 200), clean_links(d.get("links")), u["id"]))
        return h.reply(200, {"ok": True})
    if method == "GET" and sub == "partner":
        with db() as c:
            code = ensure_code(c, u)
            rows = c.execute("SELECT amount, status, created FROM credits WHERE user_id=? ORDER BY id DESC", (u["id"],)).fetchall()
            n = c.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (u["id"],)).fetchone()[0]
        tot = {k: sum(r["amount"] for r in rows if r["status"] == k) for k in ("pending", "approved", "paid")}
        with db() as c2:
            level = amb_level(c2, u["id"])
        return h.reply(200, {"code": code, "referred": n, "unit": UNIT, "totals": tot, "level": level,
                             "credits": [{"amount": r["amount"], "status": r["status"], "at": r["created"]} for r in rows],
                             "reward": settings()["reward"]["amount"]})
    if sub == "chats" or sub.startswith("chats/"):
        return chat_routes(h, method, sub, d, u)
    if u["role"] == "client":
        return client_routes(h, method, sub, d, u)
    if u["role"] == "pro":
        return pro_routes(h, method, sub, d, u)
    return h.reply(404, {"error": "not found"})


def register(h, d):
    ip = h.ip()
    if limited("reg" + ip, 6, 3600):
        return h.reply(429, {"error": "slow down"})
    email = clip(d.get("email"), 120).lower()
    name = clip(d.get("name"), 60)
    pw = str(d.get("password") or "")
    role = d.get("role")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or len(name) < 2 or len(pw) < 8 or len(pw) > 100:
        return h.reply(400, {"error": "fields"})
    if role not in ("client", "pro") or d.get("agree") is not True:
        return h.reply(400, {"error": "agree"})
    status = "active" if role == "client" else "pending"
    with db() as c:
        if c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            return h.reply(409, {"error": "exists"})
        ref = clip(d.get("ref"), 20)
        refu = c.execute("SELECT id FROM users WHERE ref_code=?", (ref,)).fetchone() if ref else None
        cur = c.execute("INSERT INTO users(email,name,pw,role,status,created,terms_at,ref_code,referred_by) VALUES(?,?,?,?,?,?,?,?,?)",
                        (email, name, hash_pw(pw), role, status, int(time.time()), int(time.time()), new_code(c), refu["id"] if refu else None))
        uid = cur.lastrowid
        if role == "pro":
            c.execute("INSERT INTO pros(user_id,kind,field,bio,exp,links) VALUES(?,?,?,?,?,?)",
                      (uid, d.get("kind") if d.get("kind") in ("individual", "company") else "individual",
                       clip(d.get("field"), 80), clip(d.get("bio"), 600), clip(d.get("exp"), 200), clean_links(d.get("links"))))
    return h.reply(200, {"ok": True}, {"Set-Cookie": cookie_for(uid)})


def login(h, d):
    if limited("login" + h.ip(), 12, 900):
        return h.reply(429, {"error": "slow down"})
    email = clip(d.get("email"), 120).lower()
    with db() as c:
        u = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not u or u["status"] == "blocked" or not check_pw(str(d.get("password") or ""), u["pw"]):
        time.sleep(0.7)
        return h.reply(401, {"error": "wrong"})
    return h.reply(200, {"ok": True}, {"Set-Cookie": cookie_for(u["id"])})


def first_name(n):
    parts = (n or "").split()
    return parts[0] if parts else ""


def visible_to(r, u):
    own = u is not None and u["id"] == r["user_id"]
    if own:
        return True
    if r["status"] not in ("open", "taken", "done"):
        return False
    return not (r["only_tagged"] and not (u is not None and r["tagged_pro"] == u["id"]))


def level_taken(c, rid, pro_id, level):
    """First come, first served per level: once a pro of a level has bid, no other pro of that level may."""
    return c.execute("SELECT 1 FROM bids b JOIN pros p ON p.user_id=b.pro_id WHERE b.request_id=? AND b.pro_id<>? AND p.level=?",
                     (rid, pro_id, level)).fetchone() is not None


def feed_row(c, r, u):
    au = c.execute("SELECT name FROM users WHERE id=?", (r["user_id"],)).fetchone()
    o = {"id": r["id"], "title": r["title"], "snippet": (r["descr"] or "")[:140], "category": r["category"], "level": r["level"],
         "status": r["status"], "created": r["created"], "budget": r["budget"], "author": first_name(au["name"] if au else ""),
         "bids": c.execute("SELECT COUNT(*) FROM bids WHERE request_id=?", (r["id"],)).fetchone()[0],
         "chats": c.execute("SELECT COUNT(*) FROM chats WHERE request_id=?", (r["id"],)).fetchone()[0],
         "mine": u is not None and u["id"] == r["user_id"], "for_me": u is not None and r["tagged_pro"] == u["id"],
         "tagged": bool(r["tagged_pro"])}
    if r["size"] and r["category"] in CATS:
        o["estimate"] = estimate(r["category"], r["level"] if r["level"] in LEVEL_RANK else "basic", r["size"])
    return o


def public_requests(h, sub, u):
    from urllib.parse import urlparse, parse_qs
    q = parse_qs(urlparse(h.path).query)
    with db() as c:
        if sub == "feed":
            cat = (q.get("cat") or [""])[0]
            st = (q.get("status") or ["open"])[0]
            text = (q.get("q") or [""])[0].strip()[:60]
            statuses = {"open": ("open",), "taken": ("taken",), "done": ("done",), "all": ("open", "taken", "done")}.get(st, ("open",))
            sql = "SELECT * FROM requests WHERE status IN (%s)" % ",".join("?" * len(statuses))
            args = list(statuses)
            if cat in CATS:
                sql += " AND category=?"
                args.append(cat)
            if text:
                sql += " AND (title LIKE ? OR descr LIKE ?)"
                args += ["%" + text + "%"] * 2
            sql += " ORDER BY id DESC LIMIT 200"
            return h.reply(200, [feed_row(c, r, u) for r in c.execute(sql, args).fetchall() if visible_to(r, u)])
        rid = int(sub.split("/")[1])
        r = c.execute("SELECT * FROM requests WHERE id=?", (rid,)).fetchone()
        if not r or not visible_to(r, u):
            return h.reply(404, {"error": "not found"})
        own = u is not None and u["id"] == r["user_id"]
        o = req_out(c, r, own, u["id"] if u else None)
        au = c.execute("SELECT name FROM users WHERE id=?", (r["user_id"],)).fetchone()
        o.update({"author": first_name(au["name"] if au else ""), "mine": own, "has_pro": bool(r["taken_pro"]),
                  "bids_count": c.execute("SELECT COUNT(*) FROM bids WHERE request_id=?", (rid,)).fetchone()[0],
                  "chats_count": c.execute("SELECT COUNT(*) FROM chats WHERE request_id=?", (rid,)).fetchone()[0],
                  "viewer": "owner" if own else "guest"})
        if own:
            chats = []
            for ch in c.execute("SELECT * FROM chats WHERE request_id=? ORDER BY id", (rid,)).fetchall():
                pu = c.execute("SELECT name FROM users WHERE id=?", (ch["pro_id"],)).fetchone()
                pp = c.execute("SELECT photo FROM pros WHERE user_id=?", (ch["pro_id"],)).fetchone()
                last = c.execute("SELECT text FROM chat_msgs WHERE chat_id=? ORDER BY id DESC LIMIT 1", (ch["id"],)).fetchone()
                chats.append({"id": ch["id"], "name": pu["name"] if pu else "", "photo": "/api/m/photo/%d" % ch["pro_id"] if pp and pp["photo"] == 2 else "",
                              "unread": unread(c, ch, u["id"]), "last": last["text"][:80] if last else ""})
            o["chats"] = chats
        elif u is not None and u["role"] == "pro":
            o["viewer"] = "pro" if u["status"] == "active" else "pending_pro"
            if u["status"] == "active":
                p = c.execute("SELECT * FROM pros WHERE user_id=?", (u["id"],)).fetchone()
                for_me = r["tagged_pro"] == u["id"]
                my = c.execute("SELECT * FROM bids WHERE request_id=? AND pro_id=?", (rid, u["id"])).fetchone()
                blocked = r["status"] == "open" and not for_me and not my and level_taken(c, rid, u["id"], p["level"])
                allowed = pro_can_see(r, u["id"], LEVEL_RANK.get(p["level"], 1))
                o.update({"for_me": for_me, "my_bid": {"price": my["price"], "days": my["days"], "note": my["note"]} if my else None,
                          "can_bid": r["status"] == "open" and allowed and not blocked, "bid_blocked": blocked,
                          "level_too_high": r["status"] == "open" and not allowed, "chat": chat_info(c, rid, u["id"], u["id"])})
                if r["taken_pro"] == u["id"]:
                    cl = c.execute("SELECT name, email FROM users WHERE id=?", (r["user_id"],)).fetchone()
                    o["client"] = {"name": cl["name"], "email": cl["email"], "contact": r["contact"]}
        elif u is not None:
            o["viewer"] = "client"
        return h.reply(200, o)


def req_out(c, r, with_bids, viewer_id=None):
    o = {"id": r["id"], "title": r["title"], "desc": r["descr"], "category": r["category"], "level": r["level"],
         "size": r["size"], "budget": r["budget"], "status": r["status"], "created": r["created"],
         "rated": bool(c.execute("SELECT 1 FROM ratings WHERE request_id=?", (r["id"],)).fetchone()), "has_pro": bool(r["taken_pro"])}
    if r["tagged_pro"]:
        t = c.execute("SELECT name FROM users WHERE id=?", (r["tagged_pro"],)).fetchone()
        o["tagged"] = {"id": r["tagged_pro"], "name": t["name"] if t else "", "only": bool(r["only_tagged"])}
    if r["size"] and r["category"] in CATS:
        o["estimate"] = estimate(r["category"], r["level"] if r["level"] in LEVEL_RANK else "basic", r["size"])
    if with_bids:
        bids = []
        for b in c.execute("SELECT * FROM bids WHERE request_id=? ORDER BY created", (r["id"],)).fetchall():
            u = c.execute("SELECT * FROM users WHERE id=?", (b["pro_id"],)).fetchone()
            p = c.execute("SELECT * FROM pros WHERE user_id=?", (b["pro_id"],)).fetchone()
            if not u or not p or u["status"] != "active":
                continue
            row = {"id": b["id"], "price": b["price"], "days": b["days"], "note": b["note"], "chosen": b["id"] == r["chosen_bid"],
                   "pro": pro_card(p, u, c), "chat": chat_info(c, r["id"], b["pro_id"], viewer_id) if viewer_id else None}
            if b["id"] == r["chosen_bid"]:
                row["pro"]["email"] = u["email"]
            bids.append(row)
        o["bids"] = bids
    return o


def client_routes(h, method, sub, d, u):
    if u["status"] != "active":
        return h.reply(403, {"error": "inactive"})
    if method == "POST" and sub == "requests":
        if limited("req%d" % u["id"], 8, 86400):
            return h.reply(429, {"error": "slow down"})
        title, desc = clip(d.get("title"), 120), clip(d.get("desc"), 3000)
        if len(title) < 3 or len(desc) < 10:
            return h.reply(400, {"error": "fields"})
        cat = d.get("category") if d.get("category") in CATS else "other"
        level = d.get("level") if d.get("level") in LEVEL_RANK else "any"
        size = d.get("size") if d.get("size") in SIZES else "small"
        with db() as c:
            tag = None
            try:
                t = int(d.get("tagged_pro") or 0)
            except (TypeError, ValueError):
                t = 0
            if t and c.execute("SELECT 1 FROM users WHERE id=? AND role='pro' AND status='active'", (t,)).fetchone():
                tag = t
            c.execute("INSERT INTO requests(user_id,title,descr,category,level,size,budget,contact,status,created,tagged_pro,only_tagged) "
                      "VALUES(?,?,?,?,?,?,?,?,'review',?,?,?)",
                      (u["id"], title, desc, cat, level, size, clip(d.get("budget"), 60), clip(d.get("contact"), 150), int(time.time()),
                       tag, 1 if tag and d.get("only_tagged") is True else 0))
        return h.reply(200, {"ok": True})
    with db() as c:
        if method == "GET" and sub == "my/requests":
            rows = c.execute("SELECT * FROM requests WHERE user_id=? ORDER BY id DESC", (u["id"],)).fetchall()
            return h.reply(200, [req_out(c, r, True, u["id"]) for r in rows])
        rid = int(d.get("request_id") or 0)
        r = c.execute("SELECT * FROM requests WHERE id=? AND user_id=?", (rid, u["id"])).fetchone() if rid else None
        if not r:
            return h.reply(404, {"error": "not found"})
        if method == "POST" and sub == "requests/choose" and r["status"] == "open":
            b = c.execute("SELECT * FROM bids WHERE id=? AND request_id=?", (int(d.get("bid_id") or 0), rid)).fetchone()
            if not b:
                return h.reply(404, {"error": "not found"})
            c.execute("UPDATE requests SET status='taken', chosen_bid=?, taken_pro=? WHERE id=?", (b["id"], b["pro_id"], rid))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "requests/found" and r["status"] == "open":
            c.execute("UPDATE requests SET status='taken' WHERE id=?", (rid,))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "requests/reopen" and r["status"] == "taken":
            c.execute("UPDATE requests SET status='open', chosen_bid=NULL, taken_pro=NULL WHERE id=?", (rid,))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "requests/done" and r["status"] in ("taken", "open"):
            c.execute("UPDATE requests SET status='done' WHERE id=?", (rid,))
            award(c, u, rid)
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "requests/close" and r["status"] in ("review", "open"):
            c.execute("UPDATE requests SET status='closed' WHERE id=?", (rid,))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "rate" and r["status"] == "done" and r["taken_pro"]:
            stars = int(d.get("stars") or 0)
            if stars < 1 or stars > 5 or c.execute("SELECT 1 FROM ratings WHERE request_id=?", (rid,)).fetchone():
                return h.reply(400, {"error": "bad"})
            c.execute("INSERT INTO ratings(request_id,pro_id,stars,text,created) VALUES(?,?,?,?,?)",
                      (rid, r["taken_pro"], stars, clip(d.get("text"), 500), int(time.time())))
            c.execute("UPDATE pros SET rating_sum=rating_sum+?, rating_count=rating_count+1 WHERE user_id=?", (stars, r["taken_pro"]))
            return h.reply(200, {"ok": True})
    return h.reply(400, {"error": "bad"})


def pro_routes(h, method, sub, d, u):
    if u["status"] != "active":
        return h.reply(403, {"error": "pending"})
    with db() as c:
        p = c.execute("SELECT * FROM pros WHERE user_id=?", (u["id"],)).fetchone()
        rank = LEVEL_RANK.get(p["level"], 1)
        if method == "GET" and sub == "board":
            out = []
            for r in c.execute("SELECT * FROM requests WHERE status='open' ORDER BY (tagged_pro=?) DESC, id DESC LIMIT 200", (u["id"],)).fetchall():
                for_me = r["tagged_pro"] == u["id"]
                if not pro_can_see(r, u["id"], rank):
                    continue
                o = req_out(c, r, False)
                o["for_me"] = for_me
                o["chat"] = chat_info(c, r["id"], u["id"], u["id"])
                b = c.execute("SELECT * FROM bids WHERE request_id=? AND pro_id=?", (r["id"], u["id"])).fetchone()
                o["my_bid"] = {"price": b["price"], "days": b["days"], "note": b["note"]} if b else None
                out.append(o)
            mine = []
            for r in c.execute("SELECT * FROM requests WHERE taken_pro=? ORDER BY id DESC", (u["id"],)).fetchall():
                o = req_out(c, r, False)
                cl = c.execute("SELECT name, email FROM users WHERE id=?", (r["user_id"],)).fetchone()
                o["client"] = {"name": cl["name"], "email": cl["email"], "contact": r["contact"]}
                o["chat"] = chat_info(c, r["id"], u["id"], u["id"])
                mine.append(o)
            return h.reply(200, {"open": out, "mine": mine})
        if method == "POST" and sub == "bids":
            if limited("bid%d" % u["id"], 60, 86400):
                return h.reply(429, {"error": "slow down"})
            rid = int(d.get("request_id") or 0)
            r = c.execute("SELECT * FROM requests WHERE id=? AND status='open'", (rid,)).fetchone()
            if r and r["only_tagged"] and r["tagged_pro"] != u["id"]:
                r = None
            if not r or (r["tagged_pro"] != u["id"] and r["level"] in LEVEL_RANK and LEVEL_RANK[r["level"]] > rank):
                return h.reply(404, {"error": "not found"})
            price, days = clip(d.get("price"), 40), clip(d.get("days"), 40)
            if not price:
                return h.reply(400, {"error": "fields"})
            mine = c.execute("SELECT 1 FROM bids WHERE request_id=? AND pro_id=?", (rid, u["id"])).fetchone()
            if not mine and r["tagged_pro"] != u["id"] and level_taken(c, rid, u["id"], p["level"]):
                return h.reply(409, {"error": "level_taken"})
            c.execute("INSERT INTO bids(request_id,pro_id,price,days,note,created) VALUES(?,?,?,?,?,?) "
                      "ON CONFLICT(request_id,pro_id) DO UPDATE SET price=excluded.price, days=excluded.days, note=excluded.note",
                      (rid, u["id"], price, days, clip(d.get("note"), 600), int(time.time())))
            return h.reply(200, {"ok": True})
    return h.reply(404, {"error": "not found"})


def award(c, client, rid):
    """A partner earns one pending reward when the client he brought gets his first job done."""
    ref = client["referred_by"]
    if not ref or ref == client["id"]:
        return
    if c.execute("SELECT COUNT(*) FROM requests WHERE user_id=? AND status='done'", (client["id"],)).fetchone()[0] != 1:
        return
    if not c.execute("SELECT 1 FROM users WHERE id=? AND status='active'", (ref,)).fetchone():
        return
    amount = settings()["reward"]["amount"]
    if amount > 0:
        c.execute("INSERT OR IGNORE INTO credits(user_id,referred_id,request_id,amount,created) VALUES(?,?,?,?,?)",
                  (ref, client["id"], rid, amount, int(time.time())))


def sys_client(c):
    """The account under which the admin posts a request on behalf of a business customer."""
    u = c.execute("SELECT id FROM users WHERE email='system@kosher-tek.local'").fetchone()
    if u:
        return u["id"]
    import secrets
    cur = c.execute("INSERT INTO users(email,name,pw,role,status,created,ref_code) VALUES(?,?,?,?,?,?,?)",
                    ("system@kosher-tek.local", "כושר טק (בשם לקוח)", hash_pw(secrets.token_hex(16)), "client", "active", int(time.time()), new_code(c)))
    return cur.lastrowid


def pro_can_see(r, uid, rank):
    if r["tagged_pro"] == uid:
        return True
    if r["only_tagged"]:
        return False
    return not (r["level"] in LEVEL_RANK and LEVEL_RANK[r["level"]] > rank)


def chat_info(c, rid, pro_id, viewer_id):
    ch = c.execute("SELECT * FROM chats WHERE request_id=? AND pro_id=?", (rid, pro_id)).fetchone()
    if not ch:
        return None
    return {"id": ch["id"], "unread": unread(c, ch, viewer_id)}


def unread(c, ch, viewer_id):
    seen = ch["client_read"] if viewer_id == ch["client_id"] else ch["pro_read"]
    return c.execute("SELECT COUNT(*) FROM chat_msgs WHERE chat_id=? AND id>? AND sender_id<>?", (ch["id"], seen, viewer_id)).fetchone()[0]


def chat_routes(h, method, sub, d, u):
    if u["status"] != "active":
        return h.reply(403, {"error": "inactive"})
    parts = sub.split("/")
    with db() as c:
        if method == "POST" and sub == "chats":
            rid = int(d.get("request_id") or 0)
            r = c.execute("SELECT * FROM requests WHERE id=?", (rid,)).fetchone()
            if not r:
                return h.reply(404, {"error": "not found"})
            if u["role"] == "pro":
                p = c.execute("SELECT * FROM pros WHERE user_id=?", (u["id"],)).fetchone()
                ok = r["taken_pro"] == u["id"] or (r["status"] == "open" and pro_can_see(r, u["id"], LEVEL_RANK.get(p["level"], 1)))
                pid, cid = u["id"], r["user_id"]
            else:
                pid = int(d.get("pro_id") or 0)
                has = c.execute("SELECT 1 FROM bids WHERE request_id=? AND pro_id=?", (rid, pid)).fetchone() or r["tagged_pro"] == pid
                act = c.execute("SELECT 1 FROM users WHERE id=? AND role='pro' AND status='active'", (pid,)).fetchone()
                ok = r["user_id"] == u["id"] and has and act and r["status"] != "review"
                cid = u["id"]
            if not ok:
                return h.reply(404, {"error": "not found"})
            c.execute("INSERT OR IGNORE INTO chats(request_id,client_id,pro_id,created) VALUES(?,?,?,?)", (rid, cid, pid, int(time.time())))
            ch = c.execute("SELECT id FROM chats WHERE request_id=? AND pro_id=?", (rid, pid)).fetchone()
            return h.reply(200, {"id": ch["id"]})
        if method == "GET" and sub == "chats":
            col = "client_id" if u["role"] == "client" else "pro_id"
            out = []
            for ch in c.execute("SELECT * FROM chats WHERE %s=? ORDER BY id DESC LIMIT 100" % col, (u["id"],)).fetchall():
                other = ch["pro_id"] if u["role"] == "client" else ch["client_id"]
                ou = c.execute("SELECT name FROM users WHERE id=?", (other,)).fetchone()
                op = c.execute("SELECT photo FROM pros WHERE user_id=?", (other,)).fetchone()
                rq = c.execute("SELECT title FROM requests WHERE id=?", (ch["request_id"],)).fetchone()
                last = c.execute("SELECT text, created FROM chat_msgs WHERE chat_id=? ORDER BY id DESC LIMIT 1", (ch["id"],)).fetchone()
                out.append({"id": ch["id"], "request_id": ch["request_id"], "title": rq["title"] if rq else "", "name": ou["name"] if ou else "",
                            "photo": "/api/m/photo/%d" % other if op and op["photo"] == 2 else "", "unread": unread(c, ch, u["id"]),
                            "last": last["text"][:80] if last else "", "last_at": last["created"] if last else ch["created"]})
            out.sort(key=lambda x: -x["last_at"])
            return h.reply(200, out)
        if len(parts) == 3 and parts[0] == "chats" and parts[1].isdigit():
            ch = c.execute("SELECT * FROM chats WHERE id=?", (int(parts[1]),)).fetchone()
            if not ch or u["id"] not in (ch["client_id"], ch["pro_id"]):
                return h.reply(404, {"error": "not found"})
            if method == "GET" and parts[2] == "messages":
                try:
                    after = int((h.path.split("after=", 1) + ["0"])[1].split("&")[0] or 0)
                except ValueError:
                    after = 0
                rows = c.execute("SELECT id, sender_id, text, created FROM chat_msgs WHERE chat_id=? AND id>? ORDER BY id LIMIT 200", (ch["id"], after)).fetchall()
                if rows:
                    col = "client_read" if u["id"] == ch["client_id"] else "pro_read"
                    c.execute("UPDATE chats SET %s=MAX(%s,?) WHERE id=?" % (col, col), (rows[-1]["id"], ch["id"]))
                return h.reply(200, [{"id": m["id"], "mine": m["sender_id"] == u["id"], "text": m["text"], "at": m["created"]} for m in rows])
            if method == "POST" and parts[2] == "send":
                text = clip(d.get("text"), 1000)
                if not text:
                    return h.reply(400, {"error": "empty"})
                if limited("chat%d" % u["id"], 90, 3600):
                    return h.reply(429, {"error": "slow down"})
                cur = c.execute("INSERT INTO chat_msgs(chat_id,sender_id,text,created) VALUES(?,?,?,?)", (ch["id"], u["id"], text, int(time.time())))
                col = "client_read" if u["id"] == ch["client_id"] else "pro_read"
                c.execute("UPDATE chats SET %s=? WHERE id=?" % col, (cur.lastrowid, ch["id"]))
                return h.reply(200, {"ok": True, "id": cur.lastrowid})
    return h.reply(404, {"error": "not found"})


# ---------------------------------------------------------------- admin API
def admin(h, method, path):
    if not admin_ok(h):
        return h.reply(401, {"error": "login"})
    try:
        return admin_route(h, method, path[len("/api/admin/m/"):])
    except ValueError:
        return h.reply(400, {"error": "bad"})
    except Exception:
        return h.reply(500, {"error": "server"})


def admin_route(h, method, sub):
    d = h.body(20000) if method in ("POST", "PUT") else {}
    if method == "GET" and sub.startswith("photo/"):
        try:
            return send_photo(h, int(sub[6:]))
        except ValueError:
            return h.reply(404, {"error": "not found"})
    with db() as c:
        if method == "GET" and sub == "overview":
            users = []
            for u in c.execute("SELECT * FROM users ORDER BY id DESC").fetchall():
                o = {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"], "status": u["status"]}
                if u["role"] == "pro":
                    p = c.execute("SELECT * FROM pros WHERE user_id=?", (u["id"],)).fetchone()
                    o.update({"kind": p["kind"], "field": p["field"], "bio": p["bio"], "exp": p["exp"], "photo": p["photo"], "links": p["links"], "level": p["level"],
                              "founding": bool(p["founding_until"] and p["founding_until"] > time.time()),
                              "admin_rating": p["admin_rating"], "rating_count": p["rating_count"],
                              "client_rating": round(p["rating_sum"] / p["rating_count"], 1) if p["rating_count"] else None})
                users.append(o)
            reqs = []
            order = {"review": 0, "open": 1, "taken": 2, "done": 3, "closed": 4}
            for r in c.execute("SELECT * FROM requests").fetchall():
                o = req_out(c, r, bool(r["via_admin"]))
                cl = c.execute("SELECT name, email FROM users WHERE id=?", (r["user_id"],)).fetchone()
                o["client"] = {"name": cl["name"], "email": cl["email"], "contact": r["contact"]}
                o["via_admin"] = bool(r["via_admin"])
                o["bids_count"] = c.execute("SELECT COUNT(*) FROM bids WHERE request_id=?", (r["id"],)).fetchone()[0]
                for bd in o.get("bids", []):
                    em = c.execute("SELECT email FROM users WHERE id=?", (bd["pro"]["id"],)).fetchone()
                    bd["pro"]["email"] = em["email"] if em else ""
                reqs.append(o)
            reqs.sort(key=lambda x: (order.get(x["status"], 9), -x["id"]))
            credits = []
            for cr in c.execute("SELECT * FROM credits ORDER BY (status='pending') DESC, id DESC LIMIT 300").fetchall():
                a = c.execute("SELECT name, email FROM users WHERE id=?", (cr["user_id"],)).fetchone()
                b = c.execute("SELECT name FROM users WHERE id=?", (cr["referred_id"],)).fetchone()
                credits.append({"id": cr["id"], "amount": cr["amount"], "status": cr["status"], "partner": a["name"] if a else "", "email": a["email"] if a else "",
                                "referred": b["name"] if b else "", "at": cr["created"]})
            return h.reply(200, {"users": users, "requests": reqs, "credits": credits, "unit": UNIT, "settings": settings(), "labels": {"cats": CATS, "levels": LEVELS, "sizes": SIZES}})
        if method == "POST" and sub == "user":
            uid = int(d.get("id") or 0)
            u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
            if not u:
                return h.reply(404, {"error": "not found"})
            if d.get("status") in ("active", "pending", "blocked"):
                c.execute("UPDATE users SET status=? WHERE id=?", (d["status"], uid))
            if u["role"] == "pro":
                if d.get("level") in LEVEL_RANK:
                    c.execute("UPDATE pros SET level=? WHERE user_id=?", (d["level"], uid))
                if "founding" in d:
                    c.execute("UPDATE pros SET founding_until=? WHERE user_id=?", (int(time.time()) + 365 * 86400 if d["founding"] is True else None, uid))
                if "admin_rating" in d:
                    try:
                        v = None if d["admin_rating"] in ("", None) else max(1.0, min(5.0, float(d["admin_rating"])))
                    except Exception:
                        v = None
                    c.execute("UPDATE pros SET admin_rating=? WHERE user_id=?", (v, uid))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "forward":
            title, desc = clip(d.get("title"), 120), clip(d.get("desc"), 3000)
            if len(title) < 3 or len(desc) < 10:
                return h.reply(400, {"error": "fields"})
            cat = d.get("category") if d.get("category") in CATS else "other"
            level = d.get("level") if d.get("level") in LEVEL_RANK else "any"
            c.execute("INSERT INTO requests(user_id,title,descr,category,level,size,budget,contact,status,created,via_admin) "
                      "VALUES(?,?,?,?,?,?,?,?,'open',?,1)",
                      (sys_client(c), title, desc, cat, level, d.get("size") if d.get("size") in SIZES else "small",
                       clip(d.get("budget"), 60), clip(d.get("contact"), 150), int(time.time())))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "choose":
            rid = int(d.get("request_id") or 0)
            r = c.execute("SELECT * FROM requests WHERE id=? AND via_admin=1 AND status='open'", (rid,)).fetchone()
            b = c.execute("SELECT * FROM bids WHERE id=? AND request_id=?", (int(d.get("bid_id") or 0), rid)).fetchone() if r else None
            if not b:
                return h.reply(404, {"error": "not found"})
            c.execute("UPDATE requests SET status='taken', chosen_bid=?, taken_pro=? WHERE id=?", (b["id"], b["pro_id"], rid))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "credit":
            if d.get("status") not in ("pending", "approved", "paid", "rejected"):
                return h.reply(400, {"error": "bad"})
            c.execute("UPDATE credits SET status=? WHERE id=?", (d["status"], int(d.get("id") or 0)))
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "photo":
            uid = int(d.get("id") or 0)
            if d.get("ok") is True:
                c.execute("UPDATE pros SET photo=2 WHERE user_id=? AND photo>0", (uid,))
            else:
                drop_photo(uid)
            return h.reply(200, {"ok": True})
        if method == "POST" and sub == "request":
            if d.get("status") not in STATUS_REQ:
                return h.reply(400, {"error": "bad"})
            c.execute("UPDATE requests SET status=? WHERE id=?", (d["status"], int(d.get("id") or 0)))
            return h.reply(200, {"ok": True})
    if method == "PUT" and sub == "settings":
        new = settings()
        for part in new:
            for k in new[part]:
                try:
                    v = float(d.get(part, {}).get(k, new[part][k]))
                    new[part][k] = v if 0 <= v <= 1000000 else new[part][k]
                except Exception:
                    pass
        tmp = SETTINGS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(new, f)
        os.replace(tmp, SETTINGS_FILE)
        return h.reply(200, {"ok": True})
    return h.reply(404, {"error": "not found"})
