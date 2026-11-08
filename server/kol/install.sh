#!/usr/bin/env bash
# קול לשולחן העבודה המרוחק: מתקין ממסר + משדר על השרת.
# הרצה (פעם אחת):  sudo bash /var/www/kosher-site/server/kol/install.sh
set -euo pipefail

KOL_USER="${KOL_USER:-ubuntu}"          # המשתמש ששולחן העבודה המרוחק רץ תחתיו
UID_N="$(id -u "$KOL_USER")"
RUNDIR="/run/user/$UID_N"
HERE="$(cd "$(dirname "$0")" && pwd)"
as_user() { sudo -u "$KOL_USER" XDG_RUNTIME_DIR="$RUNDIR" "$@"; }

echo "== חבילות"
apt-get update -qq
apt-get install -y -qq pulseaudio-utils >/dev/null
command -v node >/dev/null || apt-get install -y -qq nodejs >/dev/null
command -v npm  >/dev/null || apt-get install -y -qq npm >/dev/null

echo "== שרת קול למשתמש $KOL_USER"
loginctl enable-linger "$KOL_USER"
systemctl start "user@$UID_N.service"
for i in $(seq 1 20); do [ -d "$RUNDIR" ] && break; sleep 0.5; done
if as_user pactl info >/dev/null 2>&1; then
  echo "כבר קיים שרת קול"
else
  apt-get install -y -qq pipewire pipewire-pulse wireplumber >/dev/null
  as_user systemctl --user enable --now pipewire.socket pipewire-pulse.socket wireplumber.service
fi
# כל תוכנה בשולחן העבודה תנגן לאותו שרת קול
mkdir -p /etc/pulse/client.conf.d
echo "default-server = unix:$RUNDIR/pulse/native" > /etc/pulse/client.conf.d/kol.conf

echo "== התקנה ל-/opt/kol"
mkdir -p /opt/kol
cp "$HERE/relay.js" "$HERE/sender.js" "$HERE/ensure-sink.sh" /opt/kol/
chmod +x /opt/kol/ensure-sink.sh
[ -f /opt/kol/package.json ] || echo '{"private":true}' > /opt/kol/package.json
(cd /opt/kol && npm install --silent ws@8)

# קוד גישה: נוצר פעם אחת ומודפס פעם אחת
mkdir -p /etc/kol
if [ ! -f /etc/kol/env ]; then
  KEY=$(python3 -c 'import secrets;print(secrets.randbelow(900000)+100000)')
  printf 'ACCESS_KEY=%s\nKOL_KEY=%s\n' "$KEY" "$KEY" > /etc/kol/env
  echo "=== קוד הגישה לקול (מופיע רק עכשיו, שמור אותו): $KEY ==="
fi
chmod 600 /etc/kol/env

cat > /etc/systemd/system/kol-relay.service <<'UNIT'
[Unit]
Description=Kol relay (desktop audio -> /kol/ws)
After=network.target
[Service]
EnvironmentFile=/etc/kol/env
ExecStart=/usr/bin/node /opt/kol/relay.js
Restart=always
DynamicUser=yes
[Install]
WantedBy=multi-user.target
UNIT

cat > /etc/systemd/system/kol-sender.service <<UNIT
[Unit]
Description=Kol sender (captures desktop audio)
After=kol-relay.service user@$UID_N.service
[Service]
User=$KOL_USER
Environment=XDG_RUNTIME_DIR=$RUNDIR
EnvironmentFile=/etc/kol/env
ExecStartPre=/opt/kol/ensure-sink.sh
ExecStart=/usr/bin/node /opt/kol/sender.js
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now kol-relay kol-sender
cp /var/www/kosher-site/server/nginx-kt.conf /etc/nginx/conf.d/kt.conf 2>/dev/null || true
nginx -t >/dev/null 2>&1 && systemctl reload nginx
sleep 3
echo
echo "relay:  $(systemctl is-active kol-relay)   sender: $(systemctl is-active kol-sender)"
echo "== מוכן. פותחים https://kosher-tek.com/screen/"
echo "   תוכנות שכבר פתוחות בשולחן העבודה (למשל הדפדפן) צריך לסגור ולפתוח מחדש."
