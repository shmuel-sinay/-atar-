# כושר טק: האתר

אתר סטטי בעברית (HTML + CSS בלבד, בלי ספריות חיצוניות) + שרת קטן לטופס הפנייה.

מבנה: `/` בית, `/services/`, `/android/`, `/shop/`, `/request/`, `/contact/`. `/chat/` הוא פרויקט נפרד (קהל אחר), לא מקושר מהאתר ולא נסרק.

התקנה בשרת: `sudo bash server/deploy.sh https://github.com/USER/REPO.git`
אחרי זה כל שינוי שנדחף ל-main מתעדכן באתר תוך דקה.

מייל מהטופס: לערוך את `/etc/kt-contact/env` (KT_SMTP_USER ו-KT_SMTP_PASS, סיסמת אפליקציה של Gmail), ואז `sudo systemctl restart kt-contact`.
הודעות נשמרות גם בקובץ `/var/lib/kt-contact/messages.jsonl`.

## לוח ניהול
`/admin/` (סיסמה ב-`KT_ADMIN_PASS` בקובץ `/etc/kt-contact/env`, נוצרת אוטומטית ב-deploy הראשון ומודפסת פעם אחת).
מוצרים (שם, מחיר, סטטוס, תמונה, סדר), מחירי שירותים והודעות מהטופס.
הנתונים ב-`/var/lib/kt-contact/` (data.json, messages.jsonl, uploads/). האתר הסטטי נשאר כמו שהוא אם השרת הקטן לא עובד.
יצירת הדפים מחדש: `python3 gen.py` (הפלט נכתב בתיקייה הנוכחית).
