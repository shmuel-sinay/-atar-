/* In-page confirmation dialog: ktAsk(text, {ok, cancel, danger}) -> Promise<boolean> */
(function () {
  var css = ".ktask{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:16px;background:#0f172a73;animation:ktf .15s ease-out}" +
    ".ktask-box{width:min(420px,100%);background:var(--card,#fff);color:var(--ink,#18202e);border-radius:12px;box-shadow:0 20px 50px #0004;overflow:hidden;direction:rtl;font-family:inherit;animation:ktu .18s ease-out}" +
    ".ktask-box p{margin:0;padding:22px 24px 8px;font-size:1.05rem;line-height:1.7;white-space:pre-line}" +
    ".ktask-act{display:flex;gap:8px;justify-content:flex-start;padding:16px 24px 20px}" +
    ".ktask-act button{font:inherit;font-weight:600;border-radius:8px;padding:9px 20px;cursor:pointer;border:1px solid var(--line,#dfe3ea);background:var(--card,#fff);color:var(--ink,#18202e)}" +
    ".ktask-act .ok{background:var(--brand,#1e4f8f);border-color:var(--brand,#1e4f8f);color:#fff}" +
    ".ktask-act .ok.danger{background:var(--bad,#b42318);border-color:var(--bad,#b42318)}" +
    ".ktask-act button:focus-visible{outline:2px solid var(--brand,#1e4f8f);outline-offset:2px}" +
    "@keyframes ktf{from{opacity:0}}@keyframes ktu{from{transform:translateY(8px);opacity:0}}" +
    "@media (prefers-reduced-motion:reduce){.ktask,.ktask-box{animation:none}}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  window.ktAsk = function (text, o) {
    o = o || {};
    return new Promise(function (done) {
      var prev = document.activeElement;
      var wrap = document.createElement("div"); wrap.className = "ktask";
      var box = document.createElement("div"); box.className = "ktask-box";
      box.setAttribute("role", "alertdialog"); box.setAttribute("aria-modal", "true");
      var p = document.createElement("p"); p.textContent = text; p.id = "ktask-t"; box.setAttribute("aria-labelledby", "ktask-t");
      var act = document.createElement("div"); act.className = "ktask-act";
      var ok = document.createElement("button"); ok.type = "button"; ok.className = "ok" + (o.danger ? " danger" : ""); ok.textContent = o.ok || "אישור";
      var no = document.createElement("button"); no.type = "button"; no.textContent = o.cancel || "ביטול";
      act.appendChild(ok); act.appendChild(no); box.appendChild(p); box.appendChild(act); wrap.appendChild(box);
      function close(v) { document.removeEventListener("keydown", key, true); wrap.remove(); if (prev && prev.focus) prev.focus(); done(v); }
      function key(e) {
        if (e.key === "Escape") { e.preventDefault(); close(false); }
        else if (e.key === "Tab") { e.preventDefault(); (document.activeElement === ok ? no : ok).focus(); }
      }
      ok.addEventListener("click", function () { close(true); });
      no.addEventListener("click", function () { close(false); });
      wrap.addEventListener("click", function (e) { if (e.target === wrap) close(false); });
      document.addEventListener("keydown", key, true);
      document.body.appendChild(wrap); ok.focus();
    });
  };
})();
