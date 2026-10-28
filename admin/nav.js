(function () {
  var app = document.getElementById("app");
  if (!app) return;
  var GROUPS = [
    ["האתר הפרטי (כושר טק)", [["האתר", "/"], ["ניהול האתר", "/admin/"], ["טופס פנייה", "/contact/"]]],
    ["הצ'אט של הוועד", [["הצ'אט", "/chat/"], ["כניסת מנהל-על", "/chat/#/dev"]]],
    ["הפורום (מלאכת מחשבת)", [["הפורום", "/market/"], ["ניהול הפורום", "/market/admin/"], ["כללי הפורום", "/market/rules/"]]],
    ["השרת", [["שולחן עבודה", "/desktop/"], ["ניהול השרת", "/panel/"]]]
  ];
  var nav = document.createElement("nav");
  nav.className = "box";
  nav.setAttribute("aria-label", "ניווט מהיר");
  GROUPS.forEach(function (g) {
    var row = document.createElement("div");
    row.style.cssText = "display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:4px 0";
    var label = document.createElement("strong");
    label.textContent = g[0] + ":";
    label.style.cssText = "min-width:170px";
    row.appendChild(label);
    g[1].forEach(function (l) {
      var a = document.createElement("a");
      a.className = "sm";
      a.textContent = l[0];
      a.href = l[1];
      a.style.cssText = "text-decoration:none;display:inline-block";
      row.appendChild(a);
    });
    nav.appendChild(row);
  });
  app.insertBefore(nav, app.firstChild);
})();
