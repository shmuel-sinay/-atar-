#!/bin/bash
# Run on the server:  sudo bash deploy.sh https://github.com/USER/REPO.git
set -e
REPO="${1:?usage: deploy.sh <git-repo-url>}"
WEB=/var/www/kosher-site
apt-get install -y git nginx >/dev/null 2>&1
if [ -d "$WEB/.git" ]; then git -C "$WEB" pull -q; else rm -rf "$WEB"; git clone -q "$REPO" "$WEB"; fi
cp "$WEB/server/nginx-kt.conf" /etc/nginx/conf.d/kt.conf
# contact backend
mkdir -p /var/lib/kt-contact /etc/kt-contact
[ -f /etc/kt-contact/env ] || printf 'KT_SMTP_USER=\nKT_SMTP_PASS=\nKT_MAIL_TO=g47ben@gmail.com\n' > /etc/kt-contact/env
chmod 600 /etc/kt-contact/env
# admin password: created once, printed once
if ! grep -q '^KT_ADMIN_PASS=.' /etc/kt-contact/env; then
  NEWPASS=$(python3 -c 'import secrets;print(secrets.token_urlsafe(12))')
  sed -i '/^KT_ADMIN_PASS=/d' /etc/kt-contact/env
  echo "KT_ADMIN_PASS=$NEWPASS" >> /etc/kt-contact/env
  echo "=== סיסמת הניהול (מופיעה רק עכשיו, שמור אותה): $NEWPASS ==="
fi
# separate password for the work board admin (/market/admin/), also printed once
if ! grep -q '^KT_MARKET_ADMIN_PASS=.' /etc/kt-contact/env; then
  MPASS=$(python3 -c 'import secrets;print(secrets.token_urlsafe(12))')
  sed -i '/^KT_MARKET_ADMIN_PASS=/d' /etc/kt-contact/env
  echo "KT_MARKET_ADMIN_PASS=$MPASS" >> /etc/kt-contact/env
  echo "=== סיסמת ניהול הלוח (מופיעה רק עכשיו, שמור אותה): $MPASS ==="
fi
cat > /etc/systemd/system/kt-contact.service <<'UNIT'
[Unit]
Description=Kosher Tek site backend (contact form, admin panel)
After=network.target
[Service]
EnvironmentFile=/etc/kt-contact/env
ExecStart=/usr/bin/python3 -I /var/www/kosher-site/server/app.py
Restart=always
User=www-data
StateDirectory=kt-contact
[Install]
WantedBy=multi-user.target
UNIT
chown -R www-data:www-data /var/lib/kt-contact
systemctl daemon-reload
systemctl enable --now kt-contact >/dev/null 2>&1
systemctl restart kt-contact
# auto-update from GitHub every minute
cat > /usr/local/sbin/kt-site-update <<'UPD'
#!/bin/bash
cd /var/www/kosher-site || exit 0
OLD=$(git rev-parse HEAD)
git pull -q --ff-only 2>/dev/null || exit 0
NEW=$(git rev-parse HEAD)
if [ "$OLD" != "$NEW" ]; then
  cp server/nginx-kt.conf /etc/nginx/conf.d/kt.conf
  nginx -t >/dev/null 2>&1 && systemctl reload nginx
  systemctl restart kt-contact
fi
UPD
chmod +x /usr/local/sbin/kt-site-update
( crontab -l 2>/dev/null | grep -v kt-site-update; echo '* * * * * /usr/local/sbin/kt-site-update' ) | crontab -
if nginx -t >/dev/null 2>&1; then
  systemctl stop landing.service 2>/dev/null || true
  systemctl reload nginx || systemctl restart nginx
  echo "site: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/)  shop: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/shop/)  api: $(curl -s -o /dev/null -w '%{http_code}' -X POST -d '{}' http://127.0.0.1:8088/api/contact)"
else
  nginx -t; echo "nginx config FAILED, nothing reloaded"
fi
