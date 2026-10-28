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
  // what can be on a player: shown as a catalog on the shop page and used by the "עזרה בהתאמת נגן" questions
  var CATALOG = [
    { k: "listen", t: "שמיעה והקלטה", d: "נגן לשיעורים ולשירים, רדיו, רשמקול, וחיתוך של קטעי שמע.", base: true },
    { k: "sfarim", t: "ספרי קודש", d: "סידור, תהילים, תנ\"ך, משניות, גמרא, הלכה וספרי מוסר. הכול בתוך הנגן." },
    { k: "jewish", t: "עזרים ליהדות", d: "לוח עברי, ברכות, תפילת הדרך, מילון ארמי ועוד." },
    { k: "tools", t: "כלים ליום יום", d: "מחשבון, פתקים, יומן, שעון מעורר, קורא מסמכים ומד צעדים.", base: true },
    { k: "maps", t: "מפות וניווט", d: "מפות שעובדות בלי אינטרנט, וקווי אוטובוסים." },
    { k: "voice", t: "הקראה וכתיבה בקול", d: "הנגן מקריא טקסט בעברית, ומקליד את מה שאומרים לו." },
    { k: "translate", t: "תרגום", d: "תרגום מילים ומשפטים, גם בלי אינטרנט." },
    { k: "music", t: "כלי נגינה", d: "אורגן, תופים, מכוון לגיטרה ולימוד תווים." },
    { k: "games", t: "משחקים", d: "בדרך כלל אין. אם חשוב לך, אפשר לבקש משחקים שקטים ומתאימים מתוך רשימה שבדקנו.", quizOnly: true }
  ];
  var catbox = document.getElementById("catalog");
  if (catbox) CATALOG.filter(function (c) { return !c.quizOnly; }).forEach(function (c) {
    var a = el("article", "catitem"); a.appendChild(el("h3", null, c.t)); a.appendChild(el("p", null, c.d));
    if (c.base) a.appendChild(el("span", "cbase", "יש כבר ברמה השמורה"));
    catbox.appendChild(a);
  });

  // "עזרה בהתאמת נגן": a short friendly conversation, one question per screen
  var qbox = document.getElementById("quiz");
  if (qbox) {
    var ans = {}, step = -1;
    var TIER = { none: "שמור", safe: "שמור עם חנות פנימית", any: "עם התקנה מבחוץ" };
    var Q = [
      { k: "who", q: "למי הנגן?", opts: [["me", "בשבילי"], ["child", "בשביל ילד או נער"], ["gift", "מתנה למישהו אחר"]] },
      { k: "want", q: "מה היית רוצה שיהיה בנגן?", hint: "סמן כל מה שמעניין אותך. אם משהו לא ברור, זה בסדר: אפשר לשאול אותנו גם אחר כך.", multi: true,
        opts: CATALOG.map(function (c) { return [c.k, c.t, c.d]; }) },
      { k: "add", q: "ואחרי שתקבל אותו?", hint: "יש מי שרוצה נגן סגור לגמרי, ויש מי שרוצה להוסיף דברים בהמשך. מה מתאים לך?", opts: [
        ["none", "שיישאר רק מה שבחרתי עכשיו", "הכי שמור. אי אפשר להוסיף שום דבר, ולכן גם אין מה לעקוף."],
        ["safe", "שאוכל להוסיף בהמשך, מתוך רשימה שבדקתם", "יש בנגן חנות קטנה משלנו, ורק מה שבדקנו נמצא בה."],
        ["any", "שאוכל להוסיף גם דברים שאביא בעצמי", "לשימוש מתקדם. עדיין בלי אינטרנט ובלי סרטים."]] },
      { k: "cam", q: "צריך פנס או מצלמה?", hint: "אפשר לבחור גם את שניהם.", multi: true, none: "no", opts: [["light", "פנס"], ["cam", "מצלמה"], ["no", "לא צריך אף אחד"]] },
      { k: "video", q: "ולגבי סרטונים", hint: "בנגנים שלנו אין סרטים ואין דרך להכניס סרטונים מבחוץ. זה בכוונה, ולא ישתנה.", opts: [
        ["no", "מצוין, לא צריך"], ["own", "הייתי רוצה לראות רק מה שאני מצלם בעצמי", "את זה אפשר לבדוק: רק סרטונים שצולמו במכשיר עצמו."]] }
    ];
    function optBtn(o, on) {
      var b = el("button", "qopt" + (on ? " on" : "")); b.type = "button";
      b.appendChild(el("strong", null, o[1])); if (o[2]) b.appendChild(el("span", null, o[2]));
      return b;
    }
    function draw() {
      qbox.textContent = "";
      var head = el("div", "qhead");
      head.appendChild(el("h2", null, "עזרה בהתאמת נגן"));
      qbox.appendChild(head);
      if (step < 0) {
        head.appendChild(el("p", null, "לא צריך להבין בטכנולוגיה. נשאל כמה שאלות פשוטות, נראה לך מה אפשר שיהיה בנגן, ונמליץ על מה שמתאים לך. זה לוקח דקה."));
        var go = el("button", "btn primary", "בוא נתחיל"); go.type = "button"; go.addEventListener("click", function () { step = 0; draw(); });
        qbox.appendChild(go); return;
      }
      if (step >= Q.length) return result();
      var cur = Q[step];
      var bar = el("div", "qbar"); var fill = el("span"); fill.style.width = Math.round((step + 1) / (Q.length + 1) * 100) + "%"; bar.appendChild(fill); qbox.appendChild(bar);
      qbox.appendChild(el("h3", "qq", cur.q));
      if (cur.hint) qbox.appendChild(el("p", "qhint", cur.hint));
      var opts = el("div", "qopts" + (cur.k === "want" ? " wide" : "")), picked = cur.multi ? (ans[cur.k] || []).slice() : [];
      var next = el("button", "btn primary", "המשך"); next.type = "button";
      cur.opts.forEach(function (o) {
        var b = optBtn(o, cur.multi && picked.indexOf(o[0]) >= 0);
        b.addEventListener("click", function () {
          if (!cur.multi) { ans[cur.k] = o[0]; step++; return draw(); }
          var i = picked.indexOf(o[0]); if (i >= 0) picked.splice(i, 1); else picked.push(o[0]);
          if (cur.none && i < 0) picked = o[0] === cur.none ? [cur.none] : picked.filter(function (x) { return x !== cur.none; });
          Array.prototype.forEach.call(opts.children, function (x, j) { x.className = "qopt" + (picked.indexOf(cur.opts[j][0]) >= 0 ? " on" : ""); });
          ans[cur.k] = picked; next.disabled = !picked.length;
        });
        opts.appendChild(b);
      });
      qbox.appendChild(opts);
      var nav = el("div", "qnav");
      if (cur.multi) { next.disabled = !picked.length; next.addEventListener("click", function () { step++; draw(); }); nav.appendChild(next); }
      var back = el("button", "btn ghost", "חזרה"); back.type = "button"; back.addEventListener("click", function () { step--; draw(); }); nav.appendChild(back);
      qbox.appendChild(nav);
    }
    function result() {
      var want = ans.want || [], cam = ans.cam || [], kid = ans.who === "child";
      var extras = CATALOG.filter(function (c) { return want.indexOf(c.k) >= 0 && !c.base; });
      var tier = TIER[ans.add] || "שמור";
      var note = "";
      if (extras.length && tier === "שמור") note = "מה שבחרת ייכנס לנגן מראש, וחוץ ממנו לא יהיה אפשר להוסיף דבר.";
      if (kid && ans.add === "any") { tier = "שמור עם חנות פנימית"; note = "לילד או לנער אנחנו ממליצים להוסיף רק מתוך הרשימה שבדקנו, ולא מבחוץ."; }
      var plus = cam.indexOf("cam") >= 0 || cam.indexOf("light") >= 0 || ans.video === "own";
      var player = plus ? "הזמיר פלוס" : "הזמיר";
      var r = el("div", "qres");
      r.appendChild(el("span", "qlabel", "ההמלצה שלנו"));
      r.appendChild(el("h3", null, player + " · " + tier));
      var why = el("ul");
      why.appendChild(el("li", null, plus ? "הזמיר פלוס: פי שניים מקום" + (cam.indexOf("light") >= 0 ? ", פנס" : "") + (cam.indexOf("cam") >= 0 ? ", מצלמה" : "") + "." + (cam.indexOf("cam") < 0 ? " את המצלמה נסגור." : "")
        : "הזמיר: קטן, פשוט ונוח, ומתאים בדיוק למה שבחרת."));
      why.appendChild(el("li", null, "מה שיהיה בנגן: " + CATALOG.filter(function (c) { return c.base || want.indexOf(c.k) >= 0; }).map(function (c) { return c.t; }).join(", ") + "."));
      why.appendChild(el("li", null, tier === "שמור" ? "רמה שמורה: הנגן מגיע מוכן, ואי אפשר להוסיף לו כלום." :
        tier === "שמור עם חנות פנימית" ? "חנות פנימית: אפשר להוסיף בהמשך, אבל רק ממה שבדקנו ואישרנו." : "התקנה מבחוץ: אפשר להוסיף גם דברים שתביא בעצמך."));
      if (note) why.appendChild(el("li", null, note));
      if (ans.video === "own") why.appendChild(el("li", null, "סרטונים שצילמת במכשיר: נבדוק את זה איתך כשנדבר."));
      why.appendChild(el("li", null, "בכל נגן: בלי אינטרנט ובלי סרטים" + (want.indexOf("games") >= 0 ? ". משחקים ייכנסו רק כי ביקשת, ורק מהרשימה שלנו." : " ובלי משחקים.") + " ואם תתחרט, אפשר לשנות אחר כך."));
      r.appendChild(why);
      var details = ["נגן: " + player, "רמה: " + tier, "למי: " + ({ me: "בשבילי", child: "ילד או נער", gift: "מתנה" }[ans.who] || ""),
        "מה שיהיה בנגן: " + CATALOG.filter(function (c) { return c.base || want.indexOf(c.k) >= 0; }).map(function (c) { return c.t; }).join(", "),
        "פנס/מצלמה: " + (cam.indexOf("no") >= 0 ? "לא צריך" : cam.map(function (x) { return x === "cam" ? "מצלמה" : "פנס"; }).join(" ו")),
        ans.video === "own" ? "סרטונים שצולמו במכשיר בלבד" : ""].filter(Boolean).join("\n");
      var acts = el("div", "qnav");
      var go = el("a", "btn primary", "להזמנה עם ההתאמה הזאת");
      go.href = "/contact/?product=" + encodeURIComponent(player + " · " + tier) + "&details=" + encodeURIComponent(details);
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
