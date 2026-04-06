#!/bin/sh
set -eu

QB_URL="http://127.0.0.1:18080"
LOGIN_URL="$QB_URL/api/v2/auth/login"
PREFS_URL="$QB_URL/api/v2/app/setPreferences"
COOKIE_JAR="/tmp/qb_cookie.txt"

QB_USERNAME="${QB_USERNAME:?QB_USERNAME is required}"
QB_PASSWORD="${QB_PASSWORD:?QB_PASSWORD is required}"

wget -q \
  --save-cookies "$COOKIE_JAR" \
  --keep-session-cookies \
  --post-data "username=$QB_USERNAME&password=$QB_PASSWORD" \
  -O - \
  "$LOGIN_URL" >/dev/null

wget -q \
  --load-cookies "$COOKIE_JAR" \
  --header="Content-Type: application/x-www-form-urlencoded" \
  --post-data "json={\"listen_port\":0,\"current_network_interface\":\"lo\",\"random_port\":false,\"upnp\":false}" \
  -O - \
  "$PREFS_URL" >/dev/null

echo "qBittorrent listening port cleared because VPN forwarding went down"
