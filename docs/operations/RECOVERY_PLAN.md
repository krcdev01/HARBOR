# Recovery Plan

## Purpose
This document describes the procedure to rebuild the server from bare metal using Borg backups.

## Full Server Recovery Procedure

### Phase 1 — Base System
1. Install Ubuntu Server
2. Create user: serveradmin
3. Install Docker and Docker Compose
4. Mount storage drives:
   - /mnt/movies
   - /mnt/tv
   - /mnt/downloads

### Phase 2 — Restore Borg Access
Restore the following directory FIRST:

/root/.config/corsair/

This contains borg.env which allows access to the backup repository.

Without this file, backups cannot be accessed.

### Phase 3 — Restore Configuration
Mount the Borg repository:

/srv/borg/config-repo

List archives:
borg list /srv/borg/config-repo

Restore latest archive:
borg extract /srv/borg/config-repo::corsair-config-YYYY-MM-DD_HH-MM

This will restore:
- /etc
- /home/serveradmin
- /opt/arrstack
- /srv/jellyfin
- /srv/pihole

### Phase 4 — Rebuild Services
After restore:

1. Start Docker
2. Start Gluetun stack
3. Start arr stack (Sonarr, Radarr, Prowlarr, qBittorrent)
4. Start Jellyfin
5. Start Pi-hole
6. Start Cloudflared

### Phase 5 — Verification
Verify:

- Jellyfin libraries visible
- Radarr/Sonarr connected to qBittorrent
- VPN port forwarding working
- Backups running
- SMART monitoring (future)

## Recovery Goal

Target recovery time:
- Full server rebuild: < 4 hours
- Service restore: < 1 hour after config restore

This backup system is designed so the server is disposable and fully recoverable.
