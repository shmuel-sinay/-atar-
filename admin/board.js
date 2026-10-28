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
    var credits = d.credits.filter(function (c) { return c.status === "pending"; });
    var total = reqs.length + pros.length + photos.length + credits.length;
    box.hidden = false; box.textContent = "";
    box.appendChild(el("strong", { text: total ? "הלוח: " + total + " דברים ממתינים לאישור שלך" : "הלוח: אין כרגע דבר שממתין לאישור" }));
    function after() { note("נשמר"); refresh(); }
    function row(text, buttons) { box.appendChild(el("div", { cls: "act", style: "margin-top:8px" }, [el("span", { text: text })].concat(buttons))); }
    reqs.forEach(function (r) {
      row("בקשה חדשה: " + r.title + " (" + (labels.cats[r.category] || "") + ") מאת " + r.client.name, [
        btn("אישור ופרסום", function () { call("POST", "request", { id: r.id, status: "open" }).then(after); }),
        btn("דחייה", function () { if (confirm("לדחות את הבקשה?")) call("POST", "request", { id: r.id, status: "closed" }).then(after); }, true)]);
    });
    pros.forEach(function (u) {
      row("בקשת הצטרפות: " + u.name + " · " + (u.field || ""), [
        btn("אישור", function () { call("POST", "user", { id: u.id, status: "active" }).then(after); }),
        btn("חסימה", function () { if (confirm("לחסום?")) call("POST", "user", { id: u.id, status: "blocked" }).then(after); }, true)]);
    });
    photos.forEach(function (u) {
      row("תמונה חדשה של " + u.name, [
        btn("אישור תמונה", function () { call("POST", "photo", { id: u.id, ok: true }).then(after); }),
        btn("הסרה", function () { call("POST", "photo", { id: u.id, ok: false }).then(after); }, true)]);
    });
    credits.forEach(function (c) {
      row("תגמול שותף: " + c.partner + " · " + c.amount + " " + d.unit, [
        btn("אישור", function () { call("POST", "credit", { id: c.id, status: "approved" }).then(after); }),
        btn("דחייה", function () { call("POST", "credit", { id: c.id, status: "rejected" }).then(after); }, true)]);
    });
    box.appendChild(el("p", { cls: "meta", style: "margin:10px 0 0" }, ["לניהול מלא של הלוח: ", el("a", { href: "/market/admin/", text: "/market/admin/" })]));
    document.title = (total ? "(" + total + ") " : "") + "ניהול | כושר טק";
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
