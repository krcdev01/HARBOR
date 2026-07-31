#!/bin/sh
set -eu

PORT_FILE="/tmp/gluetun/forwarded_port"
QB_URL="http://127.0.0.1:18080"
LOGIN_URL="$QB_URL/api/v2/auth/login"
PREFS_URL="$QB_URL/api/v2/app/setPreferences"
COOKIE_JAR="/tmp/qb_cookie.txt"

QB_USERNAME="${QB_USERNAME:?QB_USERNAME is required}"
QB_PASSWORD="${QB_PASSWORD:?QB_PASSWORD is required}"

if [ ! -f "$PORT_FILE" ]; then
  echo "Forwarded port file not found: $PORT_FILE"
  exit 1
fi

PORT="$(tr -d '\r\n' < "$PORT_FILE")"

if [ -z "$PORT" ]; then
  echo "Forwarded port is empty"
  exit 1
fi

wget -q \
  --save-cookies "$COOKIE_JAR" \
  --keep-session-cookies \
  --post-data "username=$QB_USERNAME&password=$QB_PASSWORD" \
  -O - \
  "$LOGIN_URL" >/dev/null

wget -q \
  --load-cookies "$COOKIE_JAR" \
  --header="Content-Type: application/x-www-form-urlencoded" \
  --post-data "json={\"listen_port\":$PORT,\"current_network_interface\":\"tun0\",\"random_port\":false,\"upnp\":false}" \
  -O - \
  "$PREFS_URL" >/dev/null

echo "qBittorrent listening port updated to $PORT"
