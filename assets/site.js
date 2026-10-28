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

  var box = document.getElementById("products");
  if (box) {
    get("/api/products").then(function (list) {
      if (!Array.isArray(list)) return;
      box.textContent = "";
      list.forEach(function (p) {
        var c = el("article", "card");
        if (p.image && p.image.indexOf("/uploads/") === 0) {
          var img = el("img", "pimg");
          img.src = p.image; img.alt = ""; img.loading = "lazy";
          c.appendChild(img);
        }
        c.appendChild(el("h3", null, p.name));
        if (p.desc) c.appendChild(el("p", null, p.desc));
        var st = STATUS[p.status] || STATUS.order;
        var line = el("p");
        line.appendChild(el("span", st[1], st[0]));
        if (p.price) {
          line.appendChild(document.createTextNode(" "));
          line.appendChild(el("span", "price", p.price));
        }
        c.appendChild(line);
        var a = el("a", p.status === "in" ? "btn primary" : "link", p.status === "in" ? "להזמנה" : p.status === "out" ? "עדכנו אותי כשיחזור" : "לבירור");
        a.href = "/contact/?product=" + encodeURIComponent(p.name || "");
        c.appendChild(a);
        box.appendChild(c);
      });
    }).catch(function () {});
  }
})();
