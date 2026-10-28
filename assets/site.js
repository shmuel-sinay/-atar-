(function () {
  function get(url) {
    return fetch(url, { headers: { Accept: "application/json" } }).then(function (r) {
      if (!r.ok) throw 0;
      return r.json();
    });
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  var STATUS = { "in": ["במלאי", "stock ok"], out: ["אזל מהמלאי", "stock"], order: ["בהזמנה מיוחדת", "stock"] };

  var prices = document.querySelectorAll("[data-svc]");
  if (prices.length) {
    get("/api/services").then(function (s) {
      prices.forEach(function (n) {
        var v = s[n.getAttribute("data-svc")];
        if (v) n.textContent = v;
      });
    }).catch(function () {});
  }

  function zoom(src, alt) {
    var w = el("div", "zoom"), im = el("img"); im.src = src; im.alt = alt || "";
    w.appendChild(im); document.body.appendChild(w);
    function close() { w.remove(); document.removeEventListener("keydown", key); }
    function key(e) { if (e.key === "Escape") close(); }
    w.addEventListener("click", close); document.addEventListener("keydown", key);
  }
  var box = document.getElementById("products");
  if (box) {
    get("/api/products").then(function (list) {
      if (!Array.isArray(list)) return;
      box.textContent = "";
      list.forEach(function (p) {
        var c = el("article", "card product");
        var pics = (p.gallery && p.gallery.length ? p.gallery : (p.image ? [p.image] : [])).filter(function (u) { return /^\/(uploads|assets\/products)\//.test(u); });
        if (pics.length) {
          var main = el("img", "pimg"); main.src = pics[0]; main.alt = p.name || ""; main.loading = "lazy";
          main.addEventListener("click", function () { zoom(main.src, p.name); });
          c.appendChild(main);
          if (pics.length > 1) {
            var th = el("div", "pthumbs");
            pics.forEach(function (u, i) {
              var t = el("img", i ? "" : "on"); t.src = u; t.alt = ""; t.loading = "lazy";
              t.addEventListener("click", function () { main.src = u; Array.prototype.forEach.call(th.children, function (x) { x.className = x === t ? "on" : ""; }); });
              th.appendChild(t);
            });
            c.appendChild(th);
          }
        }
        c.appendChild(el("h3", null, p.name));
        var lines = String(p.desc || "").split("\n").filter(Boolean);
        if (lines.length) c.appendChild(el("p", null, lines[0]));
        if (lines.length > 1) {
          var ul = el("ul", "specs");
          lines.slice(1).forEach(function (t) { ul.appendChild(el("li", null, t)); });
          c.appendChild(ul);
        }
        var st = STATUS[p.status] || STATUS.order;
        var line = el("p");
        line.appendChild(el("span", st[1], st[0]));
        if (p.price) {
          line.appendChild(document.createTextNode(" "));
          line.appendChild(el("span", "price", p.price));
        }
        c.appendChild(line);
        var a = el("a", p.status === "in" ? "btn primary" : "btn ghost", p.status === "in" ? "להזמנה" : p.status === "out" ? "עדכנו אותי כשיחזור" : "לבירור והזמנה");
        a.href = "/contact/?product=" + encodeURIComponent(p.name || "");
        c.appendChild(a);
        box.appendChild(c);
      });
    }).catch(function () {});
  }
})();
