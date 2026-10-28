(function () {
  var $ = function (id) { return document.getElementById(id); };
  function showLogin() { $("app").hidden = true; $("login").hidden = false; $("pw").focus(); }
  function showApp() { $("login").hidden = true; $("app").hidden = false; }
  document.querySelectorAll(".tabs button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".tabs button").forEach(function (x) { x.className = x === b ? "on" : ""; });
      document.querySelectorAll(".panel").forEach(function (p) { p.classList.toggle("on", p.id === "p-" + b.dataset.tab); });
    });
  });
  function login() {
    $("loginmsg").textContent = "";
    fetch("/api/m/admin/login", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password: $("pw").value }) })
      .then(function (r) {
        if (r.ok) { $("pw").value = ""; showApp(); }
        else $("loginmsg").textContent = r.status === 429 ? "יותר מדי ניסיונות, נסה שוב מאוחר יותר." : r.status === 503 ? "הניהול לא מוגדר בשרת." : "סיסמה שגויה.";
      }).catch(function () { $("loginmsg").textContent = "אין חיבור לשרת."; });
  }
  $("go").addEventListener("click", login);
  $("pw").addEventListener("keydown", function (e) { if (e.key === "Enter") login(); });
  $("out").addEventListener("click", function () { fetch("/api/m/admin/logout", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: "{}" }).then(showLogin); });
  fetch("/api/m/admin/me", { credentials: "same-origin" }).then(function (r) { r.ok ? showApp() : showLogin(); }).catch(showLogin);
})();
(function () {
  var data = null;
  var STAT = { review: "ממתינה לאישור", open: "פתוחה", taken: "נלקחה", done: "בוצעה", closed: "סגורה" };
  var ROLE = { client: "מבקש", pro: "איש מקצוע / חברה" };
  var UST = { active: "פעיל", pending: "ממתין לאישור", blocked: "חסום" };
  var SIZEMAP, LEVELMAP, CATMAP, ufilter = "all";

  function el(tag, props, kids) {
    var e = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) {
      if (k === "text") e.textContent = props[k]; else if (k === "cls") e.className = props[k]; else e[k] = props[k];
    });
    (kids || []).forEach(function (c) { if (c) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function note(t) {
    var s = document.getElementById("status"); s.textContent = t; s.classList.add("show");
    clearTimeout(note.t); note.t = setTimeout(function () { s.classList.remove("show"); }, 2500);
  }
  function call(method, url, body) {
    return fetch("/api/admin/m/" + url, { method: method, credentials: "same-origin",
      headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  function btn(t, fn, danger) {
    var b = el("button", { type: "button", cls: "sm" + (danger ? " danger" : ""), text: t }); b.addEventListener("click", fn); return b;
  }
  function sel(map, value) {
    var s = el("select"); Object.keys(map).forEach(function (k) { var o = el("option", { value: k, text: map[k] }); if (k === value) o.selected = true; s.appendChild(o); }); return s;
  }

  function render() {
    SIZEMAP = data.labels.sizes; LEVELMAP = data.labels.levels; CATMAP = data.labels.cats;
    var pending = data.users.filter(function (u) { return u.status === "pending" || u.photo === 1 || u.cover === 1; }).length;
    var review = data.requests.filter(function (r) { return r.status === "review"; }).length;
    document.getElementById("ucount").textContent = pending ? "(" + pending + ")" : "";
    document.getElementById("rcount").textContent = review ? "(" + review + ")" : "";

    var ul = document.getElementById("ulist"); ul.textContent = "";
    var FILT = [["all", "כולם"], ["pending", "ממתינים לאישור"], ["pro", "אנשי מקצוע"], ["client", "מבקשים"], ["blocked", "חסומים"]];
    var bar = el("div", { cls: "seg" });
    FILT.forEach(function (f) {
      var b = el("button", { type: "button", cls: ufilter === f[0] ? "on" : "", text: f[1] });
      b.addEventListener("click", function () { ufilter = f[0]; render(); });
      bar.appendChild(b);
    });
    ul.appendChild(el("div", { cls: "toolbar" }, [bar]));
    var shown = data.users.filter(function (u) {
      return ufilter === "all" || (ufilter === "pending" ? (u.status === "pending" || u.photo === 1 || u.cover === 1) : ufilter === "blocked" ? u.status === "blocked" : u.role === ufilter);
    });
    shown.forEach(function (u) {
      var stCls = u.status === "active" ? "st-open" : u.status === "pending" ? "st-review" : "st-closed";
      var head = el("div", { cls: "uhead" }, [el("strong", { text: u.name }),
        el("span", { cls: "chip " + stCls, text: UST[u.status] }), el("span", { cls: "chip", text: ROLE[u.role] }),
        u.role === "pro" ? el("span", { cls: "chip cat", text: (LEVELMAP[u.level] || "").split(" (")[0] }) : null]);
      var lines = [head, el("div", { cls: "meta", text: u.email })];
      var lvl, rating;
      if (u.role === "client") {
        lines.push(el("div", { cls: "meta", text: "מבקשים נכנסים מיד ולא צריכים אישור. כל בקשה שהם מפרסמים ממתינה לאישורך בלשונית \"בקשות\"." }));
      }
      if (u.role === "pro") {
        lines.push(el("div", { cls: "meta", text: [u.kind === "company" ? "חברה" : "איש מקצוע פרטי", u.field, u.exp ? "ניסיון: " + u.exp : ""].filter(Boolean).join(" · ") }));
        if (u.bio) lines.push(el("p", { cls: "msg", text: u.bio }));
        if (u.links) lines.push(el("div", { cls: "meta", text: u.links.replace(/\n/g, "  ") }));
        lines.push(el("div", { cls: "meta", text: "דירוג לקוחות: " + (u.client_rating ? u.client_rating + " (" + u.rating_count + ")" : "עדיין אין") }));
        if (u.photo) {
          var im = el("img", { cls: "thumb", alt: "", src: "/api/admin/m/photo/" + u.id + "?t=" + Date.now() });
          lines.push(el("div", { cls: "who" }, [im, el("span", { cls: "meta", text: u.photo === 1 ? "תמונה ממתינה לאישור" : "תמונה מאושרת" })]));
        }
        if (u.cover) {
          var cv = el("img", { cls: "thumb wide", alt: "", src: "/api/admin/m/cover/" + u.id + "?t=" + Date.now() });
          lines.push(el("div", { cls: "who" }, [cv, el("span", { cls: "meta", text: u.cover === 1 ? "רקע ממתין לאישור" : "רקע מאושר" })]));
        }
        if (u.status === "pending") lines.push(el("div", { cls: "note", text: "איש המקצוע ממתין לאישור. עד האישור הוא לא יכול להגיש הצעות או לפתוח שיחות." }));
        lvl = sel(LEVELMAP, u.level);
        rating = el("input", { type: "number", min: 1, max: 5, step: 0.5, value: u.admin_rating == null ? "" : u.admin_rating, placeholder: "1 עד 5" });
      }
      var acts = el("div", { cls: "act" });
      function set(extra) { call("POST", "user", Object.assign({ id: u.id }, extra)).then(function () { note("נשמר"); load(); }).catch(function () { note("השמירה נכשלה"); }); }
      if (u.status === "pending") acts.appendChild(el("button", { type: "button", cls: "btn primary sm", text: "אישור הצטרפות", onclick: function () { set({ status: "active" }); } }));
      if (u.status === "blocked") acts.appendChild(btn("ביטול חסימה", function () { set({ status: "active" }); }));
      if (u.role === "pro" && u.photo === 1) acts.appendChild(btn("אישור תמונה", function () { call("POST", "photo", { id: u.id, ok: true }).then(function () { note("נשמר"); load(); }); }));
      if (u.role === "pro" && u.cover === 1) acts.appendChild(btn("אישור רקע", function () { call("POST", "cover", { id: u.id, ok: true }).then(function () { note("נשמר"); load(); }); }));
      if (u.role === "pro" && u.cover) acts.appendChild(btn("הסרת רקע", function () { call("POST", "cover", { id: u.id, ok: false }).then(function () { note("נשמר"); load(); }); }, true));
      if (u.role === "pro" && u.photo) acts.appendChild(btn("הסרת תמונה", function () { call("POST", "photo", { id: u.id, ok: false }).then(function () { note("נשמר"); load(); }); }, true));
      if (u.status !== "blocked") acts.appendChild(btn("חסימה", function () { ktAsk("לחסום את " + u.name + "?", { danger: true }).then(function (ok) { if (ok) set({ status: "blocked" }); }); }, true));
      var kids = lines.slice();
      if (u.role === "pro") {
        kids.push(el("div", { cls: "usettings" }, [el("label", { cls: "f", text: "רמה" }, [lvl]), el("label", { cls: "f", text: "דירוג הנהלה" }, [rating]),
          btn("שמירה", function () { set({ level: lvl.value, admin_rating: rating.value }); })]));
      }
      kids.push(acts);
      ul.appendChild(el("div", { cls: "box ucard" + (u.status === "pending" ? " pend" : "") }, kids));
    });
    if (!shown.length && data.users.length) ul.appendChild(el("p", { cls: "meta", text: "אין משתמשים בסינון הזה." }));
    if (!data.users.length) ul.appendChild(el("p", { cls: "meta", text: "אין משתמשים." }));

    var rl = document.getElementById("rlist"); rl.textContent = "";
    data.requests.forEach(function (r) {
      var acts = el("div", { cls: "act" });
      function setS(s) { call("POST", "request", { id: r.id, status: s }).then(function () { note("נשמר"); load(); }); }
      if (r.status === "review") acts.appendChild(btn("אישור ופרסום", function () { setS("open"); }));
      if (r.status !== "closed") acts.appendChild(btn("סגירה", function () { ktAsk("לסגור?", { danger: true }).then(function (ok) { if (ok) setS("closed"); }); }, true));
      var bidsBox = null;
      if (r.via_admin && r.bids && r.bids.length) {
        bidsBox = el("div", {}, [el("div", { cls: "meta", text: "הצעות (פרטי הקשר למסירה ללקוח):" })]);
        r.bids.forEach(function (b) {
          var row = el("div", { cls: "msg", text: b.pro.name + " · " + b.pro.email + " · מחיר: " + b.price + (b.days ? " · זמן: " + b.days : "") + (b.note ? " · " + b.note : "") + (b.chosen ? " · נבחר" : "") });
          if (r.status === "open") row.appendChild(btn(" בחירה בהצעה", function () { ktAsk("לבחור בהצעה הזאת?").then(function (ok) { if (ok) call("POST", "choose", { request_id: r.id, bid_id: b.id }).then(function () { note("נשמר"); load(); }); }); }));
          bidsBox.appendChild(row);
        });
      }
      rl.appendChild(el("div", { cls: "box" }, [el("strong", { text: r.title }),
        el("div", { cls: "meta", text: (r.via_admin ? "מטעם כושר טק · " : "") + STAT[r.status] + " · " + (CATMAP[r.category] || "") + " · הצעות: " + r.bids_count + " · לקוח: " + r.client.name + " · " + r.client.email + (r.client.contact ? " · " + r.client.contact : "") }),
        el("p", { cls: "msg", text: r.desc }), bidsBox, acts]));
    });
    if (!data.requests.length) rl.appendChild(el("p", { cls: "meta", text: "אין בקשות." }));

    var cl = document.getElementById("clist"); cl.textContent = "";
    document.getElementById("pcount").textContent = "";
    var KIND = { signup: "נרשם דרכו", order: "בונוס: הזמין עבודה" };
    data.credits.forEach(function (c) {
      var off = c.status === "rejected";
      var acts = el("div", { cls: "act" }, [off ? btn("החזרה", function () { call("POST", "credit", { id: c.id, status: "approved" }).then(function () { note("נשמר"); load(); }); })
        : btn("ביטול (למשל הרשמה מזויפת)", function () { ktAsk("לבטל את התגמול?", { danger: true }).then(function (ok) { if (ok) call("POST", "credit", { id: c.id, status: "rejected" }).then(function () { note("נשמר"); load(); }); }); }, true)]);
      cl.appendChild(el("div", { cls: "box" + (off ? " done" : "") }, [el("strong", { text: c.partner + " · " + c.amount + " " + data.unit + (off ? " · בוטל" : "") }),
        el("div", { cls: "meta", text: KIND[c.kind] + ": " + c.referred + " · " + c.email }), acts]));
    });
    if (!data.credits.length) cl.appendChild(el("p", { cls: "meta", text: "אין תגמולים עדיין. כל מי שנרשם דרך קישור של משתמש מזכה אותו מיד, ואם הוא גם מזמין עבודה, בבונוס נוסף." }));

    var eb = document.getElementById("elist"); eb.textContent = "";
    var inputs = {};
    function group(title, part, labels, hint) {
      var row = el("div", { cls: "row" });
      Object.keys(labels).forEach(function (k) {
        var i = el("input", { type: "number", min: 0, step: "any", value: data.settings[part][k] });
        inputs[part + "." + k] = i;
        row.appendChild(el("label", { cls: "f", text: labels[k] }, [i]));
      });
      eb.appendChild(el("div", { cls: "box" }, [el("strong", { text: title }), el("p", { cls: "meta", text: hint }), row]));
    }
    group("מחיר בסיס לפי תחום (ש\"ח)", "base", CATMAP, "עבודה קטנה ברמה בסיסית.");
    group("מכפיל לפי רמה", "level_mult", LEVELMAP, "מוכפל במחיר הבסיס.");
    group("מכפיל לפי גודל", "size_mult", SIZEMAP, "מוכפל במחיר הבסיס.");
    group("תגמול שותפים", "reward", { amount: "על כל מי שנרשם דרך הקישור (" + data.unit + ")", bonus: "בונוס כשהוא גם מזמין עבודה (" + data.unit + ")" }, "ניתן מיד, בלי שלבי אישור. אפשר לבטל תגמול חשוד בלשונית שותפים.");
    eb.appendChild(el("p", { cls: "meta", text: "מחירי הבסיס והמכפילים לשימוש פנימי שלך בלבד. הם לא מוצגים למשתמשים." }));
    document.getElementById("saveest").onclick = function () {
      var out = { base: {}, level_mult: {}, size_mult: {}, reward: {} };
      Object.keys(inputs).forEach(function (k) { var p = k.split("."); out[p[0]][p[1]] = Number(inputs[k].value); });
      call("PUT", "settings", out).then(function () { note("נשמר"); load(); }).catch(function () { note("השמירה נכשלה"); });
    };
  }
  function load() { return call("GET", "overview").then(function (d) { data = d; render(); }).catch(function () {}); }

  document.querySelectorAll(".tabs button").forEach(function (b) {
    b.addEventListener("click", function () { if (["users", "mreq", "partners", "est"].indexOf(b.dataset.tab) >= 0) load(); });
  });

  // load once the admin shell is visible (it logs in or restores the session itself)
  var tries = 0;
  (function wait() {
    if (!document.getElementById("app").hidden) return load();
    if (++tries < 200) setTimeout(wait, 300);
  })();
  document.getElementById("go").addEventListener("click", function () { tries = 0; setTimeout(function () { (function w() { if (!document.getElementById("app").hidden) load(); else if (++tries < 40) setTimeout(w, 300); })(); }, 300); });
})();

(function () {
  function el(t, cls, txt) { var e = document.createElement(t); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function call(m, u, b) {
    return fetch("/api/admin/m/" + u, { method: m, credentials: "same-origin", headers: b ? { "Content-Type": "application/json" } : {}, body: b ? JSON.stringify(b) : undefined })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  function load() {
    call("GET", "contact").then(function (rows) {
      var box = document.getElementById("klist"); box.textContent = "";
      var open = rows.filter(function (r) { return !r.done; }).length;
      document.getElementById("kcount").textContent = open ? "(" + open + ")" : "";
      if (!rows.length) box.appendChild(el("p", "meta", "אין פניות."));
      rows.forEach(function (r) {
        var card = el("div", "card" + (r.done ? " done" : ""));
        card.appendChild(el("strong", "", (r.subject || "ללא נושא") + (r.done ? " · טופל" : "")));
        card.appendChild(el("p", "meta", r.name + " · " + r.contact + " · " + new Date(r.created * 1000).toLocaleString("he-IL") + (r.user_id ? " · משתמש רשום #" + r.user_id : "")));
        var msg = el("p", "", r.message); msg.style.whiteSpace = "pre-wrap"; card.appendChild(msg);
        var act = el("div", "act"), d = el("button", "btn sm", r.done ? "סמן כפתוח" : "סמן כטופל"), x = el("button", "btn sm", "מחיקה");
        d.type = x.type = "button";
        d.onclick = function () { call("POST", "contact/done", { id: r.id }).then(load); };
        x.onclick = function () { ktAsk("למחוק את הפנייה?", { danger: true }).then(function (ok) { if (ok) call("POST", "contact/delete", { id: r.id }).then(load); }); };
        act.appendChild(d); act.appendChild(x); card.appendChild(act); box.appendChild(card);
      });
    }).catch(function () {});
  }
  var tries = 0;
  (function wait() { if (!document.getElementById("app").hidden) return load(); if (++tries < 200) setTimeout(wait, 300); })();
  document.querySelectorAll(".tabs button").forEach(function (b) { b.addEventListener("click", function () { if (b.dataset.tab === "contact") load(); }); });
})();
