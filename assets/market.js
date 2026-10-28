(function () {
  var root = document.getElementById("mk");
  var meta = { cats: {}, levels: {}, sizes: {} };
  var me = null;
  try {
    var rq = new URLSearchParams(location.search).get("ref");
    if (rq && /^[0-9a-f]{4,20}$/.test(rq)) localStorage.setItem("mk_ref", rq);
  } catch (e) {}
  function savedRef() { try { return localStorage.getItem("mk_ref") || ""; } catch (e) { return ""; } }
  var STATUS = { review: "ממתינה לאישור הנהלה", open: "מחפש בעל מקצוע", taken: "נמצא בעל מקצוע", done: "בוצעה", closed: "סגורה" };
  var CAT_DESC = { software: "כלים, סקריפטים ותוכנות בהתאמה אישית", website: "אתרים ודפי נחיתה", device: "התאמת מכשירים ומחשבים",
    design: "עיצוב גרפי ומיתוג", writing: "כתיבה, עריכה, הגהה ותרגום", help: "הדרכה, ייעוץ ועזרה טכנית", other: "כל נושא אחר" };

  function el(tag, props, kids) {
    var e = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) {
      if (k === "text") e.textContent = props[k]; else if (k === "cls") e.className = props[k]; else e[k] = props[k];
    });
    (kids || []).forEach(function (c) { if (c) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function api(method, url, body) {
    return fetch("/api/m/" + url, { method: method, credentials: "same-origin",
      headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j.__status = r.status; return j; }); });
  }
  function field(label, input) { return el("label", { cls: "mf" }, [el("span", { text: label }), input]); }
  function select(map, value, any, mapDisplay) {
    var s = el("select");
    if (any) s.appendChild(el("option", { value: "any", text: any }));
    Object.keys(map).forEach(function (k) { var o = el("option", { value: k, text: (mapDisplay || map)[k] }); if (k === value) o.selected = true; s.appendChild(o); });
    return s;
  }
  function levelShort(l) { return l === "any" ? "כל רמה" : (meta.levels[l] || "").split(" (")[0]; }
  function msgBox() { return el("div", { cls: "mmsg", role: "status" }); }
  function stars(p) { return p.rating ? " · דירוג " + p.rating + (p.ratings ? " (" + p.ratings + ")" : "") : ""; }
  function proLine(p) {
    return (p.kind === "company" ? "חברה" : "איש מקצוע") + " · " + levelShort(p.level) + stars(p) + (p.ambassador ? " · " + p.ambassador : "");
  }
  function section(title, kids) { return el("section", { cls: "card mk-sec" }, [el("h3", { text: title })].concat(kids)); }
  var drawer = null, pulling = null;
  function closeChat() { if (drawer) { drawer.remove(); drawer = null; } clearInterval(pulling); }
  function openChat(id, title) {
    closeChat();
    var list = el("div", { cls: "cm-list" }), inp = el("input", { placeholder: "הודעה...", maxLength: 1000 });
    var send = el("button", { cls: "btn primary sm", type: "button", text: "שליחה" }), x = el("button", { cls: "cm-x", type: "button", text: "×", title: "סגירה" });
    drawer = el("div", { cls: "cm" }, [el("div", { cls: "cm-head" }, [el("strong", { text: title }), x]), list, el("div", { cls: "cm-in" }, [inp, send])]);
    document.body.appendChild(drawer);
    var last = 0;
    function pull() {
      api("GET", "chats/" + id + "/messages?after=" + last).then(function (rows) {
        if (!Array.isArray(rows) || !rows.length) return;
        rows.forEach(function (msg) { last = Math.max(last, msg.id); list.appendChild(el("div", { cls: "cm-b " + (msg.mine ? "mine" : "theirs"), text: msg.text })); });
        list.scrollTop = list.scrollHeight;
      });
    }
    function sendMsg() {
      var t = inp.value.trim(); if (!t) return; inp.value = "";
      api("POST", "chats/" + id + "/send", { text: t }).then(pull);
    }
    send.addEventListener("click", sendMsg);
    inp.addEventListener("keydown", function (e) { if (e.key === "Enter") sendMsg(); });
    x.addEventListener("click", closeChat);
    pull(); pulling = setInterval(pull, 3500); inp.focus();
  }
  function startChat(body, title) {
    api("POST", "chats", body).then(function (r) { if (r.id) openChat(r.id, title); });
  }
  function copyText(t, btn, done) {
    function ok() { if (btn) { var o = btn.textContent; btn.textContent = done || "הועתק"; setTimeout(function () { btn.textContent = o; }, 1800); } }
    try { navigator.clipboard.writeText(t).then(ok, function () { window.prompt("העתק את הקישור:", t); }); } catch (e) { window.prompt("העתק את הקישור:", t); }
  }
  function shareButtons(subject, text, url) {
    var c = el("button", { cls: "btn ghost sm", type: "button", text: "העתקת קישור לשיתוף" });
    c.addEventListener("click", function () { copyText(url, c); });
    var mail = el("a", { cls: "btn ghost sm", text: "שליחה במייל", href: "mailto:?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(text + "\n" + url) });
    return [c, mail];
  }
  function profileLink(id, code) {
    return location.origin + location.pathname + (code ? "?ref=" + code : "") + "#/pro/" + id;
  }
  function shareProfile(p) {
    var box = el("div", { cls: "act" });
    function build(code) {
      shareButtons(p.name, p.name + (p.field ? " · " + p.field : ""), profileLink(p.id, code)).forEach(function (b) { box.appendChild(b); });
    }
    if (me) api("GET", "partner").then(function (r) { build(r.code); }); else build("");
    return box;
  }
  function chatsStrip(always) {
    var box = el("section", { cls: "card mk-sec cm-strip" }), started = false;
    if (!always) box.style.display = "none";
    function load() {
      if (started && !box.isConnected) return clearInterval(timer);
      started = true;
      api("GET", "chats").then(function (rows) {
        box.textContent = "";
        if (!Array.isArray(rows) || !rows.length) {
          if (always) box.appendChild(el("p", { cls: "meta", text: "אין שיחות עדיין. אפשר לפתוח שיחה מתוך כל הצעה או בקשה." }));
          else box.style.display = "none";
          return;
        }
        box.style.display = "";
        var total = rows.reduce(function (n, c) { return n + c.unread; }, 0);
        box.appendChild(el("h3", { text: "הצ'אטים שלי" + (total ? " · הודעות חדשות: " + total : "") }));
        rows.forEach(function (c) {
          var row = el("button", { type: "button", cls: "cm-row" }, [avatar({ name: c.name, photo: c.photo }),
            el("span", { cls: "cm-txt" }, [el("strong", { text: c.name + " · " + c.title }), el("span", { cls: "meta", text: c.last })]),
            c.unread ? el("span", { cls: "cm-badge", text: String(c.unread) }) : null]);
          row.addEventListener("click", function () { openChat(c.id, c.name + " · " + c.title); });
          box.appendChild(row);
        });
      });
    }
    var timer = setInterval(load, 15000);
    setTimeout(load, 0);
    return box;
  }

  function partnerBox() {
    var box = el("section", { cls: "card mk-sec" });
    api("GET", "partner").then(function (p) {
      if (!p.code) return;
      var link = location.origin + location.pathname + "?ref=" + p.code;
      var inp = el("input", { value: link, readOnly: true });
      var cp = el("button", { cls: "btn primary", type: "button", text: "העתקת הקישור" });
      cp.addEventListener("click", function () { copyText(link, cp); });
      box.appendChild(el("h3", { text: "הקישור האישי שלך" }));
      box.appendChild(el("p", { text: "משתפים את הקישור. כל מי שנרשם דרכו מזכה אותך מיד ב-" + p.reward + " " + p.unit + ", ואם הוא גם מזמין עבודה מקבלים בונוס של עוד " + p.bonus + " " + p.unit + "." }));
      box.appendChild(el("div", { cls: "linkrow" }, [inp, cp]));
      box.appendChild(el("div", { cls: "act" }, shareButtons("מקום לבקש עבודה ולקבל הצעות", "מקום לבקש עבודה, תוכנה או שירות ולקבל הצעות מאנשי מקצוע מאושרים:", link).slice(1)));
      box.appendChild(el("div", { cls: "stats three" }, [
        el("div", { cls: "stat" }, [el("b", { text: String(p.signups) }), el("span", { text: "נרשמו דרכך" })]),
        el("div", { cls: "stat" }, [el("b", { text: String(p.orders) }), el("span", { text: "גם הזמינו עבודה" })]),
        el("div", { cls: "stat" }, [el("b", { text: String(Math.round(p.total)) }), el("span", { text: p.unit + " שצברת" })])]));
      if (p.level) box.appendChild(el("p", { cls: "mk-ok", text: "הדרגה שלך: " + p.level }));
    });
    return box;
  }

  function rulesBox(onEnd) {
    var box = el("div", { cls: "rules-scroll", tabIndex: 0 }, [el("p", { cls: "meta", text: "טוען את הכללים..." })]);
    var done = false;
    function check() {
      if (done) return;
      if (box.scrollTop + box.clientHeight >= box.scrollHeight - 6) { done = true; onEnd(); }
    }
    box.addEventListener("scroll", check);
    fetch("/market/rules.json").then(function (r) { return r.json(); }).then(function (rules) {
      box.textContent = "";
      rules.forEach(function (sec) {
        box.appendChild(el("h4", { text: sec.title }));
        var ul = el("ul"); sec.items.forEach(function (t) { ul.appendChild(el("li", { text: t })); }); box.appendChild(ul);
      });
      setTimeout(check, 50);
    }).catch(function () { box.textContent = "לא ניתן לטעון את הכללים. נסה שוב מאוחר יותר."; });
    return box;
  }
  function avatar(p, big, size) {
    var box = el("span", { cls: "avatar" + (big ? " big" : "") + (size ? " " + size : "") });
    if (p.photo) { var i = el("img", { alt: "", src: p.photo + "?v=" + (p.photo_status || 0), loading: "lazy" }); box.appendChild(i); }
    else box.textContent = (p.name || "?").trim().charAt(0);
    return box;
  }
  function shrinkPhoto(file) {
    return new Promise(function (res, rej) {
      var img = new Image(), u = URL.createObjectURL(file);
      img.onload = function () {
        var m = 400, s = Math.min(1, m / Math.max(img.width, img.height)), c = document.createElement("canvas");
        c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(u);
        res(c.toDataURL("image/jpeg", 0.82));
      };
      img.onerror = rej; img.src = u;
    });
  }
  function linksOf(p) {
    return (p.links || []).map(function (u) {
      var a = el("a", { text: u, href: u, target: "_blank", rel: "noopener noreferrer nofollow" });
      a.style.display = "block"; return a;
    });
  }


  function authView(startMode) {
    var wrap = el("div", { cls: "mk-auth" });
    var lm = msgBox();
    var le = el("input", { type: "email", autocomplete: "email" }), lp = el("input", { type: "password", autocomplete: "current-password" });
    var lb = el("button", { cls: "btn primary", type: "button", text: "כניסה" });
    lb.addEventListener("click", function () {
      lm.textContent = "";
      api("POST", "login", { email: le.value, password: lp.value }).then(function (r) {
        if (r.ok) return load();
        lm.textContent = r.__status === 429 ? "יותר מדי ניסיונות, נסה שוב מאוחר יותר." : "אימייל או סיסמה שגויים.";
      });
    });
    var loginSec = section("התחברות", [field("אימייל", le), field("סיסמה", lp), lb, lm]);

    function regForm(role) {
      var m = msgBox(), name = el("input", { autocomplete: "name" }), email = el("input", { type: "email", autocomplete: "email" }),
        pw = el("input", { type: "password", autocomplete: "new-password", placeholder: "לפחות 8 תווים" });
      var kind = select({ individual: "איש מקצוע פרטי", company: "חברה" }, "individual"), fld = el("input", { placeholder: "למשל: פיתוח תוכנה עם AI" }),
        expi = el("input", { placeholder: "למשל: 5 שנים בפיתוח" }),
        bio = el("textarea", { rows: 3 }), links = el("textarea", { rows: 2, placeholder: "כתובת בכל שורה (https://...)" });
      var agree = el("input", { type: "checkbox", disabled: true });
      var box = rulesBox(function () { agree.disabled = false; hint.textContent = ""; });
      var hint = el("div", { cls: "meta", text: "יש לקרוא את הכללים עד הסוף כדי להירשם." });
      var ag = el("label", { cls: "mk-agree" }, [agree, el("span", { text: "קראתי את כללי הלוח עד הסוף ואני מסכים להם, ובכלל זה שבעתיד תיגבה עמלה על עבודות." })]);
      var b = el("button", { cls: "btn primary", type: "button", text: role === "client" ? "הרשמה" : "שליחת בקשת הצטרפות" });
      b.addEventListener("click", function () {
        m.textContent = "";
        if (!agree.checked) { m.textContent = "יש לקרוא את כללי הלוח עד הסוף ולאשר אותם."; return; }
        var body = { role: role, name: name.value, email: email.value, password: pw.value, agree: true, ref: savedRef() };
        if (role === "pro") { body.kind = kind.value; body.field = fld.value; body.exp = expi.value; body.bio = bio.value; body.links = links.value; }
        api("POST", "register", body).then(function (r) {
          if (r.ok) return load();
          m.textContent = r.__status === 409 ? "האימייל כבר רשום." : r.__status === 429 ? "יותר מדי ניסיונות." : "נא למלא שם, אימייל תקין וסיסמה של 8 תווים לפחות.";
        });
      });
      var kids = [field("שם", name), field("אימייל", email), field("סיסמה", pw)];
      if (role === "pro") kids.push(field("סוג", kind), field("תחום", fld), field("ניסיון", expi), field("על עצמך או על החברה", bio), field("קישורים", links));
      kids.push(el("strong", { text: "כללי הלוח" }), box, hint, ag, b, m);
      return section(role === "client" ? "הרשמה: מבקש עבודה" : "הרשמה: איש מקצוע או חברה", kids);
    }
    var tabs = el("div", { cls: "mk-tabs" }), holder = el("div"), mode = startMode || "login", role = "client";
    function btnTab(label, active, fn) {
      var b = el("button", { type: "button", cls: active ? "on" : "", text: label }); b.addEventListener("click", fn); return b;
    }
    function draw() {
      tabs.textContent = ""; holder.textContent = "";
      tabs.appendChild(btnTab("התחברות", mode === "login", function () { mode = "login"; draw(); }));
      tabs.appendChild(btnTab("הרשמה", mode === "reg", function () { mode = "reg"; draw(); }));
      if (mode === "login") { holder.appendChild(loginSec); return; }
      var pick = el("div", { cls: "mk-tabs sub" });
      pick.appendChild(el("span", { cls: "meta", text: "נרשמים בתור:" }));
      pick.appendChild(btnTab("מבקש עבודה", role === "client", function () { role = "client"; draw(); }));
      pick.appendChild(btnTab("איש מקצוע או חברה", role === "pro", function () { role = "pro"; draw(); }));
      holder.appendChild(pick);
      holder.appendChild(regForm(role));
    }
    wrap.appendChild(tabs); wrap.appendChild(holder); draw();
    return wrap;
  }

  function proProfile(p) {
    var kind = select({ individual: "איש מקצוע פרטי", company: "חברה" }, p.kind), fld = el("input", { value: p.field || "" }),
      bio = el("textarea", { rows: 3, value: p.bio || "" }), exp = el("input", { value: p.exp || "", placeholder: "למשל: 5 שנים בפיתוח" }),
      links = el("textarea", { rows: 2, value: (p.links || []).join("\n") });
    var m = msgBox(), b = el("button", { cls: "btn ghost", type: "button", text: "שמירת פרופיל" });
    b.addEventListener("click", function () {
      api("PUT", "profile", { kind: kind.value, field: fld.value, bio: bio.value, exp: exp.value, links: links.value }).then(function (r) { m.textContent = r.ok ? "נשמר." : "השמירה נכשלה."; });
    });
    var file = el("input", { type: "file", accept: "image/*" }), pm = msgBox();
    var ps = { 0: "אין תמונה", 1: "התמונה ממתינה לאישור הנהלה ותוצג לאחר האישור", 2: "התמונה מוצגת" };
    pm.textContent = ps[p.photo_status || 0];
    file.addEventListener("change", function () {
      if (!file.files[0]) return;
      shrinkPhoto(file.files[0]).then(function (d) { return api("POST", "photo", { data: d }); })
        .then(function (r) { pm.textContent = r.ok ? ps[1] : "ההעלאה נכשלה."; }).catch(function () { pm.textContent = "ההעלאה נכשלה."; });
    });
    var rm = el("button", { cls: "btn ghost sm", type: "button", text: "הסרת תמונה" });
    rm.addEventListener("click", function () { api("POST", "photo/remove", {}).then(function () { pm.textContent = ps[0]; }); });
    return section("הפרופיל שלי", [el("div", { cls: "who" }, [avatar(p, true), el("p", { cls: "meta", text: proLine(p) })]),
      shareProfile(p),
      field("סוג", kind), field("תחום", fld), field("ניסיון", exp), field("על עצמך או על החברה", bio), field("קישורים", links),
      field("תמונה (אופציונלי, באישור הנהלה)", file), pm, el("div", { cls: "act" }, [b, rm]), m]);
  }
  function prosList() {
    var s = el("div");
    api("GET", "pros").then(function (rows) {
      if (!Array.isArray(rows) || !rows.length) { s.appendChild(el("p", { cls: "meta", text: "עדיין אין אנשי מקצוע מאושרים." })); return; }
      var g = el("div", { cls: "grid c3" });
      rows.forEach(function (p) {
        var c = el("a", { cls: "pcard", href: "#/pro/" + p.id }, [el("div", { cls: "who" }, [avatar(p, true), el("div", {}, [el("h3", { text: p.name }), el("p", { cls: "meta", text: proLine(p) })])]),
          p.field ? el("p", { text: p.field }) : null, p.bio ? el("p", { cls: "meta", text: p.bio.length > 120 ? p.bio.slice(0, 120) + "…" : p.bio }) : null, el("span", { cls: "more", text: "לפרופיל המלא ←" })]);
        g.appendChild(c);
      });
      s.appendChild(g);
    });
    return s;
  }
  function proPage(id) {
    var s = el("div", { cls: "mk-sec" });
    s.appendChild(el("a", { href: "#/pros", cls: "meta", text: "→ כל אנשי המקצוע" }));
    api("GET", "pros").then(function (rows) {
      var p = (Array.isArray(rows) ? rows : []).filter(function (x) { return String(x.id) === String(id); })[0];
      if (!p) { s.appendChild(el("p", { text: "הפרופיל לא נמצא." })); return; }
      var c = el("article", { cls: "card mk-sec" }, [el("div", { cls: "profile-head" }, [avatar(p, true), el("div", {}, [el("h1", { text: p.name }), el("p", { cls: "meta", text: proLine(p) })])]),
        p.field ? el("p", {}, [el("strong", { text: "תחום: " }), p.field]) : null, p.exp ? el("p", {}, [el("strong", { text: "ניסיון: " }), p.exp]) : null,
        p.bio ? el("p", { text: p.bio }) : null]);
      linksOf(p).forEach(function (a) { c.appendChild(a); });
      c.appendChild(shareProfile(p));
      s.appendChild(c);
    });
    return s;
  }


  // ================= forum pages =================
  function go(path) { location.hash = "#/" + path; }
  function ago(ts) {
    if (!ts) return "";
    var s = Math.max(0, Math.floor(Date.now() / 1000 - ts));
    if (s < 3600) return "לפני " + Math.max(1, Math.floor(s / 60)) + " דקות";
    if (s < 86400) return "לפני " + Math.floor(s / 3600) + " שעות";
    return "לפני " + Math.floor(s / 86400) + " ימים";
  }
  function isProActive() { return me && me.role === "pro" && me.status === "active"; }
  function chip(text, cls) { return el("span", { cls: "chip " + (cls || ""), text: text }); }
  function statusChip(s) { return chip(STATUS[s] || s, "st-" + s); }
  function crumbs(parts) {
    var box = el("div", { cls: "crumbs" });
    parts.forEach(function (p, i) {
      if (i) box.appendChild(document.createTextNode(" › "));
      box.appendChild(p.href ? el("a", { href: p.href, text: p.text }) : el("span", { text: p.text }));
    });
    return box;
  }
  function pageTitle(text, actions) { return el("div", { cls: "ptitle" }, [el("h1", { text: text })].concat(actions || [])); }
  function note(text) { return el("p", { cls: "note", text: text }); }
  function linkBtn(text, href, primary) { return el("a", { cls: "btn" + (primary ? " primary" : ""), href: href, text: text }); }

  function feedRow(r) {
    var count = Array.isArray(r.bids) ? r.bids.length : (r.bids || 0);
    var chats = r.chats != null ? r.chats : null;
    var snippet = r.snippet || (r.desc || "").slice(0, 160);
    function cnt(n, label) { return el("span", { cls: n ? "" : "zero" }, [el("b", { text: String(n) }), el("span", { text: label })]); }
    return el("a", { cls: "row s-" + r.status, href: "#/r/" + r.id }, [
      el("span", { cls: "grow" }, [
        el("span", { cls: "line" }, [el("strong", { cls: "ttl", text: r.title }), r.for_me ? chip("מיועדת אליך", "tag") : null, r.mine ? chip("שלי", "tag") : null]),
        snippet ? el("span", { cls: "snip", text: snippet }) : null,
        el("span", { cls: "chips" }, [statusChip(r.status), chip(meta.cats[r.category] || "", "cat"), r.level && r.level !== "any" ? chip(levelShort(r.level), "lvl") : null,
          el("span", { cls: "rmeta", text: (r.author ? r.author + " · " : "") + ago(r.created) })])]),
      el("span", { cls: "counts" }, [cnt(count, "הצעות"), chats != null ? cnt(chats, "שיחות") : null])]);
  }
  function rowsBox(list, emptyText) {
    var box = el("div", { cls: "list" });
    if (!list.length) box.appendChild(el("p", { cls: "empty", text: emptyText || "אין כאן בקשות עדיין." }));
    list.forEach(function (r) { box.appendChild(feedRow(r)); });
    return box;
  }
  function seg(options, value, onChange) {
    var box = el("div", { cls: "seg", role: "tablist" });
    options.forEach(function (o) {
      var b = el("button", { type: "button", cls: o[0] === value ? "on" : "", text: o[1] });
      b.setAttribute("aria-selected", o[0] === value ? "true" : "false");
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(box.children, function (x) { x.className = x === b ? "on" : ""; x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        onChange(o[0]);
      });
      box.appendChild(b);
    });
    return box;
  }
  function sideCta(cat) {
    if (!me) return el("div", { cls: "scard cta" }, [el("h3", { text: "צריך עבודה? יודע לעשות?" }),
      el("p", { text: "מפרסמים בקשה ומקבלים הצעות מאנשי מקצוע מאושרים. כל בקשה וכל איש מקצוע נבדקים ידנית." }),
      linkBtn("הרשמה", "#/register", true), el("a", { cls: "btn ghost", href: "#/login", text: "התחברות" })]);
    if (me.role === "client") return el("div", { cls: "scard cta" }, [el("h3", { text: "בקשה חדשה" }),
      el("p", { text: "מתארים מה צריך, וההצעות מגיעות לכאן." }), linkBtn("פרסום בקשה", "#/new" + (cat ? "/" + cat : ""), true)]);
    if (me.status !== "active") return el("div", { cls: "scard" }, [el("h3", { text: "ההצטרפות בבדיקה" }),
      el("p", { text: "ההנהלה בודקת את הפרטים ותאשר ידנית. בינתיים אפשר להשלים את הפרופיל." }), linkBtn("לפרופיל", "#/profile")]);
    return el("div", { cls: "scard cta" }, [el("h3", { text: "שלום " + first(me.name) }),
      el("p", { text: "בחר בקשה פתוחה, הגש הצעה או פתח שיחה עם המזמין." }), linkBtn("העבודות שלי", "#/mine", true)]);
  }
  function first(n) { return String(n || "").split(" ")[0]; }

  // ---- home: all requests, like topics in a forum
  function feedPage(cat) {
    var layout = el("div", { cls: "layout" }), mainCol = el("div"), side = el("aside", { cls: "side first" });
    root.appendChild(layout); layout.appendChild(mainCol); layout.appendChild(side);
    mainCol.appendChild(pageTitle(cat ? meta.cats[cat] : "בקשות עבודה ושירותים"));
    mainCol.appendChild(el("p", { cls: "lead", text: cat ? (CAT_DESC[cat] || "") : "כל הבקשות שפורסמו בלוח. אנשי מקצוע מאושרים מגישים הצעות ומתכתבים עם המזמין, והמזמין בוחר." }));
    var status = "open", search = el("input", { type: "search", placeholder: "חיפוש בבקשות", "aria-label": "חיפוש" });
    var holder = el("div");
    mainCol.appendChild(el("div", { cls: "toolbar" }, [seg([["open", "מחפשים בעל מקצוע"], ["taken", "נמצא בעל מקצוע"], ["done", "בוצעו"], ["all", "הכל"]], status, function (v) { status = v; loadFeed(); }),
      el("label", { cls: "searchbox" }, [search])]));
    mainCol.appendChild(holder);
    function loadFeed() {
      var qs = "status=" + encodeURIComponent(status) + (cat ? "&cat=" + encodeURIComponent(cat) : "") + (search.value.trim() ? "&q=" + encodeURIComponent(search.value.trim()) : "");
      api("GET", "feed?" + qs).then(function (rows) {
        holder.textContent = "";
        holder.appendChild(rowsBox(Array.isArray(rows) ? rows : [], search.value.trim() ? "לא נמצאו בקשות שמתאימות לחיפוש." : status === "open" ? "אין כרגע בקשות פתוחות בנושא הזה." : "אין בקשות להצגה."));
      });
    }
    var t = null;
    search.addEventListener("input", function () { clearTimeout(t); t = setTimeout(loadFeed, 300); });

    side.appendChild(sideCta(cat));
    var nav = el("nav", { cls: "catnav", "aria-label": "תחומים" }), stats = el("div", { cls: "stats" });
    side.appendChild(el("div", { cls: "scard cats" }, [el("h3", { text: "תחומים" }), nav]));
    side.appendChild(el("div", { cls: "scard stats-card" }, [stats]));
    side.appendChild(el("div", { cls: "scard steps-card steps-wrap" }, [el("h3", { text: "איך זה עובד" }), el("ol", { cls: "steps" }, [
      el("li", {}, [el("span", {}, [el("b", { text: "מפרסמים בקשה. " }), "ההנהלה מאשרת ומפרסמת."])]),
      el("li", {}, [el("span", {}, [el("b", { text: "מקבלים הצעות. " }), "מאנשי מקצוע מאושרים, אחת לכל רמה."])]),
      el("li", {}, [el("span", {}, [el("b", { text: "בוחרים ומתקדמים. " }), "פרטי הקשר נמסרים רק למי שנבחר."])])])]));
    api("GET", "categories").then(function (st) {
      var total = 0;
      Object.keys(meta.cats).forEach(function (k) { total += ((st.cats || {})[k] || {}).requests || 0; });
      nav.appendChild(el("a", { cls: cat ? "" : "on", href: "#/" }, [el("span", { text: "כל התחומים" }), el("span", { cls: "n", text: String(total) })]));
      Object.keys(meta.cats).forEach(function (k) {
        var n = ((st.cats || {})[k] || {}).requests || 0;
        nav.appendChild(el("a", { cls: cat === k ? "on" : "", href: "#/c/" + k }, [el("span", { text: meta.cats[k] }), el("span", { cls: "n", text: n ? String(n) : "" })]));
      });
      stats.appendChild(el("div", { cls: "stat" }, [el("b", { text: String(st.pros || 0) }), el("span", { text: "אנשי מקצוע" })]));
      stats.appendChild(el("div", { cls: "stat" }, [el("b", { text: String(st.done || 0) }), el("span", { text: "עבודות שבוצעו" })]));
    });
    loadFeed();
  }

  // ---- one request: everything about it in one page
  function requestPage(id) {
    root.appendChild(crumbs([{ text: "בקשות", href: "#/" }, { text: "בקשה" }]));
    var holder = el("div");
    root.appendChild(holder);
    function draw() {
      api("GET", "requests/" + id).then(function (r) {
        holder.textContent = "";
        if (!r.id) { holder.appendChild(note("הבקשה לא נמצאה או שאינה זמינה.")); return; }
        if (r.category && root.firstChild && root.firstChild.className === "crumbs") {
          root.replaceChild(crumbs([{ text: "בקשות", href: "#/" }, { text: meta.cats[r.category] || "", href: "#/c/" + r.category }, { text: r.title }]), root.firstChild);
        }
        var layout = el("div", { cls: "layout" }), mainCol = el("div"), side = el("aside", { cls: "side" });
        holder.appendChild(layout); layout.appendChild(mainCol); layout.appendChild(side);
        mainCol.appendChild(el("article", { cls: "post" }, [
          el("div", { cls: "chips" }, [statusChip(r.status), chip(meta.cats[r.category] || "", "cat"),
            r.tagged ? chip("מתויג: " + r.tagged.name + (r.tagged.only ? " (פרטי)" : ""), "tag") : null,
            r.via_admin ? chip("מטעם ההנהלה", "tag") : null]),
          el("h1", { text: r.title }),
          el("div", { cls: "byline" }, [avatar({ name: r.author || "?" }, false, "sm"), el("span", { text: (r.author ? r.author + " · " : "") + "פורסם " + ago(r.created) })]),
          el("p", { cls: "body", text: r.desc })]));

        var info = el("dl", { cls: "dl" });
        function row(k, v) { if (v) info.appendChild(el("div", {}, [el("dt", { text: k }), el("dd", { text: v })])); }
        row("מצב", STATUS[r.status] || r.status); row("תחום", meta.cats[r.category]); row("רמה רצויה", levelShort(r.level || "any"));
        row("גודל", meta.sizes[r.size]); row("תקציב", r.budget); row("הצעות", String(r.bids_count != null ? r.bids_count : (r.bids || []).length)); row("שיחות", r.chats_count != null ? String(r.chats_count) : "");
        side.appendChild(el("div", { cls: "scard" }, [el("h3", { text: "פרטי הבקשה" }), info]));

        if (r.viewer === "guest" && !me) {
          side.appendChild(el("div", { cls: "scard cta" }, [el("h3", { text: "רוצה להציע מחיר?" }),
            el("p", { text: "הצעות ושיחות פתוחות לאנשי מקצוע מאושרים. ההצטרפות כפופה לאישור ההנהלה." }),
            linkBtn("הרשמה כאיש מקצוע", "#/register", true), el("a", { cls: "btn ghost", href: "#/login", text: "התחברות" })]));
        } else if (r.viewer === "client") {
          side.appendChild(note("הצעות מחיר ושיחות זמינות לאנשי מקצוע מאושרים. את הבקשות שלך אפשר לנהל ב\"הבקשות שלי\"."));
        } else if (r.viewer === "pending_pro") {
          side.appendChild(note("ההצטרפות שלך ממתינה לאישור ההנהלה. לאחר האישור תוכל להציע מחיר ולפתוח שיחה."));
        } else if (r.viewer === "pro") {
          if (r.client) mainCol.appendChild(el("div", { cls: "panel" }, [el("h3", { text: "פרטי המזמין" }), el("p", { text: r.client.name + " · " + r.client.email + (r.client.contact ? " · " + r.client.contact : "") })]));
          var kids = [];
          if (r.status === "open") {
            if (r.bid_blocked) kids.push(note("כבר הוגשה הצעה ברמה שלך. כדי למנוע גניבת עבודות, מותרת הצעה אחת מכל רמה. אפשר לפתוח שיחה עם המזמין."));
            else if (r.level_too_high) kids.push(note("הבקשה מיועדת לרמה גבוהה יותר מהרמה שלך."));
            else {
              var price = el("input", { placeholder: "למשל 400 ש\"ח", value: r.my_bid ? r.my_bid.price : "" }), days = el("input", { placeholder: "למשל שבוע", value: r.my_bid ? r.my_bid.days : "" }),
                noteIn = el("textarea", { rows: 3, placeholder: "כמה מילים על איך תבצע את העבודה", value: r.my_bid ? r.my_bid.note : "" }), m = msgBox();
              var bb = el("button", { cls: "btn primary", type: "button", text: r.my_bid ? "עדכון ההצעה" : "שליחת הצעה" });
              bb.addEventListener("click", function () {
                api("POST", "bids", { request_id: r.id, price: price.value, days: days.value, note: noteIn.value }).then(function (x) {
                  if (x.ok) { m.textContent = "ההצעה נשמרה. המזמין יראה אותה בדף הבקשה."; return; }
                  m.textContent = x.__status === 409 ? "כבר הוגשה הצעה ברמה שלך." : "נא להזין מחיר.";
                  if (x.__status === 409) draw();
                });
              });
              kids.push(el("div", { cls: "two" }, [field("מחיר", price), field("זמן ביצוע", days)]), field("הערה", noteIn), el("div", { cls: "act" }, [bb]), m);
            }
          }
          var cb = el("button", { cls: "btn", type: "button", text: "שיחה עם המזמין" + (r.chat && r.chat.unread ? " · חדשות: " + r.chat.unread : "") });
          cb.addEventListener("click", function () { startChat({ request_id: r.id }, "מזמין · " + r.title); });
          mainCol.appendChild(el("div", { cls: "panel" }, [el("h3", { text: r.my_bid ? "ההצעה שלך" : "הגשת הצעה" })].concat(kids)));
          side.appendChild(el("div", { cls: "scard vstack" }, [el("h3", { text: "שיחה פרטית" }), el("p", { text: "שאלות לפני הגשת הצעה? אפשר לכתוב למזמין ישירות." }), cb]));
        } else if (r.viewer === "owner") {
          var parts = ownerPanels(r, draw);
          side.appendChild(parts.shift());
          parts.forEach(function (n) { mainCol.appendChild(n); });
        }
      });
    }
    draw();
  }

  function ownerPanels(r, redraw) {
    var out = [];
    function act(label, url, data, confirmText, primary) {
      var b = el("button", { cls: "btn" + (primary ? " primary" : ""), type: "button", text: label });
      b.addEventListener("click", function () { if (confirmText && !confirm(confirmText)) return; api("POST", url, data || { request_id: r.id }).then(redraw); });
      return b;
    }
    var btns = el("div", { cls: "vstack" });
    if (r.status === "review") btns.appendChild(note("הבקשה ממתינה לאישור ההנהלה ותפורסם לאחר מכן."));
    if (r.status === "open") { btns.appendChild(act("מצאתי בעל מקצוע", "requests/found", null, "לסמן שמצאת בעל מקצוע? הבקשה תצא מרשימת הפתוחות.", true)); }
    if (r.status === "taken") { btns.appendChild(act("מחפש שוב", "requests/reopen", null, "להחזיר את הבקשה לרשימת הפתוחות?")); btns.appendChild(act("העבודה בוצעה", "requests/done", null, "לסמן שהעבודה בוצעה?", true)); }
    if (r.status === "open") btns.appendChild(act("העבודה כבר בוצעה", "requests/done", null, "לסמן שהעבודה בוצעה?"));
    if (r.status === "review" || r.status === "open") btns.appendChild(act("סגירת הבקשה", "requests/close", null, "לסגור את הבקשה?"));
    if (r.status === "done" && r.has_pro && !r.rated) {
      var stSel = select({ 5: "5 מצוין", 4: "4 טוב מאוד", 3: "3 סביר", 2: "2 חלש", 1: "1 לא מרוצה" }, "5"), tx = el("input", { placeholder: "הערה קצרה (אופציונלי)" });
      var rb = el("button", { cls: "btn primary", type: "button", text: "שליחת דירוג" });
      rb.addEventListener("click", function () { api("POST", "rate", { request_id: r.id, stars: Number(stSel.value), text: tx.value }).then(redraw); });
      btns.appendChild(el("strong", { text: "דירוג בעל המקצוע" })); btns.appendChild(stSel); btns.appendChild(tx); btns.appendChild(rb);
    }
    out.push(el("div", { cls: "scard" }, [el("h3", { text: "ניהול הבקשה" }), btns]));

    var bidsBox = el("div", { cls: "panel" }, [el("h3", { text: "הצעות מחיר (" + (r.bids || []).length + ")" })]);
    if (!(r.bids || []).length) bidsBox.appendChild(el("p", { cls: "sub", text: "עדיין אין הצעות. אנשי מקצוע יראו את הבקשה ויגישו הצעות כאן." }));
    (r.bids || []).forEach(function (b) {
      var row = el("div", { cls: "mk-bid" + (b.chosen ? " chosen" : "") }, [el("div", { cls: "bidtop" }, [
          el("a", { cls: "who", href: "#/pro/" + b.pro.id }, [avatar(b.pro), el("div", {}, [el("strong", { text: b.pro.name }), el("div", { cls: "sub", text: proLine(b.pro) })])]),
          el("div", { cls: "price" }, [document.createTextNode(b.price || ""), b.days ? el("small", { text: "זמן ביצוע: " + b.days }) : null])]),
        b.pro.exp ? el("div", { cls: "sub", text: "ניסיון: " + b.pro.exp }) : null,
        b.note ? el("div", { text: b.note }) : null]);
      linksOf(b.pro).forEach(function (a) { row.appendChild(a); });
      var cb = el("button", { cls: "btn sm", type: "button", text: "שיחה עם " + b.pro.name + (b.chat && b.chat.unread ? " · חדשות: " + b.chat.unread : "") });
      cb.addEventListener("click", function () { startChat({ request_id: r.id, pro_id: b.pro.id }, b.pro.name + " · " + r.title); });
      var acts = el("div", { cls: "act" }, [cb]);
      if (b.chosen) acts.appendChild(el("span", { cls: "mk-ok", text: "נבחר. ליצירת קשר: " + (b.pro.email || "") }));
      else if (r.status === "open") acts.appendChild(act("בחירה בהצעה", "requests/choose", { request_id: r.id, bid_id: b.id }, "לבחור בהצעה הזאת? פרטי הקשר שלך יועברו אליו."));
      row.appendChild(acts);
      bidsBox.appendChild(row);
    });
    out.push(bidsBox);

    var chatsBox = el("div", { cls: "panel" }, [el("h3", { text: "שיחות עם בעלי מקצוע (" + (r.chats || []).length + ")" })]);
    if (!(r.chats || []).length) chatsBox.appendChild(el("p", { cls: "sub", text: "בעלי מקצוע שיפתחו שיחה על הבקשה יופיעו כאן." }));
    (r.chats || []).forEach(function (c) {
      var row = el("button", { type: "button", cls: "cm-row" }, [avatar({ name: c.name, photo: c.photo }),
        el("span", { cls: "cm-txt" }, [el("strong", { text: c.name }), el("span", { cls: "meta", text: c.last })]),
        c.unread ? el("span", { cls: "cm-badge", text: String(c.unread) }) : null]);
      row.addEventListener("click", function () { openChat(c.id, c.name + " · " + r.title); });
      chatsBox.appendChild(row);
    });
    out.push(chatsBox);
    return out;
  }

  // ---- new request
  function newRequestPage(preCat) {
    if (!me || me.role !== "client") return root.appendChild(note("פרסום בקשה זמין למבקשים רשומים."));
    root.appendChild(crumbs([{ text: "בקשות", href: "#/" }, { text: "בקשה חדשה" }]));
    var title = el("input", { maxLength: 120 }), desc = el("textarea", { rows: 6, maxLength: 3000 }), cat = select(meta.cats, meta.cats[preCat] ? preCat : "software"),
      lvl = select(meta.levels, "any", "לא משנה"), size = select(meta.sizes, "small"), budget = el("input", { placeholder: "אופציונלי" }),
      contact = el("input", { placeholder: "טלפון או אימייל, יוצג רק למי שתבחר" });
    var m = msgBox(), tag = el("select"), only = el("input", { type: "checkbox" });
    tag.appendChild(el("option", { value: "", text: "ללא (פתוחה לכל אנשי המקצוע)" }));
    api("GET", "pros").then(function (rows) { (Array.isArray(rows) ? rows : []).forEach(function (p) { tag.appendChild(el("option", { value: p.id, text: p.name + " · " + levelShort(p.level) })); }); });
    var b = el("button", { cls: "btn primary", type: "button", text: "פרסום הבקשה" });
    b.addEventListener("click", function () {
      m.textContent = "";
      api("POST", "requests", { title: title.value, desc: desc.value, category: cat.value, level: lvl.value, size: size.value, budget: budget.value, contact: contact.value, tagged_pro: tag.value ? Number(tag.value) : 0, only_tagged: only.checked })
        .then(function (r) {
          if (r.ok) go("requests");
          else m.textContent = r.__status === 429 ? "הגעת למכסה היומית." : "נא למלא כותרת ותיאור (לפחות 10 תווים).";
        });
    });
    root.appendChild(el("div", { cls: "formcard" }, [el("h1", { text: "בקשה חדשה" }), el("p", { cls: "sub", text: "תאר מה צריך. הבקשה תופיע בלוח לאחר אישור ההנהלה, ופרטי הקשר שלך יימסרו רק למי שתבחר." }),
      field("כותרת", title), field("מה צריך", desc), el("div", { cls: "two" }, [field("תחום", cat), field("רמה רצויה (משפיעה על המחיר)", lvl)]),
      el("div", { cls: "two" }, [field("גודל העבודה", size), field("תקציב", budget)]), field("איך ליצור קשר", contact), field("תיוג מפתח מסוים", tag),
      el("label", { cls: "mk-agree" }, [only, el("span", { text: "גלוי רק למפתח המתויג" })]), b, m]));
  }

  // ---- account pages
  function myRequestsPage() {
    root.appendChild(pageTitle("הבקשות שלי", [linkBtn("בקשה חדשה", "#/new", true)]));
    var holder = el("div"); root.appendChild(holder);
    api("GET", "my/requests").then(function (rows) { holder.appendChild(rowsBox(Array.isArray(rows) ? rows : [], "עדיין לא פרסמת בקשות.")); });
  }
  function minePage() {
    root.appendChild(pageTitle("העבודות שלי"));
    var holder = el("div"); root.appendChild(holder);
    api("GET", "board").then(function (b) { holder.appendChild(rowsBox(b.mine || [], "עדיין לא נבחרת לעבודה.")); });
  }
  function simplePage(title, node) { root.appendChild(pageTitle(title)); root.appendChild(node); }

  // ---- header
  var badgeTimer = null;
  function renderHeader() {
    var box = document.getElementById("fuser");
    if (!box) return;
    box.textContent = "";
    clearInterval(badgeTimer);
    var hash = location.hash.replace(/^#\/?/, "").split("/")[0];
    document.querySelectorAll(".fbar nav a").forEach(function (a) {
      var h = a.getAttribute("href"), on = h === "/market/#/pros" ? (hash === "pros" || hash === "pro") : h === "/market/" ? (location.pathname.indexOf("/market/rules") < 0 && ["", "c", "r"].indexOf(hash) >= 0) : false;
      if (h.indexOf("/rules/") > 0) on = location.pathname.indexOf("/market/rules") === 0;
      if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    if (!me) {
      box.appendChild(el("a", { href: "#/login", text: "התחברות" })); box.appendChild(el("a", { cls: "hbtn", href: "#/register", text: "הרשמה" }));
      return;
    }
    var links = me.role === "client" ? [["requests", "הבקשות שלי"], ["messages", "הודעות"], ["partners", "שותפים"]]
      : me.status === "active" ? [["mine", "העבודות שלי"], ["messages", "הודעות"], ["profile", "הפרופיל"], ["partners", "שותפים"]]
      : [["profile", "הפרופיל"]];
    var msgLink = null, badge = el("span", { cls: "badge" });
    links.forEach(function (l) {
      var a = el("a", { href: "#/" + l[0], text: l[1] });
      if (l[0] === hash) a.setAttribute("aria-current", "page");
      if (l[0] === "messages") { msgLink = a; a.appendChild(badge); }
      box.appendChild(a);
    });
    if (me.role === "client") box.appendChild(el("a", { cls: "hbtn", href: "#/new", text: "בקשה חדשה" }));
    box.appendChild(el("span", { cls: "sep" }));
    box.appendChild(el("span", { cls: "uname", text: first(me.name) }));
    var out = el("button", { type: "button", text: "יציאה" });
    out.addEventListener("click", function () { api("POST", "logout", {}).then(function () { go(""); load(); }); });
    box.appendChild(out);
    function poll() {
      if (!msgLink) return;
      api("GET", "chats").then(function (rows) {
        var n = Array.isArray(rows) ? rows.reduce(function (s, c) { return s + c.unread; }, 0) : 0;
        badge.textContent = n ? String(n) : "";
      });
    }
    poll(); badgeTimer = setInterval(poll, 20000);
  }

  function contactAdminPage() {
    var name = el("input", { placeholder: "שמך" });
    var contact = el("input", { placeholder: "טלפון או מייל" });
    var subject = el("input", { placeholder: "נושא" });
    var msg = el("textarea", { placeholder: "הודעה", rows: 6 });
    var btn = el("button", { cls: "btn primary", type: "button", text: "שליחה" });
    var status = el("div", { cls: "mmsg", role: "status" });
    btn.addEventListener("click", function () {
      var n = name.value.trim(), c = contact.value.trim(), s = subject.value.trim(), m = msg.value.trim();
      if (!n || !c || !m) { status.textContent = "נא למלא שם, דרך קשר והודעה."; return; }
      api("POST", "contact-admin", { name: n, contact: c, subject: s, message: m }).then(function (r) {
        if (r.__status === 200) { status.textContent = "הודעתך נשלחה. תודה!"; name.value = ""; contact.value = ""; subject.value = ""; msg.value = ""; }
        else status.textContent = r.__status === 429 ? "כבר נשלחו כמה פניות. אפשר לנסות שוב בעוד שעה." : "השליחה נכשלה, נסה שוב.";
      });
    });
    if (me) { name.value = me.name || ""; contact.value = me.email || ""; }
    var box = el("section", { cls: "formcard" }, [
      el("h1", { text: "צור קשר עם ההנהלה" }), el("p", { cls: "sub", text: "שאלה, הצעה או בעיה? ההודעה מגיעה ישירות להנהלת הלוח." }),
      el("div", { cls: "two" }, [el("label", { cls: "mf" }, [el("span", { text: "שם" }), name]), el("label", { cls: "mf" }, [el("span", { text: "טלפון או מייל" }), contact])]),
      el("label", { cls: "mf" }, [el("span", { text: "נושא (אופציונלי)" }), subject]),
      el("label", { cls: "mf" }, [el("span", { text: "הודעה" }), msg]),
      el("div", { cls: "act" }, [btn]),
      status
    ]);
    root.appendChild(crumbs([{ text: "בקשות", href: "#/" }, { text: "צור קשר" }]));
    root.appendChild(box);
  }

  // ---- router
  function route() {
    closeChat();
    root.textContent = "";
    renderHeader();
    var parts = location.hash.replace(/^#\/?/, "").split("/"), p0 = parts[0] || "";
    var needLogin = ["requests", "new", "mine", "messages", "profile", "partners"];
    if (!me && needLogin.indexOf(p0) >= 0) return root.appendChild(authView("login"));
    if (p0 === "login" || p0 === "register") return me ? go("") : root.appendChild(authView(p0 === "register" ? "reg" : "login"));
    if (p0 === "contact") return contactAdminPage();
    if (p0 === "c") return feedPage(meta.cats[parts[1]] ? parts[1] : "");
    if (p0 === "r") return requestPage(parts[1]);
    if (p0 === "new") return newRequestPage(parts[1]);
    if (p0 === "requests") return myRequestsPage();
    if (p0 === "open") return go("");
    if (p0 === "mine") return minePage();
    if (p0 === "messages") return simplePage("הודעות", chatsStrip(true));
    if (p0 === "partners") return simplePage("תוכנית שותפים", partnerBox());
    if (p0 === "profile") return me.role === "pro" ? simplePage("הפרופיל שלי", proProfile(me.profile)) : go("");
    if (p0 === "pros") { root.appendChild(pageTitle("אנשי מקצוע")); root.appendChild(el("p", { cls: "lead", text: "אנשי מקצוע וחברות שאושרו ידנית על ידי ההנהלה. אפשר לתייג אחד מהם בבקשה חדשה." })); root.appendChild(prosList()); return; }
    if (p0 === "pro") { root.appendChild(proPage(parts[1])); return; }
    feedPage("");
  }
  window.addEventListener("hashchange", function () { load(); });
  function load() { api("GET", "me").then(function (r) { me = r.user || null; route(); }); }
  fetch("/api/m/meta").then(function (r) { return r.json(); }).then(function (m) { meta = m; load(); })
    .catch(function () { root.textContent = "השירות אינו זמין כרגע. נסה שוב מאוחר יותר."; });
})();
