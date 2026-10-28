(function () {
  var root = document.getElementById("mk");
  var meta = { cats: {}, levels: {}, sizes: {} };
  var me = null;
  try {
    var rq = new URLSearchParams(location.search).get("ref");
    if (rq && /^[0-9a-f]{4,20}$/.test(rq)) localStorage.setItem("mk_ref", rq);
  } catch (e) {}
  function savedRef() { try { return localStorage.getItem("mk_ref") || ""; } catch (e) { return ""; } }
  var STATUS = { review: "ממתינה לאישור הנהלה", open: "פתוחה להצעות", taken: "נלקחה", done: "בוצעה", closed: "סגורה" };
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
  function select(map, value, any) {
    var s = el("select");
    if (any) s.appendChild(el("option", { value: "any", text: any }));
    Object.keys(map).forEach(function (k) { var o = el("option", { value: k, text: map[k] }); if (k === value) o.selected = true; s.appendChild(o); });
    return s;
  }
  function msgBox() { return el("div", { cls: "mmsg", role: "status" }); }
  function stars(p) { return p.rating ? " · דירוג " + p.rating + (p.ratings ? " (" + p.ratings + ")" : "") : ""; }
  function proLine(p) {
    return (p.kind === "company" ? "חברה" : "איש מקצוע") + " · " + (meta.levels[p.level] || "") + stars(p) + (p.founding ? " · חבר מייסד" : "") + (p.ambassador ? " · " + p.ambassador : "");
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

  var CSTAT = { pending: "ממתין לאישור", approved: "אושר", paid: "שולם", rejected: "נדחה" };
  function partnerBox() {
    var box = el("section", { cls: "card mk-sec" });
    api("GET", "partner").then(function (p) {
      if (!p.code) return;
      var link = location.origin + location.pathname + "?ref=" + p.code;
      var inp = el("input", { value: link, readOnly: true });
      var cp = el("button", { cls: "btn ghost sm", type: "button", text: "העתקה" });
      cp.addEventListener("click", function () { inp.select(); try { navigator.clipboard.writeText(link); } catch (e) {} cp.textContent = "הועתק"; });
      box.appendChild(el("h3", { text: "תוכנית שותפים" }));
      box.appendChild(el("p", { text: "מביאים מבקש חדש ללוח ומקבלים תגמול (" + p.reward + " " + p.unit + ") כשהעבודה הראשונה שלו מסתיימת. התגמול מאושר ידנית על ידי ההנהלה." }));
      if (p.level) box.appendChild(el("p", { cls: "mk-ok", text: "הדרגה שלך: " + p.level }));
      box.appendChild(el("div", { cls: "mk-bidform" }, [inp, cp]));
      box.appendChild(el("div", { cls: "act" }, shareButtons("מקום לבקש עבודה ולקבל הצעות", "מקום לבקש עבודה, תוכנה או שירות ולקבל הצעות מאנשי מקצוע מאושרים:", link)));
      box.appendChild(el("p", { cls: "meta", text: "נרשמו דרכך: " + p.referred + " · ממתין: " + p.totals.pending + " · אושר: " + p.totals.approved + " · שולם: " + p.totals.paid + " (" + p.unit + ")" }));
      p.credits.forEach(function (c) { box.appendChild(el("div", { cls: "meta", text: c.amount + " " + p.unit + " · " + CSTAT[c.status] })); });
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
  function avatar(p, big) {
    var box = el("span", { cls: "avatar" + (big ? " big" : "") });
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
  function rangeText(e) { return e ? "הערכה: " + e.lo + "–" + e.hi + " ש\"ח (הערכה בלבד)" : ""; }

  function estimateBox(getVals) {
    var out = el("div", { cls: "mk-est" });
    function upd() {
      var v = getVals();
      api("POST", "estimate", v).then(function (e) { out.textContent = e.lo != null ? rangeText(e) : ""; });
    }
    return { node: out, update: upd };
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

  function requestCard(r, refresh) {
    var kids = [r.tagged ? el("p", { cls: "mk-ok", text: "מתויג: " + r.tagged.name + (r.tagged.only ? " (גלוי רק לו)" : "") }) : null,
      el("p", { cls: "meta", text: STATUS[r.status] + " · " + (meta.cats[r.category] || "") + " · " + (r.level === "any" ? "כל רמה" : meta.levels[r.level] || "") }),
      el("p", { text: r.desc }), r.estimate ? el("p", { cls: "meta", text: rangeText(r.estimate) }) : null];
    function act(label, url, data, confirmText) {
      var b = el("button", { cls: "btn ghost sm", type: "button", text: label });
      b.addEventListener("click", function () { if (confirmText && !confirm(confirmText)) return; api("POST", url, data).then(refresh); });
      return b;
    }
    (r.bids || []).forEach(function (b) {
      var row = el("div", { cls: "mk-bid" }, [el("div", { cls: "who" }, [avatar(b.pro), el("div", {}, [el("strong", { text: b.pro.name }), el("div", { cls: "meta", text: proLine(b.pro) })])]),
        b.pro.exp ? el("div", { cls: "meta", text: "ניסיון: " + b.pro.exp }) : null,
        el("div", { text: "מחיר: " + b.price + (b.days ? " · זמן: " + b.days : "") }), b.note ? el("div", { text: b.note }) : null]);
      linksOf(b.pro).forEach(function (a) { row.appendChild(a); });
      var cb = el("button", { cls: "btn ghost sm", type: "button", text: "צ'אט עם " + b.pro.name + (b.chat && b.chat.unread ? " · חדשות: " + b.chat.unread : "") });
      cb.addEventListener("click", function () { startChat({ request_id: r.id, pro_id: b.pro.id }, b.pro.name + " · " + r.title); });
      row.appendChild(cb);
      if (b.chosen) row.appendChild(el("div", { cls: "mk-ok", text: "נבחר. ליצירת קשר: " + (b.pro.email || "") }));
      else if (r.status === "open") row.appendChild(act("בחירה בהצעה", "requests/choose", { request_id: r.id, bid_id: b.id }, "לבחור בהצעה הזאת? פרטי הקשר שלך יועברו אליו."));
      kids.push(row);
    });
    if (r.status === "open" && !(r.bids || []).length) kids.push(el("p", { cls: "meta", text: "עדיין אין הצעות." }));
    var acts = el("div", { cls: "act" });
    if (r.status === "taken") acts.appendChild(act("סימון כבוצע", "requests/done", { request_id: r.id }, "לסמן שהעבודה בוצעה?"));
    if (r.status === "review" || r.status === "open") acts.appendChild(act("סגירת הבקשה", "requests/close", { request_id: r.id }, "לסגור את הבקשה?"));
    if (r.status === "done" && !r.rated) {
      var st = select({ 5: "5 מצוין", 4: "4 טוב מאוד", 3: "3 סביר", 2: "2 חלש", 1: "1 לא מרוצה" }, "5"), tx = el("input", { placeholder: "הערה קצרה (אופציונלי)" });
      var rb = el("button", { cls: "btn primary sm", type: "button", text: "שליחת דירוג" });
      rb.addEventListener("click", function () { api("POST", "rate", { request_id: r.id, stars: Number(st.value), text: tx.value }).then(refresh); });
      acts.appendChild(st); acts.appendChild(tx); acts.appendChild(rb);
    }
    kids.push(acts);
    return section(r.title, kids);
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
        var c = el("a", { cls: "card pcard", href: "#/pro/" + p.id }, [el("div", { cls: "who" }, [avatar(p, true), el("div", {}, [el("h3", { text: p.name }), el("p", { cls: "meta", text: proLine(p) })])]),
          p.field ? el("p", { text: p.field }) : null, el("span", { cls: "meta", text: "לפרופיל המלא ←" })]);
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
      var c = el("article", { cls: "card mk-sec" }, [el("div", { cls: "who" }, [avatar(p, true), el("div", {}, [el("h2", { cls: "title", text: p.name }), el("p", { cls: "meta", text: proLine(p) })])]),
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
  function crumbs(parts) {
    var box = el("div", { cls: "crumbs" });
    parts.forEach(function (p, i) {
      if (i) box.appendChild(document.createTextNode(" › "));
      box.appendChild(p.href ? el("a", { href: p.href, text: p.text }) : el("span", { text: p.text }));
    });
    return box;
  }
  function pageTitle(text, actions) {
    return el("div", { cls: "ptitle" }, [el("h1", { text: text })].concat(actions || []));
  }
  function note(text) { return el("p", { cls: "note", text: text }); }
  function linkBtn(text, href, primary) { return el("a", { cls: "btn" + (primary ? " primary" : ""), href: href, text: text }); }

  function requestRows(list, showCat) {
    var box = el("div", { cls: "list" });
    if (!list.length) box.appendChild(el("p", { cls: "empty", text: "אין כאן בקשות עדיין." }));
    list.forEach(function (r) {
      var info = [STATUS[r.status]];
      if (showCat) info.push(meta.cats[r.category] || "");
      info.push(r.level === "any" ? "כל רמה" : (meta.levels[r.level] || "").split(":")[0]);
      if (r.estimate) info.push("הערכה " + r.estimate.lo + "–" + r.estimate.hi + " ש\"ח");
      var count = r.bids ? r.bids.length : (r.bids_count != null ? r.bids_count : null);
      box.appendChild(el("a", { cls: "row", href: "#/r/" + r.id }, [
        el("span", { cls: "grow" }, [el("strong", { cls: "ttl", text: r.title }), r.for_me ? el("span", { cls: "tag", text: "מיועדת אליך" }) : null,
          r.my_bid ? el("span", { cls: "tag ok", text: "הגשת הצעה" }) : null, el("span", { cls: "sub", text: info.join(" · ") })]),
        count != null ? el("span", { cls: "num" }, [el("b", { text: String(count) }), el("small", { text: "הצעות" })]) : null]));
    });
    return box;
  }

  // ---- home
  function homePage() {
    root.appendChild(pageTitle("לוח עבודות ושירותים"));
    var intro = el("div", { cls: "intro" }, [el("p", { text: "מקום לפרסם בקשה לעבודה, לתוכנה או לשירות, לקבל הצעות מאנשי מקצוע וחברות מאושרים, לבחור ולדרג. כל הצטרפות, בקשה ותמונה עוברות אישור ידני של ההנהלה." })]);
    if (!me) intro.appendChild(el("p", { cls: "acts" }, [linkBtn("הרשמה", "#/register", true), linkBtn("התחברות", "#/login")]));
    else if (me.role === "client") intro.appendChild(el("p", { cls: "acts" }, [linkBtn("בקשה חדשה", "#/new", true)]));
    root.appendChild(intro);
    var list = el("div", { cls: "cats" });
    root.appendChild(list);
    api("GET", "categories").then(function (st) {
      Object.keys(meta.cats).forEach(function (k) {
        var s = (st.cats || {})[k] || { requests: 0, bids: 0, last: null };
        list.appendChild(el("a", { cls: "cat", href: "#/c/" + k }, [
          el("span", { cls: "grow" }, [el("strong", { cls: "ttl", text: meta.cats[k] }), el("span", { cls: "sub", text: CAT_DESC[k] || "" })]),
          el("span", { cls: "num" }, [el("b", { text: String(s.requests) }), el("small", { text: "בקשות" })]),
          el("span", { cls: "num" }, [el("b", { text: String(s.bids) }), el("small", { text: "הצעות" })]),
          el("span", { cls: "last", text: s.last ? "בקשה אחרונה " + ago(s.last) : "" })]));
      });
      root.appendChild(el("p", { cls: "stats", text: (st.pros || 0) + " אנשי מקצוע מאושרים · " + (st.done || 0) + " עבודות הושלמו" }));
    });
  }

  // ---- category
  function categoryPage(k) {
    if (!meta.cats[k]) return root.appendChild(note("הקטגוריה לא נמצאה."));
    root.appendChild(crumbs([{ text: "הלוח", href: "#/" }, { text: meta.cats[k] }]));
    root.appendChild(pageTitle(meta.cats[k], me && me.role === "client" ? [linkBtn("בקשה חדשה", "#/new/" + k, true)] : []));
    root.appendChild(el("p", { cls: "sub", text: CAT_DESC[k] || "" }));
    var holder = el("div");
    root.appendChild(holder);
    if (isProActive()) {
      api("GET", "board").then(function (b) { holder.appendChild(requestRows((b.open || []).filter(function (r) { return r.category === k; }))); });
    } else if (me && me.role === "client") {
      holder.appendChild(note("מוצגות כאן הבקשות שלך בקטגוריה."));
      api("GET", "my/requests").then(function (rows) { holder.appendChild(requestRows((Array.isArray(rows) ? rows : []).filter(function (r) { return r.category === k; }))); });
    } else if (me) {
      holder.appendChild(note("הבקשות יוצגו לאחר שההנהלה תאשר את ההצטרפות שלך."));
    } else {
      holder.appendChild(note("בקשות פתוחות מוצגות לאנשי מקצוע מאושרים. אפשר להירשם או להתחבר."));
    }
  }

  // ---- request page
  function proRequestBlock(r, refresh) {
    var price = el("input", { placeholder: "מחיר", value: r.my_bid ? r.my_bid.price : "" }), days = el("input", { placeholder: "זמן", value: r.my_bid ? r.my_bid.days : "" }),
      noteIn = el("input", { placeholder: "הערה", value: r.my_bid ? r.my_bid.note : "" }), m = msgBox();
    var bb = el("button", { cls: "btn primary", type: "button", text: r.my_bid ? "עדכון הצעה" : "שליחת הצעה" });
    bb.addEventListener("click", function () {
      api("POST", "bids", { request_id: r.id, price: price.value, days: days.value, note: noteIn.value }).then(function (x) { m.textContent = x.ok ? "ההצעה נשמרה." : "נא להזין מחיר."; });
    });
    var cb = el("button", { cls: "btn", type: "button", text: "צ'אט עם המבקש" + (r.chat && r.chat.unread ? " · חדשות: " + r.chat.unread : "") });
    cb.addEventListener("click", function () { startChat({ request_id: r.id }, "מבקש · " + r.title); });
    return [el("div", { cls: "mk-bidform" }, [price, days, noteIn, bb]), m, el("div", { cls: "act" }, [cb])];
  }
  function requestPage(id) {
    root.appendChild(crumbs([{ text: "הלוח", href: "#/" }, { text: "בקשה" }]));
    var holder = el("div");
    root.appendChild(holder);
    function draw() {
      holder.textContent = "";
      if (me && me.role === "client") {
        api("GET", "my/requests").then(function (rows) {
          var r = (Array.isArray(rows) ? rows : []).filter(function (x) { return String(x.id) === String(id); })[0];
          holder.appendChild(r ? requestCard(r, draw) : note("הבקשה לא נמצאה."));
        });
      } else if (isProActive()) {
        api("GET", "board").then(function (b) {
          var r = (b.open || []).filter(function (x) { return String(x.id) === String(id); })[0], mine = false;
          if (!r) { r = (b.mine || []).filter(function (x) { return String(x.id) === String(id); })[0]; mine = !!r; }
          if (!r) { holder.appendChild(note("הבקשה לא נמצאה או שאינה זמינה לך.")); return; }
          var kids = [el("p", { cls: "sub", text: STATUS[r.status] + " · " + (meta.cats[r.category] || "") + " · " + (r.level === "any" ? "כל רמה" : meta.levels[r.level] || "") + (r.budget ? " · תקציב: " + r.budget : "") }),
            r.for_me ? el("p", { cls: "mk-ok", text: "מיועדת אליך" }) : null, el("p", { text: r.desc }), r.estimate ? el("p", { cls: "sub", text: rangeText(r.estimate) }) : null];
          if (mine) {
            kids.push(el("p", { text: "מבקש: " + r.client.name + " · " + r.client.email + (r.client.contact ? " · " + r.client.contact : "") }));
            var cb = el("button", { cls: "btn", type: "button", text: "צ'אט עם " + r.client.name });
            cb.addEventListener("click", function () { startChat({ request_id: r.id }, r.client.name + " · " + r.title); });
            kids.push(cb);
          } else proRequestBlock(r, draw).forEach(function (n) { kids.push(n); });
          holder.appendChild(section(r.title, kids));
        });
      } else holder.appendChild(note("הבקשות מוצגות רק לאנשי מקצוע מאושרים ולמי שפרסם אותן."));
    }
    draw();
  }

  // ---- new request
  function newRequestPage(preCat) {
    if (!me || me.role !== "client") return root.appendChild(note("פרסום בקשה זמין למבקשים רשומים."));
    root.appendChild(crumbs([{ text: "הלוח", href: "#/" }, { text: "בקשה חדשה" }]));
    root.appendChild(pageTitle("בקשה חדשה"));
    var title = el("input", { maxLength: 120 }), desc = el("textarea", { rows: 6, maxLength: 3000 }), cat = select(meta.cats, meta.cats[preCat] ? preCat : "software"),
      lvl = select(meta.levels, "any", "לא משנה"), size = select(meta.sizes, "small"), budget = el("input", { placeholder: "אופציונלי" }),
      contact = el("input", { placeholder: "טלפון או אימייל, יוצג רק למי שתבחר" });
    var m = msgBox(), tag = el("select"), only = el("input", { type: "checkbox" });
    tag.appendChild(el("option", { value: "", text: "ללא (פתוחה לכל אנשי המקצוע)" }));
    api("GET", "pros").then(function (rows) { (Array.isArray(rows) ? rows : []).forEach(function (p) { tag.appendChild(el("option", { value: p.id, text: p.name + " · " + (meta.levels[p.level] || "") })); }); });
    var est = estimateBox(function () { return { category: cat.value, level: lvl.value === "any" ? "basic" : lvl.value, size: size.value }; });
    [cat, lvl, size].forEach(function (s) { s.addEventListener("change", est.update); });
    est.update();
    var b = el("button", { cls: "btn primary", type: "button", text: "פרסום הבקשה" });
    b.addEventListener("click", function () {
      m.textContent = "";
      api("POST", "requests", { title: title.value, desc: desc.value, category: cat.value, level: lvl.value, size: size.value, budget: budget.value, contact: contact.value, tagged_pro: tag.value ? Number(tag.value) : 0, only_tagged: only.checked })
        .then(function (r) {
          if (r.ok) go("requests");
          else m.textContent = r.__status === 429 ? "הגעת למכסה היומית." : "נא למלא כותרת ותיאור (לפחות 10 תווים).";
        });
    });
    root.appendChild(el("div", { cls: "form" }, [field("כותרת", title), field("מה צריך", desc), field("תחום", cat), field("רמה רצויה", lvl), field("גודל העבודה", size),
      field("תקציב", budget), field("איך ליצור קשר", contact), field("תיוג מפתח מסוים", tag),
      el("label", { cls: "mk-agree" }, [only, el("span", { text: "גלוי רק למפתח המתויג" })]), est.node, b, m,
      el("p", { cls: "sub", text: "הבקשה תופיע לאנשי המקצוע לאחר אישור ההנהלה." })]));
  }

  // ---- account pages
  function myRequestsPage() {
    root.appendChild(pageTitle("הבקשות שלי", [linkBtn("בקשה חדשה", "#/new", true)]));
    var holder = el("div"); root.appendChild(holder);
    api("GET", "my/requests").then(function (rows) { holder.appendChild(requestRows(Array.isArray(rows) ? rows : [], true)); });
  }
  function openPage() {
    root.appendChild(pageTitle("בקשות פתוחות"));
    var holder = el("div"); root.appendChild(holder);
    api("GET", "board").then(function (b) { holder.appendChild(requestRows(b.open || [], true)); });
  }
  function minePage() {
    root.appendChild(pageTitle("העבודות שלי"));
    var holder = el("div"); root.appendChild(holder);
    api("GET", "board").then(function (b) { holder.appendChild(requestRows(b.mine || [], true)); });
  }
  function simplePage(title, node) { root.appendChild(pageTitle(title)); root.appendChild(node); }

  // ---- header
  var badgeTimer = null;
  function renderHeader() {
    var box = document.getElementById("fuser");
    if (!box) return;
    box.textContent = "";
    clearInterval(badgeTimer);
    if (!me) {
      box.appendChild(el("a", { href: "#/login", text: "התחברות" })); box.appendChild(el("a", { href: "#/register", text: "הרשמה" }));
      return;
    }
    var links = me.role === "client" ? [["requests", "הבקשות שלי"], ["new", "בקשה חדשה"], ["messages", "הודעות"], ["partners", "שותפים"]]
      : me.status === "active" ? [["open", "בקשות פתוחות"], ["mine", "העבודות שלי"], ["messages", "הודעות"], ["profile", "הפרופיל"], ["partners", "שותפים"]]
      : [["profile", "הפרופיל"]];
    var msgLink = null, badge = el("span", { cls: "badge" });
    links.forEach(function (l) {
      var a = el("a", { href: "#/" + l[0], text: l[1] });
      if (l[0] === "messages") { msgLink = a; a.appendChild(badge); }
      box.appendChild(a);
    });
    var out = el("button", { type: "button", text: "יציאה (" + me.name + ")" });
    out.addEventListener("click", function () { api("POST", "logout", {}).then(function () { go(""); load(); }); });
    box.appendChild(out);
    function poll() {
      if (!msgLink) return;
      api("GET", "chats").then(function (rows) {
        var n = Array.isArray(rows) ? rows.reduce(function (s, c) { return s + c.unread; }, 0) : 0;
        badge.textContent = n ? String(n) : ""; badge.style.display = n ? "" : "none";
      });
    }
    poll(); badgeTimer = setInterval(poll, 20000);
  }

  // ---- router
  function route() {
    closeChat();
    root.textContent = "";
    renderHeader();
    var parts = location.hash.replace(/^#\/?/, "").split("/"), p0 = parts[0] || "";
    var needLogin = ["requests", "new", "open", "mine", "messages", "profile", "partners"];
    if (!me && needLogin.indexOf(p0) >= 0) return root.appendChild(authView("login"));
    if (p0 === "login" || p0 === "register") return me ? go("") : root.appendChild(authView(p0 === "register" ? "reg" : "login"));
    if (p0 === "c") return categoryPage(parts[1]);
    if (p0 === "r") return requestPage(parts[1]);
    if (p0 === "new") return newRequestPage(parts[1]);
    if (p0 === "requests") return myRequestsPage();
    if (p0 === "open") return openPage();
    if (p0 === "mine") return minePage();
    if (p0 === "messages") return simplePage("הודעות", chatsStrip(true));
    if (p0 === "partners") return simplePage("תוכנית שותפים", partnerBox());
    if (p0 === "profile") return me.role === "pro" ? simplePage("הפרופיל שלי", proProfile(me.profile)) : go("");
    if (p0 === "pros") return simplePage("אנשי מקצוע", prosList());
    if (p0 === "pro") { root.appendChild(proPage(parts[1])); return; }
    if (me && me.role === "pro" && me.status !== "active") root.appendChild(note("בקשת ההצטרפות שלך התקבלה. ההנהלה בודקת את הפרטים ותאשר ידנית. בינתיים אפשר להשלים את הפרופיל."));
    homePage();
  }
  window.addEventListener("hashchange", function () { load(); });
  function load() { api("GET", "me").then(function (r) { me = r.user || null; route(); }); }
  fetch("/api/m/meta").then(function (r) { return r.json(); }).then(function (m) { meta = m; load(); })
    .catch(function () { root.textContent = "השירות אינו זמין כרגע. נסה שוב מאוחר יותר."; });
})();
