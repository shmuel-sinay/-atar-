(function () {
  var box = document.getElementById("boardbox");
  var labels = { cats: {}, levels: {}, sizes: {} };
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
    setTimeout(function () { s.classList.remove("show"); }, 2500);
  }
  function call(method, url, body) {
    return fetch("/api/admin/m/" + url, { method: method, credentials: "same-origin", headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  function btn(t, fn, danger) { var b = el("button", { type: "button", cls: "sm" + (danger ? " danger" : ""), text: t }); b.addEventListener("click", fn); return b; }

  function render(d) {
    labels = d.labels;
    var reqs = d.requests.filter(function (r) { return r.status === "review"; });
    var pros = d.users.filter(function (u) { return u.role === "pro" && u.status === "pending"; });
    var photos = d.users.filter(function (u) { return u.role === "pro" && u.photo === 1; });
    var credits = [];
    var total = reqs.length + pros.length + photos.length + credits.length;
    box.hidden = false; box.textContent = "";
    var head = el("div", { cls: "act", style: "justify-content:space-between;margin:0" }, [el("strong", { text: total ? total + " דברים ממתינים לאישור שלך" : "אין כרגע דבר שממתין לאישור" }),
      btn("פרסום בקשה בשם לקוח", function () { window.forwardToBoard({}); })]);
    box.appendChild(head);
    function after() { note("נשמר"); refresh(); }
    function card(title, kids, buttons) {
      box.appendChild(el("div", { cls: "pend-item" }, [el("strong", { text: title })].concat(kids, [el("div", { cls: "act" }, buttons)])));
    }
    function sel(map, value, any) {
      var s = el("select"); if (any) s.appendChild(el("option", { value: "any", text: any }));
      Object.keys(map).forEach(function (k) { var o = el("option", { value: k, text: map[k] }); if (k === value) o.selected = true; s.appendChild(o); }); return s;
    }
    reqs.forEach(function (r) {
      var view = el("div", { cls: "pend-body" }, [
        el("div", { cls: "meta", text: (labels.cats[r.category] || "") + " · רמה: " + (r.level === "any" || !r.level ? "לא משנה" : (labels.levels[r.level] || "").split(" (")[0]) + (r.budget ? " · תקציב: " + r.budget : "") + " · מאת " + r.client.name + " (" + r.client.email + ")" }),
        el("p", { cls: "msg", text: r.desc })]);
      var form = el("div", { cls: "pend-edit", hidden: true });
      var ti = el("input", { value: r.title, maxLength: 120 }), de = el("textarea", { rows: 5, value: r.desc, maxLength: 3000 }),
        ca = sel(labels.cats, r.category), lv = sel(labels.levels, r.level || "any", "לא משנה"), sz = sel(labels.sizes, r.size || "small"), bu = el("input", { value: r.budget || "" });
      [["כותרת", ti], ["תיאור", de], ["תחום", ca], ["רמה", lv], ["גודל", sz], ["תקציב", bu]].forEach(function (f) { form.appendChild(el("label", { cls: "f", text: f[0] }, [f[1]])); });
      var edit = btn("עריכה", function () { form.hidden = !form.hidden; view.hidden = !form.hidden ? true : false; edit.textContent = form.hidden ? "עריכה" : "ביטול עריכה"; });
      function save() {
        return call("POST", "request/edit", { id: r.id, title: ti.value, desc: de.value, category: ca.value, level: lv.value, size: sz.value, budget: bu.value });
      }
      var saveBtn = btn("שמירת השינויים", function () { save().then(after).catch(function () { note("נא למלא כותרת ותיאור"); }); });
      form.appendChild(el("div", { cls: "act" }, [saveBtn]));
      card("בקשה חדשה: " + r.title, [view, form], [
        btn("אישור ופרסום", function () { (form.hidden ? Promise.resolve() : save()).then(function () { return call("POST", "request", { id: r.id, status: "open" }); }).then(after).catch(function () { note("השמירה נכשלה"); }); }),
        edit,
        btn("דחייה", function () { ktAsk("לדחות את הבקשה?", { danger: true }).then(function (ok) { if (ok) call("POST", "request", { id: r.id, status: "closed" }).then(after); }); }, true)]);
    });
    pros.forEach(function (u) {
      card("בקשת הצטרפות: " + u.name, [el("div", { cls: "meta", text: [u.email, u.kind === "company" ? "חברה" : "איש מקצוע פרטי", u.field, u.exp ? "ניסיון: " + u.exp : ""].filter(Boolean).join(" · ") }),
        u.bio ? el("p", { cls: "msg", text: u.bio }) : null, u.links ? el("div", { cls: "meta", text: u.links.replace(/\n/g, "  ") }) : null], [
        btn("אישור", function () { call("POST", "user", { id: u.id, status: "active" }).then(after); }),
        btn("חסימה", function () { ktAsk("לחסום?", { danger: true }).then(function (ok) { if (ok) call("POST", "user", { id: u.id, status: "blocked" }).then(after); }); }, true)]);
    });
    photos.forEach(function (u) {
      var img = el("img", { cls: "pend-photo", alt: "התמונה של " + u.name, src: "/api/admin/m/photo/" + u.id + "?t=" + Date.now() });
      card("תמונת פרופיל חדשה של " + u.name, [el("div", { cls: "meta", text: (u.field || "") + " · " + u.email }), img], [
        btn("אישור תמונה", function () { call("POST", "photo", { id: u.id, ok: true }).then(after); }),
        btn("הסרה", function () { call("POST", "photo", { id: u.id, ok: false }).then(after); }, true)]);
    });
    credits.forEach(function (c) {
      row("תגמול שותף: " + c.partner + " · " + c.amount + " " + d.unit, [
        btn("אישור", function () { call("POST", "credit", { id: c.id, status: "approved" }).then(after); }),
        btn("דחייה", function () { call("POST", "credit", { id: c.id, status: "rejected" }).then(after); }, true)]);
    });
    
    document.title = (total ? "(" + total + ") " : "") + "ניהול | מלאכת מחשבת";
  }
  function refresh() { return call("GET", "overview").then(render).catch(function () {}); }

  // forward a message from the contact form to the board as a request on behalf of the customer
  window.forwardToBoard = function (m) {
    var ov = el("div", { style: "position:fixed;inset:0;background:#0007;display:grid;place-items:center;z-index:60" });
    var title = el("input", { value: m.subject || "" }), desc = el("textarea", { rows: 5, value: m.message || "" }), contact = el("input", { value: m.contact || "" });
    var cat = el("select"); Object.keys(labels.cats).forEach(function (k) { cat.appendChild(el("option", { value: k, text: labels.cats[k] })); });
    var msg = el("div", { cls: "meta" });
    var send = el("button", { type: "button", cls: "btn primary", text: "פרסום בלוח" });
    var cancel = el("button", { type: "button", cls: "sm", text: "ביטול" });
    function row(label, input) { return el("label", { cls: "f" }, [el("span", { text: label }), input]); }
    var form = el("div", { cls: "box", style: "background:var(--card);width:min(520px,94vw);max-height:90vh;overflow:auto;display:grid;gap:10px" },
      [el("strong", { text: "העברת הפנייה ללוח כבקשה" }), row("כותרת", title), row("תיאור", desc), row("תחום", cat),
       row("פרטי הלקוח (יימסרו רק למי שתבחר)", contact), msg, el("div", { cls: "act" }, [send, cancel])]);
    ov.appendChild(form); document.body.appendChild(ov);
    cancel.addEventListener("click", function () { ov.remove(); });
    send.addEventListener("click", function () {
      msg.textContent = "";
      call("POST", "forward", { title: title.value, desc: desc.value, category: cat.value, contact: contact.value })
        .then(function () { ov.remove(); note("פורסם בלוח"); refresh(); })
        .catch(function () { msg.textContent = "נא למלא כותרת ותיאור (לפחות 10 תווים)."; });
    });
  };

  var tries = 0;
  (function wait() {
    if (!document.getElementById("app").hidden) { refresh(); setInterval(refresh, 60000); return; }
    if (++tries < 200) setTimeout(wait, 300);
  })();
})();
