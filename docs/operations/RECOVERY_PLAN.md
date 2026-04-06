# Recovery Plan

## Purpose

This document describes the procedure to rebuild the server from bare metal using Borg backups.

## Full Server Recovery Procedure

### Phase 1 — Base System

1. Install Ubuntu Server 24.04 (Noble)

2. Create user: serveradmin

3. Install Docker and Docker Compose
```
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
```

4. Create required mount points used by the media stack.
```
sudo mkdir -p /mnt/movies /mnt/tv /mnt/downloads
```

5. Create SSH Key for GitHub
```
ssh-keygen -t ed25519 -C "serveradmin@stageserver"
cat ~/.ssh/id_ed25519.pub
```
Copy the key into your GitHub account for SSH auth.

6. Clone the required homeserver repositories into an isolated subfolder ****THIS NEEDS TO DIFFERENTIATE BETWEEN RESTORE VERSUS DEPLOYMENT****
```
git clone git@github.com:krcdev01/homeserver-infra.git
git clone git@github.com:krcdev01/homeserver-apps.git
```

### Phase 2 — Restore Borg Access

1. Restore the following directory from homserver-infra: 
```
/root/.config/corsair/
```

2. Switch to the root user and navigate to this directory.

3. Update the borg.env.template file and add the decryption password, then rename the file to borg.env
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