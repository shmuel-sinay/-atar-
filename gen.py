# -*- coding: utf-8 -*-
import os, re, html, hashlib
OUT = os.environ.get("KT_OUT", ".")
PHONE_DISPLAY = "055-440-7560"
PHONE_TEL = "0554407560"
EMAIL = "kt3182319@gmail.com"

ICONS = {
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/></svg>',
 "win": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
 "code": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>',
 "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6z"/><path d="m9 12 2 2 4-4"/></svg>',
 "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>',
 "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>',
 "lang": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h9M8.5 3v2M6 5c0 4 2.5 7 6 8M11 5c0 4-3 8-7 9"/><path d="m13 21 4-9 4 9M14.5 18h5"/></svg>',
 "pen": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18z"/><circle cx="11" cy="11" r="2"/></svg>',
 "music": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg>',
 "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
}

def V(path):
    """URL with a content hash, so a changed asset is never served from an old cache."""
    try:
        with open(os.path.join(OUT, path.lstrip("/")), "rb") as f:
            return "/%s?v=%s" % (path.lstrip("/"), hashlib.md5(f.read()).hexdigest()[:8])
    except OSError:
        return path

NAV = [("/", "בית"), ("/services/", "שירותים"), ("/android/", "אנדרואיד"), ("/shop/", "חנות"),
       ("/contact/", "צור קשר")]

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
<link rel="canonical" href="https://kosher-tek.com{path}">
<meta property="og:type" content="website"><meta property="og:locale" content="he_IL"><meta property="og:site_name" content="כושר טק">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="https://kosher-tek.com{path}"><meta property="og:image" content="https://kosher-tek.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/logo-180.png">
<link rel="stylesheet" href="{V("assets/style.css")}">
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
    <div><h4>כושר טק</h4><p>עריכת אנדרואיד מקצועית, מה שטכנאי רגיל לא יודע לעשות. ותוכנות ואפליקציות מהר ובמחירי רצפה.</p></div>
    <div><h4>ניווט</h4><ul>{"".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in NAV)}</ul></div>
    <div><h4>יצירת קשר</h4><ul><li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/contact/">טופס פנייה</a></li></ul></div>
  </div>
  <div class="legal">© כושר טק</div>
</div></footer>
<script src="{V("assets/site.js")}" defer></script>
</body></html>
'''

SITE = "https://kosher-tek.com"
ORG_JSONLD = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","name":"כושר טק",
"url":"%s/","logo":"%s/assets/logo-512.png","image":"%s/assets/og.png","telephone":"+972-55-440-7560","email":"%s",
"description":"עריכה והתאמה מקצועית של מכשירי אנדרואיד ונגנים, ברמה שטכנאי רגיל לא מגיע אליה, לציבור שומר תורה ומצוות. וגם תוכנות ואפליקציות מהר ובמחירי רצפה.",
"areaServed":"IL","priceRange":"₪","knowsAbout":["פיתוח אפליקציות אנדרואיד","תוכנות למחשב","MDM","רוט","קושחה","סינון מכשירים"]}</script>
""" % (SITE, SITE, SITE, EMAIL)

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
CTA_BAND = f'''
<section class="ctaband"><div class="wrap">
  <div>
    <h2>יש לך מכשיר או רעיון? נשמח לשמוע.</h2>
    <p>מספרים מה צריך ועל איזה מכשיר, ומקבלים הצעה ברורה ומחיר מראש, בלי התחייבות.</p>
  </div>
  <div class="ctaacts">
    <a class="btn primary" href="/contact/">השארת פרטים</a>
    <a class="ctaline" href="tel:{PHONE_TEL}"><span>טלפון</span>{PHONE_DISPLAY}</a>
    <a class="ctaline" href="mailto:{EMAIL}"><span>מייל</span>{EMAIL}</a>
  </div>
</div></section>
'''

home = head("כושר טק | עריכת אנדרואיד מקצועית: מה שטכנאי רגיל לא יודע לעשות",
            "עריכה והכשרה של מכשירי אנדרואיד ונגנים ברמה שטכנאי רגיל לא מגיע אליה: MDM, רוט, קושחה ייעודית והסרת אינטרנט, לציבור שומר תורה ומצוות. מחשבים מסוננים, תוכנות ואפליקציות מהר ובמחירי רצפה. " + PHONE_DISPLAY, "/")
home += f'''
<section class="hero"><div class="wrap">
  <div>
    <span class="badge">מומחה לעריכת אנדרואיד</span>
    <h1>מה שטכנאי רגיל <em>לא יודע</em> לעשות באנדרואיד.<br>וגם מה שלא שווה לשלם לו עליו.</h1>
    <p class="lead">עריכה והכשרה של מכשירי אנדרואיד ונגנים בכל רמה: מחסימה וניהול ועד בניית מערכת מחדש. עבודות שרוב הטכנאים לא נוגעים בהן, או שגובים עליהן סכום שלא מצדיק את עצמו. ובנוסף תוכנות, אפליקציות ואתרים, מהר ובמחירי רצפה שאי אפשר להתחרות בהם.</p>
    <div class="cta"><a class="btn primary" href="/contact/?subject=אנדרואיד">לעריכת מכשיר</a><a class="btn ghost" href="/android/">מה אפשר לעשות</a></div>
  </div>
  <img class="mark" src="/assets/logo.svg" alt="" width="300" height="300">
</div></section>

<section class="block"><div class="wrap">
  <h2 class="title">מה אנחנו עושים</h2>
  <p class="sub">המומחיות היא עריכת אנדרואיד. בתוכנות, באפליקציות ובאתרים היתרון הוא מהירות ומחיר.</p>
  <div class="grid c3">
    {card("shield","עריכת מכשירי אנדרואיד","ההתמחות המרכזית: עבודות שטכנאי רגיל לא יודע לבצע, או שאצלו לא שוות את המחיר.",["חסימה וניהול מכשיר (MDM)","רוט ועריכת המערכת מבפנים","קושחה ייעודית","הסרת אינטרנט, דפדפנים וחנות, ושאר התאמות"],link="/android/",svc="android")}
    {card("music","הכשרת נגנים","הכשרה מלאה של נגני אנדרואיד מכל הדגמים, כך שיישארו כלי לשמיעה וללימוד בלבד.",["הסרת האינטרנט מהמערכת","שלוש רמות הכשרה, בלי סרטים","טעינת שיעורים ותכנים לפי בקשה"],link="/contact/?subject=אנדרואיד",svc="players")}
    {card("win","מחשבים: מסוננים או בלי אינטרנט","התאמת מחשבים לבית, לעסק ולמוסד: אינטרנט מסונן בלבד, או מחשב בלי אינטרנט בכלל.",["חיבור לסינון ברמת הספק, בשיטת נטפרי","הסרת האינטרנט ברמת התוכנה וברמת החומרה","התקנת Windows ו-Office נקייה"],link="/services/",svc="computers")}
    {card("phone","אפליקציות אנדרואיד","אפליקציה ייעודית לעסק, למוסד או למכשיר סגור. מוכנה מהר, במחיר שאי אפשר להתחרות בו.",["אפליקציות חדשות מאפס","שיפור והתאמה של אפליקציות קיימות","אפליקציות שעובדות בלי אינטרנט"],link="/contact/?subject=פיתוח",svc="apps")}
    {card("code","תוכנות למחשב","כלי שעושה בדיוק את מה שצריך. מהר וזול, בלי לשלם סכומי עתק למתכנת.",["תוכנות וכלים בהתאמה אישית","אוטומציה לאקסל, לקבצים ולעבודה משרדית","כלים לעסקים, למוסדות ולגמ\"חים"],link="/contact/?subject=פיתוח",svc="software")}
    {card("globe","בניית אתרים","אתר תדמית או אתר עסקי: מעוצב, מהיר ומוכן לחיפוש בגוגל, במחיר רצפה.",["מותאם לטלפון ולמחשב","טופס פנייה שמגיע ישר למייל","ממשק לעדכון תכנים בעצמך"],link="/contact/?subject=אתר",svc="websites")}
  </div>
  <p class="more-svc">ועוד: תרגום אפליקציות לעברית · עיצוב לוגו, פרסומות ותמונות · תוספים וסקריפטים · <a href="/services/">לכל השירותים והמחירון ←</a></p>
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
'''
home += CTA_BAND
home += ORG_JSONLD
home += foot()
write("/", home)
# ---------- SERVICES ----------
s = head("שירותים ומחירון | כושר טק",
         "כל השירותים של כושר טק ומחירון: עריכת מכשירי אנדרואיד והכשרת נגנים, מחשבים מסוננים או בלי אינטרנט, אפליקציות ותוכנות, אתרים, תרגום אפליקציות, עיצוב ותוספים.", "/services/")
s += '''<section class="pagehead"><div class="wrap"><h1>השירותים שלנו</h1><p>המומחיות: עריכת אנדרואיד שטכנאי רגיל לא מגיע אליה. בתוכנות, באפליקציות ובאתרים: מהירות ומחירי רצפה שאי אפשר להתחרות בהם.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c2">'''
s += card("shield","עריכת מכשירי אנדרואיד","ההתמחות המרכזית. עבודות שטכנאי רגיל לא יודע לבצע, או שאצלו לא שוות את המחיר.",["חסימה וניהול מכשיר (MDM), בלי פריצה","רוט ועריכה של המערכת מבפנים","קושחה ייעודית, מוכנה לצריבה","הסרת האינטרנט, הדפדפנים והחנות","ושאר התאמות לפי הצורך"],link="/android/",svc="android")
s += card("music","הכשרת נגנים","הכשרה מלאה של נגני אנדרואיד מכל הדגמים, כך שיישארו כלי לשמיעה וללימוד בלבד.",["הסרת האינטרנט מהמערכת עצמה","הסרת דפדפנים, חנות ואפליקציות מיותרות","שלוש רמות: בסיס בלבד, חנות פנימית, או התקנה מבחוץ","בכל הרמות: בלי סרטים","טעינת שיעורים ותכנים לפי בקשה","אפשרות לנגן מוכן מהקו השמור שלנו"],link="/shop/",svc="players")
s += card("win","מחשבים: מסוננים או בלי אינטרנט","במחשב האינטרנט רק מסונן, או שאין אותו בכלל.",["חיבור לסינון ברמת הספק, בשיטת נטפרי","הסרת האינטרנט ברמת התוכנה: מערכת בלי רכיבי רשת","הסרת האינטרנט ברמת החומרה: ניתוק פיזי של כרטיס הרשת וה-WiFi","התקנת Windows ו-Office נקייה, דרייברים והגדרות"],link="/contact/?subject=אחר",svc="computers")
s += card("phone","אפליקציות אנדרואיד","אפליקציה שעושה בדיוק את מה שצריך, מוכנה מהר עם הכלים המתקדמים ביותר, במחיר שאי אפשר להתחרות בו.",["אפליקציות חדשות מאפס","שיפור והתאמה של אפליקציות קיימות","אפליקציות שעובדות בלי אינטרנט, למכשירים סגורים ולנגנים","אפליקציות לעסקים ולמוסדות"],link="/contact/?subject=פיתוח",svc="apps")
s += card("code","תוכנות למחשב","כלי שחוסך שעות עבודה, מהר ובזול.",["תוכנות וכלים בהתאמה אישית","אוטומציה לאקסל, לקבצים ולעבודה משרדית","ניהול נתונים, דוחות והדפסות","כלים לעסקים, למוסדות ולגמ\"חים"],link="/contact/?subject=פיתוח",svc="software")
s += card("globe","בניית אתרים","אתר תדמית או אתר עסקי, מעוצב ומהיר, במחיר רצפה.",["עיצוב אישי שמתאים לעסק ולציבור","מותאם לטלפון ולמחשב","טופס פנייה שמגיע ישר למייל","ממשק לעדכון תכנים, מחירים ומוצרים בעצמך","הקמה בגוגל, כתובת ואחסון"],link="/contact/?subject=אתר",svc="websites")
s += card("lang","תרגום אפליקציות","אפליקציה בעברית מלאה ומסודרת, גם כשאין לה גרסה רשמית בעברית.",["תרגום הממשק והתכנים","התאמה לכתיבה מימין לשמאל","גם לאפליקציות שלא נועדו לתרגום"],link="/contact/?subject=פיתוח",svc="translate")
s += card("pen","עיצוב: לוגו, פרסומות ותמונות","עיצוב מקצועי ונקי, בהתאמה לציבור ולמותג שלך.",["לוגו ומיתוג","מודעות ופרסומות","תמונות ובאנרים לאתר"],link="/contact/?subject=אחר",svc="design")
s += card("bolt","תוספים וסקריפטים","כלי קטן שחוסך עבודה, מוכן מהר ובזול במיוחד.",["תוספים לדפדפן","סקריפטים ואוטומציות","חיבור בין תוכנות ושירותים"],link="/contact/?subject=פיתוח",svc="scripts")
s += '''</div></div></section>
<section class="block alt"><div class="wrap">
<h2 class="title">מחירון</h2>
<p class="sub">המחירים מתעדכנים מעת לעת. כל עבודה מקבלת הצעה ברורה מראש.</p>
<div class="plist">''' + "".join('<div><span>%s</span><span class="price" data-svc="%s">במחיר רצפה</span></div>' % x for x in [
    ("עריכת מכשירי אנדרואיד", "android"), ("הכשרת נגנים", "players"), ("מחשבים: מסוננים או בלי אינטרנט", "computers"),
    ("אפליקציות אנדרואיד", "apps"), ("תוכנות למחשב", "software"), ("בניית אתרים", "websites"),
    ("תרגום אפליקציות", "translate"), ("עיצוב: לוגו, פרסומות ותמונות", "design"), ("תוספים וסקריפטים", "scripts")]) + '''</div>
</div></section>
'''
s += CTA_BAND
s += foot()
write("/services/", s)
# ---------- ANDROID ----------
a = head("עריכת מכשירי אנדרואיד והכשרת נגנים | כושר טק",
         "עריכה והכשרה של מכשירי אנדרואיד ונגנים בכל הרמות: חסימה וניהול (MDM), רוט, קושחה ייעודית והסרת אינטרנט, דפדפנים וחנות, בהתאמה לציבור שומר תורה ומצוות.", "/android/")
a += '''<section class="pagehead"><div class="wrap"><h1>עריכת מכשירי אנדרואיד</h1><p>זו ההתמחות שלנו: עבודות שטכנאי רגיל לא יודע לבצע, או שאצלו לא שוות את המחיר. מכשיר שעושה בדיוק מה שצריך, ושום דבר מעבר לכך.</p></div></section>
<section class="block"><div class="wrap">
<h2 class="title">שלוש רמות של עריכה</h2>
<p class="sub">הרמה נבחרת לפי המכשיר ולפי כמה עמוק צריך להגיע.</p>
<div class="grid c3">'''
a += card("shield","חסימה וניהול (MDM)","המכשיר עובר לניהול מלא, בלי פריצה ובלי לפגוע בתוכנה של היצרן.",["חסימת אפליקציות, הגדרות והתקנות","נעילה שקשה מאוד לעקוף","אפשר להוסיף ולהוריד בהמשך"],price="מתאים לרוב המכשירים")
a += card("bolt","רוט ועריכת המערכת","גישה לליבת המערכת: מסירים ומשנים כל מה שצריך, מבפנים.",["הסרת רכיבים מהמערכת עצמה","הסרת האינטרנט, הדפדפנים והחנות לגמרי","עריכה עמוקה של המערכת"],price="למכשירים נתמכים")
a += card("phone","קושחה ייעודית","בונים למכשיר מערכת משלו, נקייה וסגורה כבר מההתחלה.",["מערכת שנבנתה מחדש","קובץ מוכן לצריבה","מתאים להכשרת כמה מכשירים זהים"],price="לפי דגם")
a += '''</div></div></section>
<section class="block alt"><div class="wrap">
<h2 class="title">מה אפשר לעשות במכשיר</h2>
<p class="sub">מכשירי אנדרואיד ונגנים מוכשרים אצלנו בלי אינטרנט. מכאן, אפשר לבנות כמעט כל שילוב:</p>
<ul class="feat">
<li><strong>הסרת האינטרנט מהמכשיר</strong>: WiFi ונתונים מוסרים ברמת המערכת, לא רק חסומים</li>
<li><strong>הסרת דפדפנים, חנות אפליקציות ואפליקציות מובנות</strong> שאין בהן צורך</li>
<li><strong>השארת אפליקציות נבחרות בלבד</strong> שעובדות בלי אינטרנט: נגן, רדיו, הקלטה, שעון, מחשבון ועוד</li>
<li><strong>חסימת מצלמה, גלריה והעברת קבצים</strong>, או כל שילוב אחר</li>
<li><strong>נגנים ומכשירי שיעורים</strong> עם תכנים שנטענים מראש</li>
<li><strong>מכשירים לילדים ולבני נוער</strong> עם מה שמתאים להם בלבד</li>
<li><strong>הכשרת כמה מכשירים זהים</strong> לעסקים ולמוסדות, בהגדרה אחת</li>
<li><strong>אפליקציה ייעודית</strong> שנבנית במיוחד למכשיר שלך</li>
<li><strong>ושאר התאמות</strong>: אם יש צורך מסוים, כנראה שאפשר לעשות אותו</li>
</ul>
</div></section>
<section class="block"><div class="wrap">
<h2 class="title">גם במחשבים</h2>
<p class="sub">במחשב האינטרנט רק מסונן, או שאין אותו בכלל.</p>
<ul class="feat">
<li><strong>אינטרנט מסונן בלבד</strong>: חיבור לסינון ברמת הספק, בשיטת נטפרי</li>
<li><strong>הסרת האינטרנט ברמת התוכנה</strong>: מערכת בלי רכיבי הרשת</li>
<li><strong>הסרת האינטרנט ברמת החומרה</strong>: ניתוק פיזי של כרטיס הרשת וה-WiFi</li>
</ul>
</div></section>
'''
a += CTA_BAND
a += foot()
write("/android/", a)
# ---------- SHOP ----------
sh = head("חנות נגנים | כושר טק: נגני אנדרואיד מוכשרים",
          "הקו השמור: נגני אנדרואיד מוכשרים בלי אינטרנט ובלי סרטים, בשלוש רמות הכשרה. סדרת הזמיר: הזמיר (אנדרואיד 13, מסך 3.99 אינץ', Bluetooth ורדיו) והזמיר פלוס עם אחסון כפול ופנס. מגיעים מוכנים, בלי אינטרנט.", "/shop/")
sh += '''<section class="pagehead"><div class="wrap"><h1>הקו השמור</h1><p>נגני אנדרואיד שנבחרו בקפידה ומגיעים מוכשרים ומוכנים לשימוש. אנחנו לא מוכרים מה שאנחנו לא עומדים מאחוריו.</p></div></section>
<section class="block"><div class="wrap">
<div class="guard"><strong>בכל הנגנים שלנו:</strong> בלי אינטרנט ובלי שום אפשרות להכניס סרטים. זה לא תוסף, זה הבסיס.</div>
<div id="quiz" class="quiz"></div>
<h2 class="title">שלוש רמות הכשרה</h2>
<p class="sub">כל נגן בחנות אפשר להזמין בכל אחת מהרמות. בוחרים לפי הצורך, מהשמורה ביותר.</p>
<div class="grid c3 tiers">
<article class="card tier"><span class="tnum">1</span><h3>שמור</h3><p>אפליקציות בסיס בלבד, בלי שום התקנה.</p><ul><li>נגן, רדיו, הקלטה ושיעורים</li><li>שעון, מחשבון, לוח שנה וקבצים</li><li>אי אפשר להוסיף אפליקציות</li></ul><span class="tag">השמור ביותר</span></article>
<article class="card tier"><span class="tnum">2</span><h3>שמור עם חנות פנימית</h3><p>כל הבסיס, ובנוסף חנות פנימית נרחבת של אפליקציות שנבדקו ואושרו.</p><ul><li>מבחר רחב של אפליקציות מאושרות</li><li>מתקינים רק מתוך החנות הפנימית</li><li>בלי התקנה מבחוץ</li></ul></article>
<article class="card tier"><span class="tnum">3</span><h3>עם התקנה מבחוץ</h3><p>לשימוש מתקדם: אפשר להתקין אפליקציות גם מבחוץ.</p><ul><li>התקנת קבצי אפליקציה מבחוץ</li><li>עדיין בלי אינטרנט</li><li>עדיין בלי סרטים</li></ul></article>
</div>
<h2 class="title" style="margin-top:44px">הנגנים</h2>
<div class="grid c2" id="products"></div>
<div class="note" style="margin-top:24px">התשלום אינו מתבצע באתר. אחרי יצירת קשר נתאם הכול ישירות.</div></div></section>
'''
sh += foot()
write("/shop/", sh)

# ---------- FORUM (separate look, not part of the business site) ----------
FORUM = "מלאכת מחשבת"

def fhead(title, path):
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#14243f">
<link rel="icon" href="{V("assets/forum-icon.svg")}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700&family=Heebo:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{V("assets/forum.css")}">
<script src="{V("assets/ask.js")}" defer></script>
</head>
<body class="forum">
<header class="fbar"><div class="fwrap">
  <a class="fbrand" href="/market/"><img src="{V("assets/forum-icon.svg")}" alt="" width="32" height="32">{FORUM}</a>
  <nav><a href="/market/"{' aria-current="page"' if path == "/market/" else ""}>הלוח</a><a href="/market/#/pros">אנשי מקצוע</a><a href="/market/rules/"{' aria-current="page"' if path == "/market/rules/" else ""}>כללי הלוח</a></nav>
  <div id="fuser" class="fuser"></div>
</div></header>
<main class="fmain"><div class="fwrap">
'''

def ffoot():
    return '''</div></main>
<footer class="ffoot"><div class="fwrap">
  <div><span class="fname">'''+FORUM+'''</span> · <span>כל בקשה ואיש מקצוע מאושרים ידנית</span></div>
  <a href="/market/#/contact">צור קשר עם ההנהלה</a>
</div></footer>
</body></html>
'''

# ---------- REQUEST ----------
r = head("בקשות ועבודות | כושר טק", "לוח בקשות ועבודות: מפרסמים מה צריך, ואנשי מקצוע וחברות לוקחים את העבודה.", "/request/")
r += f'''<section class="pagehead"><div class="wrap"><h1>בקשות ועבודות</h1><p>צריך עזרה במשהו? מפרסמים בקשה, ואנשי מקצוע וחברות מהתחום לוקחים אותה. בלי מתווכים ובלי הפתעות.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c3">
<article class="card"><div class="ico">{ICONS["chat"]}</div><h3>מפרסמים בקשה</h3><p>כותבים מה צריך: תוכנה, אתר, עיצוב, כתיבה, התאמת מכשיר, עזרה טכנית או כל עבודה אחרת, ואפשר להוסיף תקציב וזמן רצוי.</p></article>
<article class="card"><div class="ico">{ICONS["shield"]}</div><h3>אנשי מקצוע נבחרים</h3><p>הגישה לבקשות פתוחה רק לאנשי מקצוע וחברות שאושרו, כדי לשמור על רמה ועל אמינות.</p></article>
<article class="card"><div class="ico">{ICONS["bolt"]}</div><h3>לוקחים ומבצעים</h3><p>איש מקצוע בוחר בקשה שמתאימה לו, מציע מחיר וזמן, ומתאם ישירות עם מי שביקש. פרטי הקשר נחשפים רק לאחר שהעבודה נלקחה.</p></article>
</div>
<div class="note" style="margin-top:24px"><strong>שלב ראשון.</strong> ההצטרפות, הבקשות וההצעות באישור ידני של הנהלת האתר. בהמשך תיגבה עמלה על עבודות, והכול מפורט בכללי האתר.</div>
<p style="margin-top:20px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn primary" href="/market/">כניסה ללוח</a><a class="btn ghost" style="color:var(--green)" href="/contact/?subject=פיתוח">שליחת בקשה בטופס</a><a class="btn ghost" style="color:var(--green)" href="/contact/?subject=אחר">הצטרפות כאיש מקצוע</a><a class="link" href="/rules/">כללי האתר</a></p></div></section>
'''
r += foot()
write("/request/", r)

# ---------- MARKET ----------
mk = fhead(FORUM, "/market/")
mk += '''<noscript>הלוח דורש JavaScript.</noscript><div id="mk">טוען...</div>
<script src="%s" defer></script>
''' % V("assets/market.js")
mk += ffoot()
write("/market/", mk)

# ---------- BOARD ADMIN (separate from the business admin) ----------
ma = fhead("ניהול | " + FORUM, "/market/admin/")
ma += '''<div id="login" class="box" hidden style="max-width:360px;margin:8vh auto"><h1 style="margin:0 0 10px;font-size:1.3rem">ניהול הלוח</h1>
<label class="f">סיסמה<input type="password" id="pw" autocomplete="current-password"></label>
<button class="btn primary" id="go" type="button" style="margin-top:10px;width:100%">כניסה</button><div id="loginmsg" role="status" class="meta" style="margin-top:8px"></div></div>
<div id="app" hidden>
<div class="ptitle"><h1>ניהול הלוח</h1><button class="btn sm" id="out" type="button">יציאה</button></div>
<section id="boardbox" class="box" hidden></section>
<nav class="tabs" role="tablist">
<button data-tab="users" class="on">משתמשים <span id="ucount"></span></button><button data-tab="mreq">בקשות <span id="rcount"></span></button>
<button data-tab="partners">שותפים <span id="pcount"></span></button><button data-tab="est">הגדרות</button><button data-tab="contact">פניות <span id="kcount"></span></button></nav>
<section class="panel on" id="p-users"><div id="ulist"></div></section>
<section class="panel" id="p-mreq"><div id="rlist"></div></section>
<section class="panel" id="p-partners"><div id="clist"></div></section>
<section class="panel" id="p-contact"><div id="klist"></div></section>
<section class="panel" id="p-est"><div id="elist"></div><div class="act"><button class="btn primary" id="saveest" type="button">שמירה</button></div></section>
</div><div id="status" role="status" aria-live="polite"></div>
<script src="@@JS@@"></script>
<script src="@@INBOX@@"></script>
'''.replace("@@JS@@", V("assets/market-admin.js")).replace("@@INBOX@@", V("assets/market-inbox.js"))
ma += ffoot()
write("/market/admin/", ma)

# ---------- HUB: one private page with a button to every group (not linked from anywhere) ----------
HUB = [
 ("האתר הפרטי (כושר טק)", [("האתר", "/"), ("ניהול האתר", "/admin/")]),
 ("הצ'אט של הוועד", [("הצ'אט", "/chat/"), ("כניסת מנהל-על", "/chat/#/dev")]),
 ("הפורום", [("הפורום", "/market/"), ("ניהול הפורום", "/market/admin/")]),
 ("השרת", [("שולחן עבודה", "/desktop/"), ("ניהול השרת", "/panel/")]),
]
hb = '''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>כל המקומות</title>
<style>body{margin:0;font-family:system-ui,"Segoe UI",Arial,sans-serif;background:#f3f4f6;color:#1f2937;line-height:1.6}
main{max-width:760px;margin:0 auto;padding:28px 16px}h1{margin:0 0 18px;font-size:1.5rem}
section{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 18px;margin-bottom:14px}
h2{margin:0 0 10px;font-size:1.05rem;color:#4b5563}.b{display:flex;gap:10px;flex-wrap:wrap}
a{display:inline-block;padding:10px 20px;border-radius:8px;background:#1f2937;color:#fff;text-decoration:none;font-weight:600}
a:hover{background:#374151}</style></head><body><main><h1>כל המקומות</h1>'''
for _t, _ls in HUB:
    hb += "<section><h2>%s</h2><div class='b'>%s</div></section>" % (html.escape(_t), "".join('<a href="%s">%s</a>' % (_h, html.escape(_n)) for _n, _h in _ls))
hb += "</main></body></html>"
write("/hub/", hb)

# ---------- RULES ----------
RULES = [
 ("1. כללי", [
  "הלוח מיועד לציבור שומר תורה ומצוות, ופועל לפי כללים אלה. השימוש בלוח מהווה הסכמה להם.",
  "הלוח מתווך בין מי שזקוק לשירות לבין אנשי מקצוע וחברות. הצטרפות של אנשי מקצוע וכל בקשה שמתפרסמת כפופות לאישור ידני של מנהל הלוח.",
  "מנהל הלוח רשאי לסרב לבקשה, להסיר תוכן, להשעות או לחסום משתמש, בכל עת, גם בלי לפרט נימוקים.",
  "הלוח אינו פעיל בשבתות ובמועדים. פניות שיתקבלו בימים אלה יטופלו לאחריהם.",
 ]),
 ("2. הרשמה ואישור", [
  "מבקשי עבודה נכנסים מיד עם ההרשמה. כל בקשה שהם מפרסמים מתפרסמת רק לאחר אישור ידני.",
  "יש למסור פרטים נכונים ומלאים. החשבון אישי ואין להעבירו לאחר.",
  "אנשי מקצוע וחברות יאושרו רק לאחר בדיקה של תחום העיסוק והתאמתו לכללי הלוח. הגישה לבקשות הפתוחות ולהצעות מחיר מוגבלת לבעלי אישור.",
  "האחריות על שמירת הסיסמה היא על המשתמש.",
 ]),
 ("3. תחומי עבודה מותרים", [
  "פיתוח תוכנה וכלים, בניית אתרים והתאמתם.",
  "התאמת מכשירים ומחשבים והתקנות תוכנה.",
  "כתיבה, עריכה, הגהה, הקלדה ותרגום של תכנים מתאימים.",
  "עיצוב גרפי ומיתוג בסגנון הולם.",
  "הדרכה, ייעוץ טכנולוגי ושירותי משרד ועסק.",
  "תחום שאינו ברשימה: אפשר לבקש, והחלטת האישור נתונה למנהל הלוח.",
 ]),
 ("4. תוכן ועבודות שאסור לפרסם או לבצע", [
  "תוכן שאינו צנוע או שאינו הולם את הציבור שאליו הלוח מיועד, בטקסט ובתמונה. לא יועלו תמונות של נשים או בנות, או של חלקי גוף.",
  "פריצה, האזנה, מעקב אחר אדם, גניבת מידע או התחזות.",
  "עקיפה או הסרה של סינון וחסימה שהמשתמש או הקהילה בחרו, וכן יצירת גישה לתכנים בלתי מסוננים.",
  "משחקי הימורים והגרלות, ועבודות שמטרתן ריבית אסורה או הונאה.",
  "תוכן העוסק בדתות אחרות, בעבודה זרה או בחילול ערכי היהדות.",
  "תוכן מפלג, לשון הרע, הוצאת שם רע, השמצה, קללות וביטויים גסים. הדיבור בלוח הוא בלשון נקייה ומכובדת.",
  "פרסום עסקי של צד שלישי, קישורים חיצוניים לא מאושרים והפניה לאתרים שאינם מתאימים.",
 ]),
 ("5. בקשות והצעות מחיר", [
  "בקשה תכלול תיאור ברור של הצורך. מנהל הלוח רשאי לערוך, לדחות או להסיר בקשה.",
  "הלוח מציג הערכת מחיר אוטומטית. זו הערכה בלבד, ואינה התחייבות. המחיר הסופי נקבע בין הצדדים.",
  "רק אנשי מקצוע וחברות מאושרים רשאים להציע מחיר או לקחת עבודה.",
  "כל עבודה שנלקחה מסומנת בלוח, ופרטי הקשר של מי שביקש נחשפים רק למי שלקח אותה.",
  "מומלץ לסכם בכתב את היקף העבודה, המחיר ולוח הזמנים לפני תחילת הביצוע.",
 ]),
 ("6. עמלות", [
  "בשלב הנוכחי השימוש בלוח ללא עמלה.",
  "בעתיד תיגבה עמלה על עבודות שנסגרו דרך הלוח. כל מי שמצטרף ומשתמש בלוח מצהיר שהוא מבין זאת ומסכים לכך.",
  "שיעור העמלה ואופן גבייתה יפורסמו מראש ובכתב, ולא יחולו על עבודה שנלקחה לפני הפרסום.",
  "אין לעקוף את הלוח כדי להימנע מעמלה בעבודה שהוכרה דרכו.",
  "אנשי מקצוע שהוכרו כחברים מייסדים פטורים מעמלה לתקופה של שנה מיום ההכרה בהם, והתקופה אינה כוללת שינוי מעמד.",
 ]),
 ("7. פרטיות ושמירת מידע", [
  "פרטי קשר נחשפים רק במקרים הנדרשים לביצוע העבודה, כאמור בסעיף 5.",
  "אין למסור לאחרים פרטים שהתקבלו דרך הלוח, ואין להשתמש בהם לשום מטרה אחרת.",
  "מנהל הלוח רשאי לעיין בפניות, בבקשות ובהודעות בלוח לצורך בירור תלונות, אכיפת הכללים ושמירה על הציבור.",
 ]),
 ("8. מעמד הלוח ואחריות", [
  "הלוח משמש מתווך בלבד, ואינו צד לעסקה, להתקשרות או לעבודה שבין המזמין לבין המפתח.",
  "העבודה, תנאיה, איכותה, לוח הזמנים, התשלום עליה ותוכנה הם באחריות המזמין והמפתח בלבד.",
  "ללוח ולמנהליו אין כל אחריות לעבודה, לביצועה או לתוצאותיה, ולא לכל נזק או הפסד שייגרמו בעקבותיה.",
  "כל אחד מהצדדים אחראי לעצמו לכל הנובע מן העבודה שהוא מזמין או מבצע.",
 ]),
 ("9. תוכנית שותפים", [
  "לכל חבר בלוח יש קישור אישי. על כל מי שנרשם דרכו נצבר לו תגמול בקרדיטים, ואם מי שנרשם גם מזמין עבודה, נצבר בונוס נוסף.",
  "מנהל הלוח קובע את גובה התגמולים ואת השימוש בהם, ורשאי לבטל תגמול או לשנות את התוכנית כולה, בכל עת.",
  "אין תגמול על הזמנה עצמית, על חשבונות כפולים או על הזמנה שנעשתה בספאם או בהטעיה.",
 ]),
 ("10. אכיפה ופניות", [
  "הפרת הכללים עלולה לגרור הסרת תוכן, אזהרה, השעיה או חסימה.",
  "אפשר להגיש תלונה או ערעור דרך דף צור קשר, והחלטת מנהל הלוח היא הסופית.",
 ]),
 ("11. שינויים", [
  "מנהל הלוח רשאי לעדכן את הכללים. הנוסח העדכני מפורסם בדף זה, והמשך שימוש בלוח מהווה הסכמה לו.",
 ]),
]
ru = fhead("כללי הלוח | " + FORUM, "/market/rules/")
ru += '<div class="ptitle"><h1>כללי הלוח</h1></div><p class="sub">הכללים נועדו לשמור על לוח נקי, אמין ומתאים לציבור. נא לקרוא לפני ההצטרפות.</p><div class="fstack">'
for t, items in RULES:
    ru += '<article class="card"><h3>%s</h3><ul>%s</ul></article>' % (html.escape(t), "".join("<li>%s</li>" % html.escape(x) for x in items))
ru += '</div><script src="%s" defer></script>' % V("assets/forum-nav.js")
ru += ffoot()
write("/market/rules/", ru)
# the same rules as data, shown inside the sign-up forms
import json
with open(os.path.join(OUT, "market", "rules.json"), "w", encoding="utf-8") as _f:
    json.dump([{"title": t, "items": it} for t, it in RULES], _f, ensure_ascii=False)

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
    <option>בניית אתר</option><option>חנות / מוצרים</option><option value="פיתוח">בקשה / עבודה</option><option>אחר</option></select></label>
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
  try{{var pr=new URLSearchParams(location.search).get('product');if(pr){{pr=pr.slice(0,60);var o=document.createElement('option');o.value='הזמנה: '+pr;o.textContent='הזמנה: '+pr;f.subject.insertBefore(o,f.subject.firstChild);f.subject.selectedIndex=0;if(!f.message.value)f.message.value='אני מעוניין ב'+pr+'. ';}}}}catch(e){{}}
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
# the admin page is hand-written: refresh its asset versions too
_ap = os.path.join(OUT, "admin", "index.html")
if os.path.exists(_ap):
    with open(_ap, encoding="utf-8") as _f:
        _h = _f.read()
    for _name in ("assets/style.css", "assets/ask.js"):
        _h = re.sub(r'(["\'])/%s(\?v=[0-9a-f]+)?\1' % re.escape(_name), lambda m: m.group(1) + V(_name) + m.group(1), _h)
    with open(_ap, "w", encoding="utf-8") as _f:
        _f.write(_h)
print("pages generated")
