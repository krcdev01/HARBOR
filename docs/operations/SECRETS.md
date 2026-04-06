CORSAIR Backup System

Location:
/root/.config/corsair/borg.env

Purpose:
Stores Borg repository passphrase for automated backups.

Required variable:
BORG_PASSPHRASE

Permissions:
600 (root only)

Gluetun Container

Location:
/opt/arrstack/gluetun/.env

Purpose:
Stores VPN provider credentials and environment configuration used by Gluetun and the torrent-watchdog.

Required variables:

VPN Credentials

VPN_SERVICE_PROVIDER
VPN_TYPE

VPN Account Credentials

OPENVPN_USER
OPENVPN_PASSWORD

qBittorrent WebUI Credentials

QB_USERNAME
QB_PASSWORD

Gluetun Configuration

SERVER_COUNTRIES
FIREWALL
FIREWALL_INPUT_PORTS

Permissions:
600 recommended

Pi-hole

Location:
/srv/pihole/docker-compose.yml
or /srv/pihole/.env if externalized later

Purpose:
Stores the Pi-hole web UI/API password.

Required variable:
PIHOLE_WEBPASSWORD

Permissions:
600 recommended

Cloudflared Tunnel

Location:
Environment variable used by:
/srv/jellyfin/docker-compose.yml

Purpose:
Stores the Cloudflare Tunnel authentication token used to expose services externally.

Required variable:
CLOUDFLARED_TOKEN

Permissions:
600 recommended if stored in .env

Jellyfin Public Server URL

Location:
Environment variable used by:
/srv/jellyfin/docker-compose.yml

Purpose:
Defines the public URL Jellyfin uses for external access and link generation.

Required variable:
JELLYFIN_PUBLISHED_SERVER_URL

Permissions:
Not a credential, but treated as sensitive configuration and not stored directly in the repository.