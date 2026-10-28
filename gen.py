# -*- coding: utf-8 -*-
import os, html
OUT = os.environ.get("KT_OUT", ".")
PHONE_DISPLAY = "055-440-7560"
PHONE_TEL = "0554407560"
EMAIL = "g47ben@gmail.com"

ICONS = {
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/></svg>',
 "win": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
 "code": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>',
 "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6z"/><path d="m9 12 2 2 4-4"/></svg>',
 "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>',
 "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>',
 "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
}

NAV = [("/", "בית"), ("/services/", "שירותים"), ("/android/", "אנדרואיד"), ("/shop/", "חנות"),
       ("/request/", "בקשת פיתוח"), ("/contact/", "צור קשר")]

def head(title, desc, path):
    nav = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == path else "", t) for h, t in NAV)
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#0a3326">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="/"><img src="/assets/logo.svg" alt="" width="40" height="40"><span>כושר טק<small>טכנולוגיה מותאמת לציבור</small></span></a>
  <nav class="main" aria-label="ראשי">{nav}</nav>
</div></header>
<main>
'''

def foot():
    return f'''</main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><h4>כושר טק</h4><p>פתרונות טכנולוגיה מותאמים לציבור: אנדרואיד, מחשבים ותוכנות. מקצועי, מהיר ובמחיר שפוי.</p></div>
    <div><h4>ניווט</h4><ul>{"".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in NAV)}</ul></div>
    <div><h4>יצירת קשר</h4><ul><li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/contact/">טופס פנייה</a></li></ul></div>
  </div>
  <div class="legal">התקנות תוכנה נעשות ברישיון חוקי או בתוכנות חינמיות וקוד פתוח. © כושר טק</div>
</div></footer>
<script src="/assets/site.js" defer></script>
</body></html>
'''

SVC_BY_TITLE = {"התאמת אנדרואיד": "android", "מחשבים ו-Office": "computers", "התאמת מחשבים והתקנת Office": "computers",
                "תוכנות בהתאמה אישית": "software", "בניית אתרים": "websites", "חנות": "shop"}

def card(icon, title, text, bullets=None, price="מחיר סימלי", link=None, svc=None):
    svc = svc or SVC_BY_TITLE.get(title)
    sattr = ' data-svc="%s"' % svc if svc else ""
    b = "".join("<li>%s</li>" % x for x in bullets) if bullets else ""
    ul = "<ul>%s</ul>" % b if b else ""
    l = '<a class="link" href="%s">לפרטים ←</a>' % link if link else ""
    return f'<article class="card"><div class="ico">{ICONS[icon]}</div><h3>{title}</h3><p>{text}</p>{ul}<p><span class="price"{sattr}>{price}</span></p>{l}</article>'

def write(path, content):
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)

# ---------- HOME ----------
home = head("כושר טק | טכנולוגיה מותאמת, מקצועית ובמחיר שפוי", "כושר טק: התאמת אנדרואיד, התקנות מחשב, תוכנות בהתאמה אישית ובניית אתרים, לציבור שומר תורה ומצוות.", "/")
home += f'''
<section class="hero"><div class="wrap">
  <div>
    <span class="badge">שנים של ניסיון · מחירים שפויים</span>
    <h1>טכנולוגיה <em>מותאמת</em> בדיוק אליך.<br>בלי לשלם סכומי עתק.</h1>
    <p class="lead">התאמת מכשירי אנדרואיד, התקנות מחשב, תוכנות בהתאמה אישית ואתרים. עבודה מסודרת, זריזה ומקצועית, במחיר שמתאים לכל כיס.</p>
    <div class="cta"><a class="btn primary" href="/contact/">קבלת הצעה</a><a class="btn ghost" href="/services/">לכל השירותים</a></div>
  </div>
  <img class="mark" src="/assets/logo.svg" alt="" width="300" height="300">
</div></section>

<section class="block"><div class="wrap">
  <h2 class="title">במה אנחנו מתמחים</h2>
  <p class="sub">המומחיות העיקרית שלנו היא אנדרואיד: מכשירים מותאמים ומסוננים לפי הצורך, עד רמת הקושחה.</p>
  <div class="grid c3">
    {card("phone","התאמת אנדרואיד","רוט, גרסה מותאמת אישית ובניית קושחה מוכנה לצריבה.",["הסרת אפליקציות ודפדפנים מובנים","הסרת חיבור אינטרנט מהמכשיר","עריכת מתקין החבילות"],link="/android/")}
    {card("win","מחשבים ו-Office","התאמת מחשבים חדשים והתקנת Windows ו-Office.",["התקנה נקייה ומסודרת","Office ברישיון חוקי או LibreOffice חינמי","תוכנות חינמיות וקוד פתוח"],link="/services/")}
    {card("code","תוכנות בהתאמה אישית","תוכנה שנבנית במהירות עם כלי בינה מלאכותית, במחיר של חלק ממה שמבקשים מתכנת.",None,link="/request/")}
    {card("globe","בניית אתרים","אתר עסקי נקי ומהיר, בלי תלות בספקים יקרים.",None,link="/contact/")}
    {card("box","חנות","מנגני אנדרואיד ומוצרים נוספים. מלאי מתעדכן, ואפשר להשאיר פרטים.",None,link="/shop/")}
    {card("shield","התאמה לציבור","הכול נעשה בהתאמה לצרכים של הציבור שומר התורה והמצוות.",None,link="/contact/")}
  </div>
</div></section>

<section class="block alt"><div class="wrap">
  <h2 class="title">איך זה עובד</h2>
  <p class="sub">שלושה צעדים, בלי סיבוכים.</p>
  <ol class="steps">
    <li><strong>משאירים פרטים</strong><br>טופס קצר או שיחת טלפון: מה צריך ועל איזה מכשיר.</li>
    <li><strong>מקבלים הצעה</strong><br>מחיר ברור מראש, בלי הפתעות.</li>
    <li><strong>מקבלים תוצאה</strong><br>עבודה מסודרת, בדוקה ומוכנה לשימוש.</li>
  </ol>
</div></section>

<section class="block"><div class="wrap">
  <div class="card" style="display:grid;gap:14px;justify-items:start">
    <h2 class="title" style="margin:0">מה צריך? אפשר לדבר.</h2>
    <p class="sub" style="margin:0">השאר פרטים ונחזור אליך. {PHONE_DISPLAY} · {EMAIL}</p>
    <a class="btn primary" href="/contact/">לטופס הפנייה</a>
  </div>
</div></section>
'''
home += foot()
write("/", home)
# write() with "/" makes site/index.html
# ---------- SERVICES ----------
s = head("שירותים | כושר טק", "כל השירותים של כושר טק: אנדרואיד, מחשבים, תוכנות ואתרים.", "/services/")
s += '''<section class="pagehead"><div class="wrap"><h1>השירותים שלנו</h1><p>מחירים סימליים ומותאמים. כל עבודה מתומחרת מראש בהצעה ברורה.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c2">'''
s += card("phone","התאמת אנדרואיד","השירות המרכזי שלנו, מרוט ועד קושחה שלמה.",["רוט למכשירים נתמכים","בניית גרסה מותאמת אישית","קושחה מוכנה לצריבה ב-SP Flash Tool","הסרת אפליקציות ודפדפנים מובנים","הסרת דרייברים של חיבור אינטרנט","עריכת מתקין החבילות"],link="/android/")
s += card("win","התאמת מחשבים והתקנת Office","התאמת מחשבים חדשים והתקנת Windows ו-Office, נקי, מהיר ומסודר.",["התאמת מחשבים חדשים","התקנת Windows מקובץ ISO רשמי","התקנת Office ברישיון חוקי, או LibreOffice חינמי","דרייברים, הגדרות והסרת תוכנות מיותרות"])
s += card("code","תוכנות בהתאמה אישית","צריך כלי קטן שיעשה בדיוק מה שאתה צריך? אפשר לקבל אותו מהר.",["סקריפטים וכלי שירות","כלים לעסקים קטנים","בנייה מהירה בעזרת בינה מלאכותית, במחיר נמוך"],link="/request/")
s += card("globe","בניית אתרים","אתר עסקי או אישי, נקי וקל לתחזוקה.",["עיצוב מותאם","אחסון וכתובת","טופס פנייה למייל"])
s += '''</div></div></section>
<section class="block alt"><div class="wrap"><div class="note"><strong>שימו לב:</strong> אנחנו עובדים רק עם תוכנות חינמיות, קוד פתוח או תוכנות ברישיון חוקי. אין התקנה של תוכנות פרוצות.</div></div></section>
'''
s += foot()
write("/services/", s)
# ---------- ANDROID ----------
a = head("התאמת אנדרואיד | כושר טק", "רוט, קושחה מותאמת אישית, הסרת אפליקציות ודפדפנים והסרת חיבור אינטרנט ממכשירי אנדרואיד.", "/android/")
a += '''<section class="pagehead"><div class="wrap"><h1>התאמת אנדרואיד</h1><p>המומחיות העיקרית שלנו. מכשיר שעושה רק מה שאתה רוצה, ושום דבר מעבר לכך.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c3">'''
a += card("shield","רוט והתאמה","הרשאות מלאות על המכשיר והגדרה מדויקת של מה שמותר ומה לא.",["רוט למכשירים נתמכים","התאמת הגדרות מערכת"])
a += card("phone","קושחה מותאמת אישית","בונים גרסה ייעודית למכשיר שלך, מוכנה לצריבה.",["קובץ מוכן לצריבה ב-SP Flash Tool","הסרת אפליקציות מובנות","עריכת מתקין החבילות"])
a += card("bolt","מכשיר סגור לרשת","מכשיר ללא חיבור אינטרנט, על ידי הסרת הדרייברים הרלוונטיים.",["הסרת דרייברים של Wi-Fi ונתונים","הסרת דפדפנים"])
a += '''</div></div></section>
<section class="block alt"><div class="wrap">
<h2 class="title">איך מתחילים</h2>
<p class="sub">שלח את דגם המכשיר ואת מה שאתה צריך, ונחזיר הצעה ברורה.</p>
<a class="btn primary" href="/contact/">שליחת פרטים</a>
</div></section>
'''
a += foot()
write("/android/", a)
# ---------- SHOP ----------
sh = head("חנות | כושר טק", "מנגני אנדרואיד ומוצרים נוספים.", "/shop/")
sh += f'''<section class="pagehead"><div class="wrap"><h1>חנות</h1><p>מוצרים שנבחרו בקפידה. התשלום והמסירה נעשים בתיאום ישיר.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c3" id="products">
<article class="card"><div class="ico">{ICONS["phone"]}</div><h3>נגן אנדרואיד M393</h3><p>נגן עם אנדרואיד 13, מותאם אישית לפי בקשה.</p><p><span class="stock">אזל מהמלאי</span></p><a class="btn ghost" style="color:var(--green)" href="/contact/">עדכנו אותי כשיחזור</a></article>
<article class="card"><div class="ico">{ICONS["box"]}</div><h3>דגמים נוספים</h3><p>יש דגמים נוספים בהזמנה מיוחדת. אפשר לברר זמינות ומחיר.</p><p><span class="price" data-svc="shop">לפי דגם</span></p><a class="link" href="/contact/">לבירור ←</a></article>
</div>
<div class="note" style="margin-top:24px">התשלום אינו מתבצע באתר. אחרי יצירת קשר נתאם הכול ישירות.</div></div></section>
'''
sh += foot()
write("/shop/", sh)
# ---------- REQUEST ----------
r = head("בקשת פיתוח | כושר טק", "פלטפורמה לבקשת פיתוח תוכנה במחירים אוטומטיים.", "/request/")
r += f'''<section class="pagehead"><div class="wrap"><h1>בקשת פיתוח</h1><p>פלטפורמה בהקמה: מבקשים תוכנה, ומפתחים מבצעים אותה במחירים שנקבעים אוטומטית.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c2">
<article class="card"><div class="ico">{ICONS["code"]}</div><h3>מבקשים</h3><p>מתארים מה צריך, מקבלים מחיר מיידי וממתינים לביצוע. בלי מו"מ ובלי הפתעות.</p><p><span class="price" data-svc="request">מחיר אוטומטי</span></p></article>
<article class="card"><div class="ico">{ICONS["bolt"]}</div><h3>מבצעים</h3><p>מפתחים בוחרים בקשות שמתאימות להם ומקבלים תמורה לפי מחירון האתר.</p></article>
</div>
<div class="note" style="margin-top:24px"><strong>בקרוב.</strong> בינתיים אפשר לשלוח בקשת פיתוח ישירות בטופס הפנייה, ונחזור עם מחיר.</div>
<p style="margin-top:20px"><a class="btn primary" href="/contact/?subject=פיתוח">שליחת בקשה</a></p></div></section>
'''
r += foot()
write("/request/", r)
# /chat/ is a separate project (built chat app), not linked from this site and not generated here.
# ---------- CONTACT ----------
k = head("צור קשר | כושר טק", "טופס פנייה, טלפון ומייל.", "/contact/")
k += f'''<section class="pagehead"><div class="wrap"><h1>צור קשר</h1><p>השאר פרטים ונחזור אליך. אפשר גם להתקשר: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div></section>
<section class="block"><div class="wrap">
<form class="contact" id="cf" novalidate>
  <label>שם<input name="name" autocomplete="name" required></label>
  <label>טלפון או מייל<input name="contact" autocomplete="tel" required></label>
  <label>במה מדובר<select name="subject">
    <option>התאמת אנדרואיד</option><option>התקנת מחשב</option><option>תוכנה בהתאמה אישית</option>
    <option>בניית אתר</option><option>חנות / מוצרים</option><option value="פיתוח">בקשת פיתוח</option><option>אחר</option></select></label>
  <label>פרטים<textarea name="message" rows="5" required></textarea></label>
  <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
  <button class="btn primary" type="submit">שליחה</button>
  <div id="formmsg" role="status" aria-live="polite"></div>
</form>
<p style="margin-top:22px;color:var(--ink-soft)">ישיר: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div></section>
<script>
(function(){{
  var f=document.getElementById('cf'),m=document.getElementById('formmsg');
  try{{var q=new URLSearchParams(location.search).get('subject');if(q){{for(var i=0;i<f.subject.options.length;i++){{if(f.subject.options[i].value===q||f.subject.options[i].text===q){{f.subject.selectedIndex=i}}}}}}}}catch(e){{}}
  f.addEventListener('submit',function(e){{
    e.preventDefault();
    if(!f.name.value.trim()||!f.contact.value.trim()||!f.message.value.trim()){{m.textContent='נא למלא שם, דרך קשר ופרטים.';return}}
    m.textContent='שולח...';
    fetch('/api/contact',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{name:f.name.value,contact:f.contact.value,subject:f.subject.value,message:f.message.value,website:f.website.value}})}})
    .then(function(r){{if(!r.ok)throw 0;return r.json()}})
    .then(function(){{f.reset();m.textContent='תודה, קיבלנו. נחזור אליך בהקדם.'}})
    .catch(function(){{m.innerHTML='לא הצלחנו לשלוח. אפשר להתקשר או לשלוח מייל: <a href="mailto:{EMAIL}">{EMAIL}</a>'}});
  }});
}})();
</script>
'''
k += foot()
write("/contact/", k)
# home written into site/index.html (the helper wrote it to site/index.html via "")
print("pages generated")
