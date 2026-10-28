(function () {
  var data = null;
  var STAT = { review: "ממתינה לאישור", open: "פתוחה", taken: "נלקחה", done: "בוצעה", closed: "סגורה" };
  var ROLE = { client: "מבקש", pro: "איש מקצוע / חברה" };
  var UST = { active: "פעיל", pending: "ממתין לאישור", blocked: "חסום" };
  var SIZEMAP, LEVELMAP, CATMAP;

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
    var pending = data.users.filter(function (u) { return u.status === "pending" || u.photo === 1; }).length;
    var review = data.requests.filter(function (r) { return r.status === "review"; }).length;
    document.getElementById("ucount").textContent = pending ? "(" + pending + ")" : "";
    document.getElementById("rcount").textContent = review ? "(" + review + ")" : "";

    var ul = document.getElementById("ulist"); ul.textContent = "";
    data.users.forEach(function (u) {
      var lines = [el("strong", { text: u.name }), el("div", { cls: "meta", text: u.email + " · " + ROLE[u.role] + " · " + UST[u.status] })];
      var lvl, rating;
      if (u.role === "pro") {
        lines.push(el("div", { cls: "meta", text: (u.kind === "company" ? "חברה" : "פרטי") + " · " + (u.field || "") }));
        if (u.bio) lines.push(el("p", { cls: "msg", text: u.bio }));
        if (u.links) lines.push(el("div", { cls: "meta", text: u.links.replace(/\n/g, "  ") }));
        lines.push(el("div", { cls: "meta", text: "דירוג לקוחות: " + (u.client_rating || "אין") + " (" + u.rating_count + ")" }));
        if (u.exp) lines.push(el("div", { cls: "meta", text: "ניסיון: " + u.exp }));
        if (u.photo) {
          var im = el("img", { cls: "thumb", alt: "", src: "/api/admin/m/photo/" + u.id + "?t=" + Date.now() });
          lines.push(im, el("div", { cls: "meta", text: u.photo === 1 ? "תמונה ממתינה לאישור" : "תמונה מאושרת" }));
        }
        lvl = sel(LEVELMAP, u.level);
        rating = el("input", { type: "number", min: 1, max: 5, step: 0.5, value: u.admin_rating == null ? "" : u.admin_rating, placeholder: "דירוג הנהלה" });
        rating.style.maxWidth = "130px";
      }
      var acts = el("div", { cls: "act" });
      function set(extra) { call("POST", "user", Object.assign({ id: u.id }, extra)).then(function () { note("נשמר"); load(); }).catch(function () { note("השמירה נכשלה"); }); }
      if (u.status !== "active") acts.appendChild(btn("אישור", function () { set({ status: "active" }); }));
      if (u.status !== "blocked") acts.appendChild(btn("חסימה", function () { if (confirm("לחסום את " + u.name + "?")) set({ status: "blocked" }); }, true));
      if (u.role === "pro" && u.photo === 1) acts.appendChild(btn("אישור תמונה", function () { call("POST", "photo", { id: u.id, ok: true }).then(function () { note("נשמר"); load(); }); }));
      if (u.role === "pro" && u.photo) acts.appendChild(btn("הסרת תמונה", function () { call("POST", "photo", { id: u.id, ok: false }).then(function () { note("נשמר"); load(); }); }, true));
      if (u.role === "pro") {
        acts.appendChild(lvl); acts.appendChild(rating);
        acts.appendChild(btn("שמירת רמה ודירוג", function () { set({ level: lvl.value, admin_rating: rating.value }); }));
      }
      ul.appendChild(el("div", { cls: "box" }, lines.concat([acts])));
    });
    if (!data.users.length) ul.appendChild(el("p", { cls: "meta", text: "אין משתמשים." }));

    var rl = document.getElementById("rlist"); rl.textContent = "";
    data.requests.forEach(function (r) {
      var acts = el("div", { cls: "act" });
      function setS(s) { call("POST", "request", { id: r.id, status: s }).then(function () { note("נשמר"); load(); }); }
      if (r.status === "review") acts.appendChild(btn("אישור ופרסום", function () { setS("open"); }));
      if (r.status !== "closed") acts.appendChild(btn("סגירה", function () { if (confirm("לסגור?")) setS("closed"); }, true));
      rl.appendChild(el("div", { cls: "box" }, [el("strong", { text: r.title }),
        el("div", { cls: "meta", text: STAT[r.status] + " · " + (CATMAP[r.category] || "") + " · הצעות: " + r.bids_count + " · לקוח: " + r.client.name + " · " + r.client.email + (r.client.contact ? " · " + r.client.contact : "") }),
        el("p", { cls: "msg", text: r.desc }), acts]));
    });
    if (!data.requests.length) rl.appendChild(el("p", { cls: "meta", text: "אין בקשות." }));

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
    eb.appendChild(el("p", { cls: "meta", text: "ההערכה שמוצגת: בסיס × רמה × גודל, בטווח של 80% עד 130%." }));
    document.getElementById("saveest").onclick = function () {
      var out = { base: {}, level_mult: {}, size_mult: {} };
      Object.keys(inputs).forEach(function (k) { var p = k.split("."); out[p[0]][p[1]] = Number(inputs[k].value); });
      call("PUT", "settings", out).then(function () { note("נשמר"); load(); }).catch(function () { note("השמירה נכשלה"); });
    };
  }
  function load() { return call("GET", "overview").then(function (d) { data = d; render(); }).catch(function () {}); }

  document.querySelectorAll(".tabs button").forEach(function (b) {
    b.addEventListener("click", function () { if (["users", "mreq", "est"].indexOf(b.dataset.tab) >= 0) load(); });
  });

  // load once the admin shell is visible (it logs in or restores the session itself)
  var tries = 0;
  (function wait() {
    if (!document.getElementById("app").hidden) return load();
    if (++tries < 200) setTimeout(wait, 300);
  })();
  document.getElementById("go").addEventListener("click", function () { tries = 0; setTimeout(function () { (function w() { if (!document.getElementById("app").hidden) load(); else if (++tries < 40) setTimeout(w, 300); })(); }, 300); });
})();
