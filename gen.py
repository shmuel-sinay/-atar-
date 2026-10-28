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

NAV = [("/", "בית"), ("/services/", "שירותים"), ("/players/", "הכשרת נגנים"), ("/shop/", "חנות"),
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
<meta property="og:type" content="website"><meta property="og:locale" content="he_IL"><meta property="og:site_name" content="כשר טק">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="https://kosher-tek.com{path}"><meta property="og:image" content="https://kosher-tek.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/logo-512.png" sizes="512x512" type="image/png">
<link rel="apple-touch-icon" href="/assets/logo-180.png">
<link rel="stylesheet" href="{V("assets/style.css")}">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="/"><img src="/assets/logo.svg" alt="" width="40" height="40"><span>כשר טק<small>טכנולוגיה מותאמת לציבור</small></span></a>
  <nav class="main" aria-label="ראשי">{nav}</nav>
</div></header>
<main>
'''

def foot():
    return f'''</main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><h4>כשר טק</h4><p>כל ההתאמות שחלמתם עליהן, למכשירים, נגנים ומחשבים: גם מה שיקר מדי אצל אחרים וגם מה שאף אחד לא עושה. והכול במחירי רצפה.</p></div>
    <div><h4>ניווט</h4><ul>{"".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in NAV)}</ul></div>
    <div><h4>יצירת קשר</h4><ul><li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/contact/">טופס פנייה</a></li></ul></div>
  </div>
  <div class="legal">© כשר טק</div>
</div></footer>
<script src="{V("assets/site.js")}" defer></script>
</body></html>
'''

SITE = "https://kosher-tek.com"
ORG_JSONLD = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","name":"כשר טק",
"url":"%s/","logo":"%s/assets/logo-512.png","image":"%s/assets/og.png","telephone":"+972-55-440-7560","email":"%s",
"description":"כל ההתאמות שחלמתם עליהן למכשירים, נגנים ומחשבים, לציבור שומר תורה ומצוות: גם מה שיקר מדי אצל אחרים וגם מה שאף אחד לא עושה. הכול במחירי רצפה.",
"areaServed":"IL","priceRange":"₪","knowsAbout":["פיתוח אפליקציות אנדרואיד","תוכנות למחשב","MDM","רוט","קושחה","סינון מכשירים","עיצוב גרפי"]}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"כשר טק","alternateName":"Kosher Tek","url":"%s/"}</script>
""" % (SITE, SITE, SITE, EMAIL, SITE)

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
    <h2>יש לך נגן, מחשב או רעיון? נשמח לשמוע.</h2>
    <p>מספרים מה צריך, ומקבלים הצעה ברורה ומחיר רצפה מראש, בלי התחייבות.</p>
  </div>
  <div class="ctaacts">
    <a class="btn primary" href="/contact/">השארת פרטים</a>
    <a class="ctaline" href="tel:{PHONE_TEL}"><span>טלפון</span>{PHONE_DISPLAY}</a>
    <a class="ctaline" href="mailto:{EMAIL}"><span>מייל</span>{EMAIL}</a>
  </div>
</div></section>
'''

home = head("כשר טק | כל ההתאמות שחלמתם עליהן, במחירי רצפה",
            "התאמה והכשרה של מכשירים, נגנים ומחשבים לציבור שומר תורה ומצוות: כל התאמה שחלמתם עליה, במחירי רצפה: גם כזו שאצל אחרים יקרה מדי וגם כזו שאף אחד לא עושה. ובנוסף תוכנות, אפליקציות ואתרים. " + PHONE_DISPLAY, "/")
home += f'''
<section class="hero"><div class="wrap">
  <div>
    <span class="badge">נגנים · מחשבים · תוכנות · תוספים · עיצוב</span>
    <h1>כל ההתאמות <em>שחלמתם</em> עליהן.<br>במחירי רצפה.</h1>
    <p class="pricebadge">מחירים שאי אפשר להתחרות בהם · גם מה שאף אחד לא עושה</p>
    <p class="lead">נגני אנדרואיד ומחשבים בדיוק כמו שרציתם: גם התאמות שאצל אחרים יקרות מדי, וגם כאלה שאף אחד לא עושה. בהתאמה מלאה לציבור שומר התורה והמצוות. ובנוסף תוכנות, אפליקציות, אתרים ועיצוב גרפי מקצועי, מהר ובזול.</p>
    <div class="cta"><a class="btn primary" href="/contact/">ספרו לנו מה אתם צריכים</a><a class="btn ghost" href="/services/">מה אפשר לעשות</a></div>
  </div>
  <img class="mark" src="/assets/logo.svg" alt="" width="300" height="300">
</div></section>

<section class="block"><div class="wrap">
  <h2 class="title">מה אנחנו עושים</h2>
  <p class="sub">התאמות שאף אחד לא עושה או שאצל אחרים יקרות מדי, ותוכנות, אפליקציות ואתרים. והכול במחירי רצפה.</p>
  <div class="grid c3">
    {card("music","הכשרת נגני אנדרואיד","ההתמחות המרכזית: נגנים בלי אינטרנט ובלי סרטים, בדיוק עם מה שבחרת. מה שאף אחד לא עושה, במחיר רצפה.",["חסימה וניהול (MDM), רוט וקושחה ייעודית","שלוש גרסאות, ועזרה בבחירה","שיעורים, ספרי קודש וכלים שימושיים"],link="/players/",svc="players")}
    {card("bolt","תוספים","תוכנה קטנה שנכנסת לדפדפן או לתוכנה שכבר יש לכם, ועושה בשנייה מה שלוקח לכם שעה.",["לחיצה אחת במקום עשר","מילוי טפסים והעברת נתונים לבד","כפתורים חדשים באתרים שאתם עובדים בהם"],link="/plugins/",svc="scripts")}
    {card("win","מחשבים: התאמות והסרת אינטרנט","התאמת מחשבים לבית, לעסק ולמוסד, כולל מחשב בלי אינטרנט בכלל.",["הסרת האינטרנט ברמת התוכנה וברמת החומרה","השגה והתקנה של תוכנות מחשב","התקנת Windows ו-Office נקייה"],link="/computers/",svc="computers")}
    {card("phone","אפליקציות אנדרואיד","אפליקציה ייעודית לעסק, למוסד או למכשיר סגור. מוכנה מהר, במחיר שאי אפשר להתחרות בו.",["אפליקציות חדשות מאפס","שיפור והתאמה של אפליקציות קיימות","אפליקציות שעובדות בלי אינטרנט"],link="/apps/",svc="apps")}
    {card("code","תוכנות למחשב","כלי שעושה בדיוק את מה שצריך. מהר וזול, בלי לשלם סכומי עתק למתכנת.",["תוכנות וכלים בהתאמה אישית","אוטומציה לאקסל, לקבצים ולעבודה משרדית","כלים לעסקים, למוסדות ולגמ\"חים"],link="/software/",svc="software")}
    {card("globe","בניית אתרים","אתר תדמית או אתר עסקי: מעוצב, מהיר ומוכן לחיפוש בגוגל, במחיר רצפה.",["מותאם לטלפון ולמחשב","טופס פנייה שמגיע ישר למייל","ממשק לעדכון תכנים בעצמך"],link="/websites/",svc="websites")}
    {card("pen","עיצוב גרפי","מעצבת גרפית מקצועית בצוות: עיצוב שנראה יוקרתי, מדויק ומתאים לציבור, במחיר רצפה.",["לוגו ומיתוג לעסק","מודעות, פרסומות ופליירים","הזמנות, כרטיסי ביקור ותמונות לאתר"],link="/design/",svc="design")}
  </div>
  <p class="more-svc">ועוד: <a href="/translate/">תרגום אפליקציות</a> · <a href="/pc-software/">השגה והתקנה של תוכנות מחשב</a> · <a href="/services/">לכל השירותים והמחירון ←</a></p>
</div></section>

<section class="block plugins" id="plugins"><div class="wrap">
  <h2 class="title">מה כוחו של תוסף?</h2>
  <p class="sub">תוסף הוא תוכנה קטנה שנכנסת לדפדפן או לתוכנה שאתם כבר משתמשים בה, ומוסיפה לה בדיוק את מה שחסר. הוא קטן, אבל הוא יכול לחסוך שעות עבודה בכל יום.</p>
  <div class="grid c3 pwr">
    <article><strong>לחיצה אחת במקום עשר</strong><p>פעולה שחוזרת על עצמה כל יום הופכת לכפתור אחד.</p></article>
    <article><strong>טפסים שממלאים את עצמם</strong><p>שם, כתובת, מספרים ופרטים קבועים נכנסים לבד, בלי טעויות.</p></article>
    <article><strong>נתונים שעוברים לבד</strong><p>מאתר לאקסל, מאקסל למסמך, בלי להעתיק ולהדביק שורה אחרי שורה.</p></article>
    <article><strong>כפתור שחסר לכם באתר</strong><p>האתר או המערכת שאתם עובדים בהם מקבלים בדיוק את הכפתור שתמיד רציתם.</p></article>
    <article><strong>בדיקות ותזכורות</strong><p>התוסף שם לב לבד כשמשהו משתנה, ומזכיר לכם.</p></article>
    <article><strong>מסך נקי</strong><p>מסתירים באתרים את מה שמסיח ולא שייך, ונשאר רק מה שצריך לעבודה.</p></article>
  </div>
  <p class="pwr-end"><strong>שעה של עבודה כל יום יכולה להפוך לשנייה.</strong> ותוסף כזה נבנה מהר, במחיר רצפה. <a href="/contact/?subject=פיתוח">ספרו לנו מה מעייף אתכם בעבודה ←</a></p>
</div></section>

<section class="block alt"><div class="wrap">
  <h2 class="title">נגן אנדרואיד: יותר מנגן, פחות מסמארטפון</h2>
  <p class="sub">כמו פלאפון כשר, רק בלי שיחות ועם מסך מגע: שיעורים, שירים, ספרי קודש, מפות וכלים שימושיים. הכול בלי אינטרנט ובלי סרטים, ורק מה שבחרת.</p>
  <a class="btn primary" href="/shop/">לנגנים ולעזרה בבחירה</a>
</div></section>

<section class="block"><div class="wrap">
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
s = head("שירותים ומחירון | כשר טק",
         "כל השירותים של כשר טק ומחירון: הכשרת נגני אנדרואיד, מחשבים בלי אינטרנט, השגה והתקנה של תוכנות, אפליקציות ותוכנות, אתרים, תרגום אפליקציות, עיצוב ותוספים.", "/services/")
s += '''<section class="pagehead"><div class="wrap"><h1>השירותים שלנו</h1><p>כל ההתאמות שחלמתם עליהן, במחירי רצפה שאי אפשר להתחרות בהם: גם מה שיקר מדי אצל אחרים וגם מה שאף אחד לא עושה.</p></div></section>
<section class="block"><div class="wrap"><div class="grid c2">'''
s += card("music","הכשרת נגני אנדרואיד","ההתמחות המרכזית: עבודות שאף אחד לא עושה, או שאצל אחרים יקרות מדי. נגנים בלבד, בסמארטפונים אנחנו לא נוגעים.",["חסימה וניהול (MDM), רוט וקושחה ייעודית","הסרת האינטרנט מתוך המערכת","שלוש גרסאות, ובכולן בלי סרטים","שיעורים, ספרי קודש וכלים שימושיים","ושאר התאמות לפי הצורך"],link="/players/",svc="players")
s += card("win","מחשבים: התאמות והסרת אינטרנט","התאמת מחשבים לבית, לעסק ולמוסד, כולל מחשב בלי אינטרנט בכלל.",["הסרת האינטרנט ברמת התוכנה: מערכת בלי רכיבי רשת","הסרת האינטרנט ברמת החומרה: ניתוק פיזי של כרטיס הרשת וה-WiFi","התקנת Windows ו-Office נקייה, דרייברים והגדרות"],link="/computers/",svc="computers")
s += card("box","השגה והתקנה של תוכנות מחשב","צריך תוכנה מסוימת ולא יודע מאיפה להביא או איך להתקין? אנחנו נשיג, נתקין ונגדיר.",["איתור התוכנה המתאימה לצורך","התקנה והגדרה מלאה","התאמה למחשב בלי אינטרנט"],link="/pc-software/",svc="pcsoft")
s += card("phone","אפליקציות אנדרואיד","אפליקציה שעושה בדיוק את מה שצריך, מוכנה מהר עם הכלים המתקדמים ביותר, במחיר שאי אפשר להתחרות בו.",["אפליקציות חדשות מאפס","שיפור והתאמה של אפליקציות קיימות","אפליקציות שעובדות בלי אינטרנט, למכשירים סגורים ולנגנים","אפליקציות לעסקים ולמוסדות"],link="/apps/",svc="apps")
s += card("code","תוכנות למחשב","כלי שחוסך שעות עבודה, מהר ובזול.",["תוכנות וכלים בהתאמה אישית","אוטומציה לאקסל, לקבצים ולעבודה משרדית","ניהול נתונים, דוחות והדפסות","כלים לעסקים, למוסדות ולגמ\"חים"],link="/software/",svc="software")
s += card("globe","בניית אתרים","אתר תדמית או אתר עסקי, מעוצב ומהיר, במחיר רצפה.",["עיצוב אישי שמתאים לעסק ולציבור","מותאם לטלפון ולמחשב","טופס פנייה שמגיע ישר למייל","ממשק לעדכון תכנים, מחירים ומוצרים בעצמך","הקמה בגוגל, כתובת ואחסון"],link="/websites/",svc="websites")
s += card("lang","תרגום אפליקציות","אפליקציה בעברית מלאה ומסודרת, גם כשאין לה גרסה רשמית בעברית.",["תרגום הממשק והתכנים","התאמה לכתיבה מימין לשמאל","גם לאפליקציות שלא נועדו לתרגום"],link="/translate/",svc="translate")
s += card("pen","עיצוב גרפי","מעצבת גרפית מקצועית בצוות. עיצוב נקי, יוקרתי ומדויק, בהתאמה מלאה לציבור ולמותג שלך, במחיר רצפה.",["לוגו ומיתוג מלא לעסק","מודעות, פרסומות ופליירים","הזמנות לשמחות וכרטיסי ביקור","באנרים ותמונות לאתר ולרשתות","עיצוב אריזות ושלטים"],link="/design/",svc="design")
s += card("bolt","תוספים וסקריפטים","תוכנה קטנה שנכנסת לדפדפן או לתוכנה שכבר יש לכם, ועושה בשנייה מה שלוקח שעה.",["לחיצה אחת במקום עשר פעולות","טפסים שממלאים את עצמם","נתונים שעוברים לבד מאתר לאקסל","כפתורים חדשים באתרים ובמערכות"],link="/plugins/",svc="scripts")
s += '''</div></div></section>
<section class="block alt"><div class="wrap">
<h2 class="title">מחירון</h2>
<p class="sub">המחירים מתעדכנים מעת לעת. כל עבודה מקבלת הצעה ברורה מראש.</p>
<div class="plist">''' + "".join('<div><span>%s</span><span class="price" data-svc="%s">במחיר רצפה</span></div>' % x for x in [
    ("הכשרת נגני אנדרואיד", "players"), ("מחשבים: התאמות והסרת אינטרנט", "computers"), ("השגה והתקנה של תוכנות מחשב", "pcsoft"),
    ("אפליקציות אנדרואיד", "apps"), ("תוכנות למחשב", "software"), ("בניית אתרים", "websites"),
    ("תרגום אפליקציות", "translate"), ("עיצוב גרפי", "design"), ("תוספים וסקריפטים", "scripts")]) + '''</div>
</div></section>
'''
s += CTA_BAND
s += foot()
write("/services/", s)
# ---------- LANDING PAGES: one focused page per service ----------
from html import escape as _e
LANDINGS = [
 dict(path="/design/", svc="design", subj="עיצוב", icon="pen",
  title="עיצוב גרפי מקצועי במחיר רצפה | לוגו, מודעות והזמנות | כשר טק",
  desc="מעצבת גרפית מקצועית: לוגו ומיתוג לעסק, מודעות, פליירים, הזמנות לשמחות, כרטיסי ביקור, באנרים ושלטים. עיצוב יוקרתי ומתאים לציבור, במחירי רצפה.",
  h1="עיצוב גרפי <em>שנראה יוקרתי</em>.<br>במחיר רצפה.",
  lead="מעצבת גרפית מקצועית בצוות. עיצוב נקי, מדויק ומכובד, שמתאים לציבור שומר התורה והמצוות ולאופי של העסק או של השמחה שלך.",
  what=[("לוגו ומיתוג","לוגו שזוכרים, צבעים וגופנים קבועים, וכל מה שהעסק צריך כדי להיראות אחיד ומקצועי."),
        ("מודעות ופליירים","מודעה לעיתון, לבית הכנסת או ללוח המודעות: ברורה, בולטת ומושכת את העין."),
        ("הזמנות לשמחות","הזמנות לחתונה, לבר מצווה ולברית, בעיצוב מיוחד ומכובד."),
        ("כרטיסי ביקור","כרטיס שנותן רושם ראשוני טוב, מוכן להדפסה."),
        ("באנרים ותמונות לאתר","תמונות ראשיות, באנרים ותמונות לשיתוף, בגדלים הנכונים."),
        ("אריזות ושלטים","מדבקות, אריזות, שלטים ורול-אפים שמוכנים לבית הדפוס.")],
  who=["בעל עסק שרוצה להיראות מקצועי","מוסד, ישיבה או גמ\"ח","משפחה לקראת שמחה","מי שצריך מודעה דחופה"],
  steps=[("מספרים מה צריך","מה מעצבים, למי, ואיזה סגנון אוהבים. אפשר לצרף דוגמאות."),("מקבלים סקיצה","עיצוב ראשון, ותיקונים עד שזה בדיוק מה שרצית."),("קבצים מוכנים","קבצים סופיים לדפוס ולמסך, באיכות מלאה.")],
  faq=[("כמה סבבי תיקונים יש?","מתקנים עד שהעיצוב מתאים לך. את הפרטים מסכמים מראש בהצעה."),
       ("מקבלים את הקבצים המקוריים?","כן. מקבלים קבצים מוכנים לדפוס ולשימוש באתר וברשתות."),
       ("העיצוב מתאים לציבור?","כן. כל עיצוב נעשה בהתאמה מלאה לציבור שומר התורה והמצוות."),
       ("אפשר עבודה דחופה?","ברוב המקרים כן. ספרו לנו מתי צריך, ונאמר מיד אם זה אפשרי.")]),
 dict(path="/computers/", svc="computers", subj="אחר", icon="win",
  title="מחשב בלי אינטרנט והתאמת מחשבים | כשר טק",
  desc="הסרת האינטרנט מהמחשב ברמת התוכנה וברמת החומרה, התאמת מחשבים לבית, לעסק ולמוסד, והתקנת Windows ו-Office נקייה. במחירי רצפה.",
  h1="מחשב <em>בלי אינטרנט</em>,<br>בדיוק כמו שצריך.",
  lead="התאמת מחשבים לבית, לעסק ולמוסד: מחשב שעובד מצוין לכל מה שצריך, בלי אינטרנט בכלל. בתוכנה, בחומרה, או בשתיהן.",
  what=[("הסרה ברמת התוכנה","מערכת שאין בה רכיבי רשת. אין דרך פשוטה להחזיר אותם."),
        ("הסרה ברמת החומרה","ניתוק פיזי של כרטיס הרשת וה-WiFi. הכי חזק שיש."),
        ("התקנה נקייה","Windows ו-Office מותקנים מחדש, בלי תוכנות מיותרות."),
        ("דרייברים והגדרות","מדפסת, סורק וכל מה שצריך, מוגדר ועובד בלי אינטרנט."),
        ("תוכנות שצריך","משיגים ומתקינים את התוכנות שאתם עובדים איתן."),
        ("מחשבים למוסדות","כמה מחשבים זהים, באותה הגדרה בדיוק.")],
  who=["בית שרוצה מחשב לעבודה וללימוד בלבד","משרד ועסק","ישיבות ותלמודי תורה","מי שקנה מחשב חדש"],
  steps=[("מספרים על המחשב","איזה מחשב, ומה הוא צריך לעשות."),("בוחרים רמה","תוכנה, חומרה או שתיהן. נמליץ על מה שמתאים."),("מקבלים מחשב מוכן","נקי, עובד ובלי אינטרנט.")],
  faq=[("אפשר בכל זאת להדפיס ולסרוק?","כן. מדפסות וסורקים מוגדרים לעבודה בלי אינטרנט."),
       ("מה ההבדל בין תוכנה לחומרה?","בתוכנה מסירים את רכיבי הרשת מהמערכת. בחומרה מנתקים את הרכיב עצמו, וזו הרמה החזקה ביותר."),
       ("איך מעדכנים תוכנות בלי אינטרנט?","דרך דיסק און קי, או שמביאים אלינו לעדכון.")]),
 dict(path="/pc-software/", svc="pcsoft", subj="אחר", icon="box",
  title="השגה והתקנה של תוכנות מחשב | כשר טק",
  desc="צריך תוכנה מסוימת ולא יודע מאיפה להביא או איך להתקין? איתור, התקנה והגדרה מלאה, גם למחשב בלי אינטרנט. במחירי רצפה.",
  h1="צריך תוכנה?<br><em>נשיג ונתקין.</em>",
  lead="לא יודע איזו תוכנה מתאימה, מאיפה להביא אותה או איך מתקינים? אנחנו מאתרים, מתקינים ומגדירים, גם במחשב בלי אינטרנט.",
  what=[("איתור התוכנה","נמצא את התוכנה שעושה בדיוק את מה שצריך."),("התקנה והגדרה","מותקנת, מוגדרת ומוכנה לעבודה."),("בלי אינטרנט","התקנה מלאה גם במחשב שאין בו אינטרנט."),("הדרכה קצרה","מסבירים איך עובדים איתה.")],
  who=["מי שעובד במחשב בלי אינטרנט","עסקים ומשרדים","מוסדות","כל מי שלא רוצה להסתבך"],
  steps=[("מספרים מה צריך","מה התוכנה צריכה לעשות."),("ממליצים","איזו תוכנה מתאימה, ובכמה."),("מתקינים","מוכן לעבודה.")],
  faq=[("אם אין תוכנה שמתאימה?","נבנה אחת. ראו תוכנות למחשב בהתאמה אישית."),("זה עובד גם בלי אינטרנט?","כן, זו בדיוק ההתמחות שלנו.")]),
 dict(path="/apps/", svc="apps", subj="פיתוח", icon="phone",
  title="פיתוח אפליקציות אנדרואיד במחירי רצפה | כשר טק",
  desc="פיתוח אפליקציות אנדרואיד לעסקים, למוסדות ולמכשירים סגורים: חדשות מאפס, שיפור קיימות, ואפליקציות שעובדות בלי אינטרנט. מהר ובמחירי רצפה.",
  h1="אפליקציה משלך.<br><em>מהר, ובמחיר רצפה.</em>",
  lead="אפליקציה שעושה בדיוק את מה שצריך, נבנית עם הכלים המתקדמים ביותר, ובמחיר שאי אפשר להתחרות בו.",
  what=[("אפליקציות חדשות","מרעיון לאפליקציה עובדת."),("שיפור קיימות","תיקונים, תוספות והתאמות לאפליקציה שכבר יש."),("בלי אינטרנט","אפליקציות שעובדות במכשירים סגורים ובנגנים."),("לעסקים ולמוסדות","הזמנות, רשימות, ניהול ומידע לחברים.")],
  who=["עסק שרוצה אפליקציה","מוסד, ישיבה או ארגון","בעלי נגנים ומכשירים סגורים","מי שיש לו רעיון"],
  steps=[("מספרים את הרעיון","מה האפליקציה צריכה לעשות."),("הצעה ברורה","מחיר וזמן מראש."),("אפליקציה מוכנה","בודקים יחד ומתקנים עד שזה מושלם.")],
  faq=[("כמה זמן זה לוקח?","אפליקציה פשוטה מוכנה בדרך כלל מהר מאוד. נאמר זמן מדויק בהצעה."),("אפשר לעדכן בהמשך?","כן, תמיד.")]),
 dict(path="/software/", svc="software", subj="פיתוח", icon="code",
  title="תוכנות למחשב בהתאמה אישית | אוטומציה לאקסל | כשר טק",
  desc="תוכנות וכלים למחשב בהתאמה אישית: אוטומציה לאקסל, לקבצים ולעבודה משרדית, ניהול נתונים ודוחות. לעסקים, למוסדות ולגמ\"חים, במחירי רצפה.",
  h1="כלי שחוסך <em>שעות עבודה</em>.<br>מהר ובזול.",
  lead="תוכנה שעושה בדיוק את מה שאתם צריכים, בלי לשלם סכומי עתק למתכנת.",
  what=[("אוטומציה לאקסל","דוחות, חישובים וסידור נתונים בלחיצה."),("קבצים ומסמכים","שינוי שמות, המרות, מיזוג והדפסה בכמויות."),("ניהול נתונים","רשימות, לקוחות, תרומות והלוואות במקום אחד."),("כלים בהתאמה אישית","כל מה שחוזר על עצמו כל יום.")],
  who=["משרדים ועסקים","גמ\"חים ומוסדות","מי שעובד הרבה עם אקסל","כל מי שנמאס לו מעבודה חוזרת"],
  steps=[("מספרים מה מעייף","איזו עבודה חוזרת על עצמה."),("הצעה ברורה","מחיר מראש."),("כלי מוכן","עובד, ובדוק על הנתונים שלכם.")],
  faq=[("זה עובד בלי אינטרנט?","כן, ברוב המקרים."),("זה מסובך לשימוש?","לא. בונים בדיוק לפי איך שאתם עובדים.")]),
 dict(path="/websites/", svc="websites", subj="אתר", icon="globe",
  title="בניית אתרים לעסקים במחירי רצפה | כשר טק",
  desc="בניית אתר תדמית ואתר עסקי: עיצוב אישי, מותאם לטלפון, טופס פנייה למייל, ממשק לעדכון תכנים והקמה בגוגל. במחירי רצפה.",
  h1="אתר לעסק <em>שמביא לקוחות</em>.<br>במחיר רצפה.",
  lead="אתר מעוצב, מהיר ומוכן לחיפוש בגוגל, עם עיצוב גרפי מקצועי מהצוות שלנו.",
  what=[("עיצוב אישי","מותאם לעסק ולציבור, מהמעצבת שלנו."),("טלפון ומחשב","נראה מצוין בכל מסך."),("טופס פנייה","פניות מגיעות ישר למייל."),("עדכון בעצמך","ממשק פשוט לעדכון תכנים, מחירים ומוצרים."),("גוגל","מוכן לחיפוש, עם כתובת ואחסון.")],
  who=["עסקים קטנים","מוסדות וארגונים","בעלי מקצוע","גמ\"חים"],
  steps=[("מספרים על העסק","מה רוצים שיהיה באתר."),("עיצוב","רואים ומתקנים."),("האתר באוויר","מוכן, ומוכר לגוגל.")],
  faq=[("אפשר לעדכן לבד?","כן, יש ממשק פשוט."),("כולל גם לוגו?","אפשר. המעצבת שלנו תעצב לוגו ומיתוג באותה הזדמנות.")]),
 dict(path="/translate/", svc="translate", subj="פיתוח", icon="lang",
  title="תרגום אפליקציות לעברית | כשר טק",
  desc="תרגום אפליקציות לעברית מלאה: ממשק ותכנים, התאמה לכתיבה מימין לשמאל, גם לאפליקציות שאין להן גרסה רשמית בעברית.",
  h1="האפליקציה שלך,<br><em>בעברית מלאה.</em>",
  lead="תרגום מסודר של ממשק ותכנים, גם כשלאפליקציה אין גרסה רשמית בעברית.",
  what=[("תרגום הממשק","כל הכפתורים, התפריטים וההודעות."),("ימין לשמאל","התצוגה מסודרת כמו שצריך."),("גם בלי תמיכה רשמית","גם באפליקציות שלא נועדו לתרגום.")],
  who=["בעלי נגנים","מבוגרים שלא קוראים אנגלית","עסקים"],
  steps=[("שולחים את האפליקציה","או את שמה."),("מתרגמים","ובודקים שהכול נראה טוב."),("מתקינים","מוכן לשימוש.")],
  faq=[("זה עובד באפליקציה שכבר מותקנת?","מקבלים גרסה מתורגמת שמחליפה אותה.")]),
 dict(path="/plugins/", svc="scripts", subj="פיתוח", icon="bolt",
  title="תוספים וסקריפטים לדפדפן ולתוכנות | כשר טק",
  desc="תוסף שנכנס לדפדפן או לתוכנה שכבר יש לכם וחוסך שעות: טפסים שממלאים את עצמם, נתונים שעוברים לאקסל וכפתורים חדשים באתרים. במחירי רצפה.",
  h1="שעה של עבודה כל יום,<br><em>בשנייה אחת.</em>",
  lead="תוסף הוא תוכנה קטנה שנכנסת לדפדפן או לתוכנה שאתם כבר משתמשים בה, ומוסיפה בדיוק את מה שחסר.",
  what=[("לחיצה אחת במקום עשר","פעולה חוזרת הופכת לכפתור."),("טפסים שממלאים את עצמם","בלי הקלדה ובלי טעויות."),("נתונים שעוברים לבד","מאתר לאקסל, מאקסל למסמך."),("כפתור שחסר","בדיוק באתר או במערכת שאתם עובדים בהם.")],
  who=["משרדים","מי שעובד במערכות אינטרנטיות כל יום","עסקים ומוסדות"],
  steps=[("מספרים מה מעייף","איזו פעולה חוזרת."),("בונים","מהר ובזול."),("חוסכים זמן","מהיום הראשון.")],
  faq=[("זה בטוח?","כן. התוסף עושה רק את מה שנבנה לעשות, ואתם רואים בדיוק מה.")]),
]
def landing(L):
    p = head(L["title"], L["desc"], L["path"])
    what = "".join('<li><strong>%s</strong><br>%s</li>' % w for w in L["what"])
    who = "".join('<li>%s</li>' % w for w in L["who"])
    steps = "".join('<li><strong>%s</strong><br>%s</li>' % s for s in L["steps"])
    faq = "".join('<details class="faq"><summary>%s</summary><p>%s</p></details>' % f for f in L["faq"])
    p += f'''<section class="hero lp"><div class="wrap"><div>
  <p class="pricebadge">מחירי רצפה · הצעה ברורה מראש</p>
  <h1>{L["h1"]}</h1><p class="lead">{L["lead"]}</p>
  <p><span class="price" data-svc="{L["svc"]}">במחיר רצפה</span></p>
  <div class="cta"><a class="btn primary" href="/contact/?subject={L["subj"]}">לקבלת הצעה</a><a class="btn ghost" href="/services/">לכל השירותים</a></div>
</div><div class="ico lpico">{ICONS[L["icon"]]}</div></div></section>
<section class="block"><div class="wrap"><h2 class="title">מה מקבלים</h2><ul class="feat">{what}</ul></div></section>
<section class="block alt"><div class="wrap"><h2 class="title">למי זה מתאים</h2><ul class="feat">{who}</ul></div></section>
<section class="block"><div class="wrap"><h2 class="title">איך זה עובד</h2><ol class="steps">{steps}</ol></div></section>
<section class="block alt"><div class="wrap"><h2 class="title">שאלות נפוצות</h2>{faq}</div></section>
'''
    p += CTA_BAND + foot()
    write(L["path"], p)
for _L in LANDINGS: landing(_L)
# ---------- PLAYER EDITING BLOCKS (shown on the players page) ----------
a = '''<section class="block"><div class="wrap">
<h2 class="title">איך אנחנו נכנסים לנגן</h2>
<p class="sub">שלוש שיטות, לפי הדגם ולפי כמה עמוק צריך להגיע.</p>
<div class="grid c3">'''
a += card("shield","חסימה וניהול (MDM)","הנגן עובר לניהול מלא, בלי פריצה ובלי לפגוע בתוכנה של היצרן.",["חסימת אפליקציות, הגדרות והתקנות","נעילה שקשה מאוד לעקוף","אפשר להוסיף ולהוריד בהמשך"],price="מתאים לרוב הנגנים")
a += card("bolt","רוט ועריכת המערכת","גישה לליבת המערכת: מסירים ומשנים כל מה שצריך, מבפנים.",["הסרת רכיבים מהמערכת עצמה","הסרת האינטרנט, הדפדפנים והחנות לגמרי","עריכה עמוקה של המערכת"],price="לנגנים נתמכים")
a += card("phone","קושחה ייעודית","בונים לנגן מערכת משלו, נקייה וסגורה כבר מההתחלה.",["מערכת שנבנתה מחדש","קובץ מוכן לצריבה","מתאים להכשרת כמה נגנים זהים"],price="לפי דגם")
a += '''</div></div></section>
<section class="block alt"><div class="wrap">
<h2 class="title">למה אף אחד לא עושה את זה?</h2>
<div class="grid c2 whyc">
<article class="card"><h3>כל נגן שונה</h3><p>אין "כפתור הכשרה". כל דגם בנוי אחרת, ומה שעובד באחד שובר את השני. צריך להכיר את הנגן מבפנים.</p></article>
<article class="card"><h3>להסיר, לא רק לחסום</h3><p>חסימה רגילה אפשר לעקוף. כדי שהאינטרנט באמת לא יהיה, מוציאים אותו מתוך המערכת, בלי לפגוע בשמע, בבלוטות' ובשאר הדברים.</p></article>
<article class="card"><h3>כל תוכנה נבדקת</h3><p>תוכנה שנראית תמימה יכולה לפתוח דלת לאינטרנט או לסרטים. לכן כל דבר נבדק על הנגן עצמו לפני שהוא נכנס.</p></article>
<article class="card"><h3>עבודה קטנה, מחיר קטן</h3><p>אצל אחרים זה לא שווה את הזמן, ולכן או שלא יעשו, או שיגבו הרבה. אצלנו זו ההתמחות, ולכן זה מהיר ובמחיר רצפה.</p></article>
</div>
</div></section>
<section class="block"><div class="wrap">
<h2 class="title">מה עוד אפשר לעשות בנגן</h2>
<p class="sub">הנגן מוכשר אצלנו בלי אינטרנט. מכאן, אפשר לבנות כמעט כל שילוב:</p>
<ul class="feat">
<li><strong>הסרת האינטרנט מהנגן</strong>: WiFi ונתונים מוסרים ברמת המערכת, לא רק חסומים</li>
<li><strong>הסרת דפדפנים, חנות אפליקציות ואפליקציות מובנות</strong> שאין בהן צורך</li>
<li><strong>חסימת מצלמה, גלריה והעברת קבצים</strong>, או כל שילוב אחר</li>
<li><strong>שיעורים ותכנים</strong> שנטענים מראש</li>
<li><strong>נגן לילד או לנער</strong> עם מה שמתאים לו בלבד</li>
<li><strong>הכשרת כמה נגנים זהים</strong> לישיבות, למוסדות ולעסקים</li>
<li><strong>אפליקציה ייעודית</strong> שנבנית במיוחד לנגן שלך</li>
<li><strong>ושאר התאמות</strong>: אם יש צורך מסוים, כנראה שאפשר לעשות אותו</li>
</ul>
</div></section>
'''
PLAYER_EDIT = a
write("/android/", '''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>הכשרת נגני אנדרואיד | כשר טק</title>
<link rel="canonical" href="https://kosher-tek.com/players/"><meta http-equiv="refresh" content="0;url=/players/"></head>
<body><p><a href="/players/">לדף הכשרת נגני אנדרואיד</a></p></body></html>''')
# ---------- SHOP ----------
sh = head("חנות נגנים | כשר טק: נגני אנדרואיד מוכשרים",
          "הקו השמור: נגני אנדרואיד מוכשרים בלי אינטרנט ובלי סרטים, בשלוש גרסאות. סדרת הזמיר: הזמיר והזמיר פלוס עם פנס ומצלמה. אנדרואיד, מסך מגע 4 אינץ', Bluetooth ורדיו. מגיעים מוכנים, בלי אינטרנט.", "/shop/")
sh += '''<section class="pagehead"><div class="wrap"><h1>הקו השמור</h1><p>נגני אנדרואיד שנבחרו בקפידה ומגיעים מוכשרים ומוכנים לשימוש. אנחנו לא מוכרים מה שאנחנו לא עומדים מאחוריו.</p></div></section>
<section class="block"><div class="wrap">
<div class="guard"><strong>בכל הנגנים שלנו:</strong> בלי אינטרנט ובלי סרטים. אנחנו לא תומכים במשחקים ולא מכניסים אותם. זה לא תוסף, זה הבסיס.</div>
<div class="intro2">
<div><h2 class="title">מה זה נגן אנדרואיד?</h2>
<p>תחשוב על פלאפון כשר, רק בלי שיחות ועם מסך מגע גדול ונוח. שומעים בו שיעורים ושירים, מקליטים, ויכולים להיות בו גם ספרי קודש, מפות, מחשבון ועוד הרבה דברים שימושיים. הכול עובד בלי אינטרנט.</p>
<p>ההבדל בין נגן טוב לנגן מסוכן הוא איך הכשירו אותו. אצלנו האינטרנט מוסר מתוך המערכת עצמה, כל תוכנה נבדקת על הנגן לפני שהיא נכנסת, ואתה בוחר בדיוק מה יהיה בו.</p></div>
<ul class="pros"><li><strong>בלי אינטרנט</strong>, מוסר מבפנים ולא רק חסום</li><li><strong>בלי סרטים ובלי משחקים</strong></li><li><strong>רק מה שבחרת</strong>, וכל דבר נבדק על הנגן</li><li><strong>אפשר לשנות</strong> אחר כך, אם תצטרך</li></ul>
</div>
<h2 class="title" id="versions">שלוש גרסאות</h2>
<p class="sub">כל נגן בחנות אפשר להזמין בכל אחת מהגרסאות. בוחרים לפי הצורך, מהשמורה ביותר.</p>
<div class="grid c3 tiers">
<article class="card tier"><span class="tnum">1</span><h3>שמור</h3><p>אפליקציות בסיס בלבד, בלי שום התקנה.</p><ul><li>נגן, רדיו, הקלטה ושיעורים</li><li>שעון, מחשבון, לוח שנה וקבצים</li><li>אי אפשר להוסיף אפליקציות</li></ul><span class="tag">השמור ביותר</span></article>
<article class="card tier"><span class="tnum">2</span><h3>שמור עם חנות פנימית</h3><p>כל הבסיס, ובנוסף חנות פנימית נרחבת של אפליקציות שנבדקו ואושרו.</p><ul><li>מבחר רחב של אפליקציות מאושרות</li><li>מתקינים רק מתוך החנות הפנימית</li><li>בלי התקנה מבחוץ ובלי משחקים</li></ul></article>
<article class="card tier"><span class="tnum">3</span><h3>גרסה פתוחה: התקנה מבחוץ</h3><p>לשימוש מתקדם: אפשר להתקין אפליקציות גם מבחוץ.</p><ul><li>התקנת קבצי אפליקציה מבחוץ</li><li>משחקים: אנחנו לא תומכים בהם ולא מכניסים אותם, אבל בפועל אפשר להתקין לבד</li><li>עדיין בלי אינטרנט ובלי סרטים</li></ul></article>
</div>
<div class="quizcta"><div><strong>לא בטוח איזו גרסה מתאימה לך?</strong><span>כמה שאלות פשוטות, ונמליץ על נגן וגרסה.</span></div><button type="button" class="btn primary" id="quizopen">צריך עזרה בבחירת גרסה?</button></div>
<div id="quiz" class="quiz" hidden></div>
<h2 class="title" style="margin-top:44px">מה אפשר שיהיה בנגן</h2>
<p class="sub">דוגמאות למה שאפשר להכניס. כל דבר נבדק אצלנו על הנגן עצמו לפני שהוא נכנס.</p>
<div class="grid c3 catgrid" id="catalog"></div>
<h2 class="title" style="margin-top:44px">הנגנים</h2>
<div class="grid c2" id="products"></div>
<h2 class="title" style="margin-top:44px">השוואה בין הנגנים</h2>
<div class="cmp">
<div class="cmp-both"><h3>בשני הנגנים</h3><ul>
<li>אנדרואיד, מסך מגע 4 אינץ' וגוף מתכת</li><li>רמקול מובנה ושקע לאוזניות</li><li>Bluetooth ורדיו FM</li><li>הקלטה</li>
<li>כרטיס זיכרון להרחבה</li><li>קורא ספרים, שעון ומד צעדים</li><li>סוללה ליותר מ-20 שעות שמיעה</li><li>קבצי שמע: MP3, WAV, FLAC, AAC, OGG</li>
<li>מגיעים מוכשרים, בלי אינטרנט</li></ul></div>
<table class="cmp-diff"><thead><tr><th>מה שונה</th><th>הזמיר</th><th>הזמיר פלוס</th></tr></thead><tbody>
<tr><td>אחסון</td><td>16GB (או 64GB לפי בקשה)</td><td>32GB</td></tr>
<tr><td>פנס</td><td>לא</td><td>כן</td></tr>
<tr><td>מצלמה</td><td>לא</td><td>כן (אפשר לסגור)</td></tr>
</tbody></table>
</div>
<div class="note" style="margin-top:24px">התשלום אינו מתבצע באתר. אחרי יצירת קשר נתאם הכול ישירות.</div></div></section>
'''
sh += foot()
write("/shop/", sh)

# ---------- PLAYER KASHERING (a player the customer already has) ----------
_i = sh.index('<div class="intro2">'); _j = sh.index('<h2 class="title" style="margin-top:44px">הנגנים</h2>')
_core = sh[_i:_j]
_v = _core.index('<h2 class="title" id="versions">')
_levels = PLAYER_EDIT[:PLAYER_EDIT.index('<h2 class="title">מה עוד אפשר לעשות בנגן</h2>')]
_poss = PLAYER_EDIT[PLAYER_EDIT.index('<h2 class="title">מה עוד אפשר לעשות בנגן</h2>'):]
_core = _core[:_v] + '</div></section>\n' + _levels + '<section class="block"><div class="wrap">\n' + _core[_v:] + _poss.replace('</div></section>', '', 1)
_core = _core.replace("כל נגן בחנות אפשר להזמין בכל אחת מהגרסאות. בוחרים לפי הצורך, מהשמורה ביותר.", "את הנגן שלך אפשר להכשיר בכל אחת מהגרסאות. בוחרים לפי הצורך, מהשמורה ביותר.")
_core = _core.replace("כמה שאלות פשוטות, ונמליץ על נגן וגרסה.", "כמה שאלות פשוטות, ונמליץ על הגרסה שמתאימה לך.")
_core = _core.replace('<div id="quiz" class="quiz" hidden></div>', '<div id="quiz" class="quiz" data-mode="kasher" hidden></div>')
pl = head("הכשרת נגני אנדרואיד | כשר טק",
          "הכשרת נגני אנדרואיד מכל הדגמים, במחירי רצפה: חסימה וניהול (MDM), רוט וקושחה ייעודית, בלי אינטרנט ובלי סרטים, בשלוש גרסאות ועם כל מה שתרצה שיהיה בנגן. מה שאף אחד לא עושה.", "/players/")
pl += '''<section class="pagehead"><div class="wrap"><h1>הכשרת נגני אנדרואיד</h1><p>ההתמחות שלנו, במחיר רצפה: עבודות שאף אחד לא עושה, או שאצל אחרים יקרות מדי. יש לך נגן? נכשיר אותו בדיוק לפי מה שאתה צריך: בלי אינטרנט, בלי סרטים, ורק עם מה שבחרת. כל הדגמים. בסמארטפונים אנחנו לא נוגעים.</p></div></section>
<section class="block"><div class="wrap">
<div class="guard"><strong>בכל נגן שאנחנו מכשירים:</strong> האינטרנט מוסר מתוך המערכת, ואין סרטים. אנחנו לא תומכים במשחקים ולא מכניסים אותם.</div>
''' + _core + '''<h2 class="title" style="margin-top:44px">איך זה עובד</h2>
<ol class="steps">
<li><strong>מספרים לנו</strong><br>איזה נגן יש לך ומה אתה רוצה שיהיה בו. השאלון למעלה עושה את זה בדקה.</li>
<li><strong>מביאים או שולחים</strong><br>את הנגן אלינו, ומקבלים מחיר ברור מראש.</li>
<li><strong>מקבלים נגן מוכשר</strong><br>בדוק, מוכן לשימוש, ואפשר לשנות גרסה גם אחר כך.</li>
</ol>
<p class="more-svc">אין לך נגן? <a href="/shop/">אפשר לקנות נגן מוכשר מהקו השמור שלנו ←</a></p>
</div></section>
'''
pl += CTA_BAND
pl += foot()
write("/players/", pl)

# ---------- FORUM (separate look, not part of the business site) ----------
FORUM = "מלאכת מחשבת"

def fhead(title, path, desc=None):
    idx = desc is not None
    meta = (f'<meta name="description" content="{html.escape(desc)}">\n<link rel="canonical" href="{SITE}{path}">\n<meta property="og:site_name" content="{FORUM}">\n<meta property="og:title" content="{html.escape(title)}">\n<meta property="og:description" content="{html.escape(desc)}">\n<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"{FORUM}","alternateName":"פורום מלאכת מחשבת","url":"{SITE}/market/"}}</script>') if idx else '<meta name="robots" content="noindex">'
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
{meta}
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
r = head("בקשות ועבודות | כשר טק", "לוח בקשות ועבודות: מפרסמים מה צריך, ואנשי מקצוע וחברות לוקחים את העבודה.", "/request/")
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
mk = fhead(FORUM + " | פורום ולוח עבודות טכנולוגיה לציבור החרדי", "/market/", "מלאכת מחשבת: פורום ולוח עבודות טכנולוגיה. מפרסמים בקשה לעבודה במחשבים, נגנים, אפליקציות ותוכנות, ואנשי מקצוע מאושרים מגישים הצעות.")
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
 ("האתר הפרטי (כשר טק)", [("האתר", "/"), ("ניהול האתר", "/admin/")]),
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
ru = fhead("כללי הלוח | " + FORUM, "/market/rules/", "כללי הפורום והלוח של מלאכת מחשבת: איך מפרסמים בקשה, איך מגישים הצעה, ומה מותר ואסור.")
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
k = head("צור קשר | כשר טק", "טופס פנייה, טלפון ומייל.", "/contact/")
k += f'''<section class="pagehead"><div class="wrap"><h1>צור קשר</h1><p>השאר פרטים ונחזור אליך. אפשר גם להתקשר: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div></section>
<section class="block"><div class="wrap">
<form class="contact" id="cf" novalidate>
  <label>שם<input name="name" autocomplete="name" required></label>
  <label>טלפון או מייל<input name="contact" autocomplete="tel" required></label>
  <label>במה מדובר<select name="subject">
    <option>הכשרת נגן</option><option>התקנת מחשב</option><option>תוכנה בהתאמה אישית</option><option>עיצוב</option>
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
  try{{var pr=new URLSearchParams(location.search).get('product');if(pr){{pr=pr.slice(0,60);var o=document.createElement('option');o.value='הזמנה: '+pr;o.textContent='הזמנה: '+pr;f.subject.insertBefore(o,f.subject.firstChild);f.subject.selectedIndex=0;if(!f.message.value)f.message.value='אני מעוניין: '+pr+'. ';}}var dt=new URLSearchParams(location.search).get('details');if(dt)f.message.value=(f.message.value+'\\n'+dt.slice(0,1200)).trim()+'\\n';}}catch(e){{}}
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
