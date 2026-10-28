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
  // "עזרה בהתאמת נגן": plain questions, no technical words, ends with a player and a level
  var qbox = document.getElementById("quiz");
  if (qbox) {
    var ans = {}, step = 0;
    var Q = [
      { k: "who", q: "למי הנגן?", opts: [["me", "בשבילי"], ["child", "בשביל ילד או נער"], ["gift", "מתנה למישהו אחר"]] },
      { k: "use", q: "בשביל מה הנגן?", hint: "אפשר לבחור כמה תשובות.", multi: true, opts: [
        ["shiurim", "לשמוע שיעורים"], ["music", "לשמוע שירים וניגונים"], ["learn", "לחזור על לימוד"],
        ["record", "להקליט"], ["games", "משחקים"], ["apps", "תוכנה מסוימת שאני צריך"], ["light", "גם כפנס או למצלמה"]] },
      { k: "video", q: "תרצה לראות בו סרטונים?", opts: [["no", "לא, רק לשמוע"], ["own", "רק סרטונים שאצלם בעצמי במכשיר"], ["yes", "כן, גם סרטונים מבחוץ"]] },
      { k: "add", q: "תרצה להוסיף לו תוכנות בעתיד?", hint: "\"תוכנה\" כאן היא כל דבר שמוסיפים לנגן: למשל ספר שיעורים, לוח זמנים, או משהו לעבודה.", opts: [
        ["none", "לא, מספיק לי מה שיש בו"], ["safe", "כן, אבל רק מרשימה בטוחה שבדקתם"], ["any", "כן, גם דברים שאביא בעצמי"]] },
      { k: "cam", q: "צריך מצלמה או פנס?", opts: [["no", "לא צריך"], ["light", "רק פנס"], ["cam", "כן, מצלמה"]] }
    ];
    var TIER = { none: "שמור", safe: "שמור עם חנות פנימית", any: "עם התקנה מבחוץ" };
    function draw() {
      qbox.textContent = "";
      var head = el("div", "qhead");
      head.appendChild(el("h2", null, "עזרה בהתאמת נגן"));
      head.appendChild(el("p", null, "כמה שאלות פשוטות, ונמליץ על הנגן והרמה שמתאימים לך. לא צריך להבין בטכנולוגיה."));
      qbox.appendChild(head);
      if (step >= Q.length) return result();
      var cur = Q[step];
      var bar = el("div", "qbar"); var fill = el("span"); fill.style.width = Math.round(step / Q.length * 100) + "%"; bar.appendChild(fill); qbox.appendChild(bar);
      qbox.appendChild(el("h3", "qq", cur.q));
      if (cur.hint) qbox.appendChild(el("p", "qhint", cur.hint));
      var opts = el("div", "qopts"), picked = (ans[cur.k] || []).slice ? (ans[cur.k] || []).slice() : [];
      cur.opts.forEach(function (o) {
        var b = el("button", "qopt" + (cur.multi && picked.indexOf(o[0]) >= 0 ? " on" : ""), o[1]); b.type = "button";
        b.addEventListener("click", function () {
          if (!cur.multi) { ans[cur.k] = o[0]; step++; return draw(); }
          var i = picked.indexOf(o[0]); if (i >= 0) picked.splice(i, 1); else picked.push(o[0]);
          b.className = "qopt" + (picked.indexOf(o[0]) >= 0 ? " on" : ""); ans[cur.k] = picked; next.disabled = !picked.length;
        });
        opts.appendChild(b);
      });
      qbox.appendChild(opts);
      var nav = el("div", "qnav");
      if (step) { var back = el("button", "btn ghost", "חזרה"); back.type = "button"; back.addEventListener("click", function () { step--; draw(); }); nav.appendChild(back); }
      if (cur.multi) { var next = el("button", "btn primary", "המשך"); next.type = "button"; next.disabled = !picked.length; next.addEventListener("click", function () { step++; draw(); }); nav.appendChild(next); }
      qbox.appendChild(nav);
    }
    function result() {
      var use = ans.use || [];
      var plus = ans.cam === "cam" || ans.cam === "light" || ans.video === "own" || use.indexOf("light") >= 0;
      var player = plus ? "הזמיר פלוס" : "הזמיר", tier = TIER[ans.add] || "שמור";
      var wantsApps = use.indexOf("apps") >= 0 || use.indexOf("games") >= 0;
      if (wantsApps && tier === "שמור") tier = "שמור עם חנות פנימית";
      var kid = ans.who === "child";
      if (kid && ans.add === "any") tier = "שמור עם חנות פנימית";
      var r = el("div", "qres");
      r.appendChild(el("span", "qlabel", "ההמלצה שלנו"));
      r.appendChild(el("h3", null, player + " · " + tier));
      var why = el("ul");
      why.appendChild(el("li", null, plus ? "בזמיר פלוס יש פי שניים מקום, פנס ומצלמה (ואפשר גם בלי מצלמה)." : "הזמיר קטן, פשוט ונוח, ומתאים בדיוק לשמיעה וללימוד."));
      why.appendChild(el("li", null, tier === "שמור" ? "ברמה השמורה יש רק מה שצריך: נגן, רדיו, הקלטה ושיעורים. אי אפשר להוסיף שום דבר, ולכן אין מה לעקוף." :
        tier === "שמור עם חנות פנימית" ? "אפשר להוסיף תוכנות, אבל רק מתוך רשימה שאנחנו בדקנו ואישרנו." : "אפשר להוסיף גם דברים מבחוץ, ועדיין אין בו אינטרנט ואין בו סרטים."));
      if (kid && ans.add === "any") why.appendChild(el("li", null, "לילד או לנער אנחנו ממליצים על רשימה בטוחה בלבד, ולא על הוספה מבחוץ."));
      if (ans.who === "gift") why.appendChild(el("li", null, "למתנה: אפשר לשנות רמה גם אחרי שהנגן אצל מי שקיבל אותו."));
      if (wantsApps) why.appendChild(el("li", null, (use.indexOf("games") >= 0 && use.indexOf("apps") >= 0 ? "משחקים ותוכנות" : use.indexOf("games") >= 0 ? "משחקים" : "את התוכנה שצריך") + " מוסיפים מתוך הרשימה הבטוחה שלנו" + (ans.add === "any" ? ", או מבחוץ לפי בחירתך." : ".")));
      if (ans.video === "own") why.appendChild(el("li", null, "אפשר לבדוק גרסה שמאפשרת לראות רק סרטונים שצולמו במכשיר עצמו, בלי שום אפשרות להכניס סרטים מבחוץ. נבדוק את זה איתך בהזמנה."));
      if (ans.video === "yes") why.appendChild(el("li", "qwarn", "סרטונים מבחוץ לא יהיו: אין אצלנו נגנים כאלה, וזה בכוונה. אנחנו לא מוכרים מה שאנחנו לא עומדים מאחוריו."));
      why.appendChild(el("li", null, "בכל מקרה: בלי אינטרנט ובלי אפשרות להכניס סרטים, ואפשר לשנות רמה גם אחר כך."));
      r.appendChild(why);
      var acts = el("div", "qnav");
      var go = el("a", "btn primary", "להזמנה עם ההתאמה הזאת");
      go.href = "/contact/?product=" + encodeURIComponent(player + " · " + tier + (kid ? " · לילד או נער" : "") + (ans.video === "own" ? " · סרטונים שצולמו במכשיר בלבד" : ""));
      var again = el("button", "btn ghost", "להתחיל מחדש"); again.type = "button";
      again.addEventListener("click", function () { ans = {}; step = 0; draw(); });
      acts.appendChild(go); acts.appendChild(again); r.appendChild(acts);
      qbox.appendChild(r);
    }
    draw();
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
        if (p.tiers) {
          var TIERS = ["שמור", "שמור עם חנות פנימית", "עם התקנה מבחוץ"];
          var pick = el("div", "tierpick");
          pick.appendChild(el("span", null, "רמת הכשרה:"));
          TIERS.forEach(function (t, i) {
            var b = el("button", i ? "" : "on", t); b.type = "button";
            b.addEventListener("click", function () {
              Array.prototype.forEach.call(pick.querySelectorAll("button"), function (x) { x.className = x === b ? "on" : ""; });
              a.href = "/contact/?product=" + encodeURIComponent((p.name || "") + " · " + t);
            });
            pick.appendChild(b);
          });
          a.href = "/contact/?product=" + encodeURIComponent((p.name || "") + " · " + TIERS[0]);
          c.appendChild(pick);
        }
        c.appendChild(a);
        box.appendChild(c);
      });
    }).catch(function () {});
  }
})();
