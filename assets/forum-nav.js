/* Fills the header links of forum pages that do not run the board app (rules page). */
(function () {
  var box = document.getElementById("fuser");
  if (!box) return;
  function link(text, href) { var a = document.createElement("a"); a.textContent = text; a.href = href; box.appendChild(a); }
  fetch("/api/m/me", { credentials: "same-origin" }).then(function (r) { return r.json(); }).then(function (r) {
    var u = r.user;
    if (!u) { link("התחברות", "/market/#/login"); link("הרשמה", "/market/#/register"); return; }
    var items = u.role === "client" ? [["הבקשות שלי", "requests"], ["בקשה חדשה", "new"], ["הודעות", "messages"], ["שותפים", "partners"]]
      : u.status === "active" ? [["בקשות פתוחות", "open"], ["העבודות שלי", "mine"], ["הודעות", "messages"], ["הפרופיל", "profile"], ["שותפים", "partners"]]
      : [["הפרופיל", "profile"]];
    items.forEach(function (i) { link(i[0], "/market/#/" + i[1]); });
  }).catch(function () {});
})();
