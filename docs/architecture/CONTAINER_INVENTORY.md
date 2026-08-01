# Container Inventory

## Overview
This document inventories all containers that comprise the HARBOR platform. It defines their roles, relationships, exposed interfaces, persistence requirements, and operational notes.

This is a **platform-level document**. It does not include host-specific paths, hardware assumptions, or non-HARBOR services.

---

## Container Summary

| Container | Stack | Image | Exposed Ports | Container Paths | Depends On | Backup Required | Notes |
|---|---|---|---|---|---|---|---|
| jellyfin | Media | jellyfin/jellyfin:10.11 | 8096/tcp, 8920/tcp | /config, /cache, /media, /media_e | None | Yes | Primary media server |
| cloudflared | Remote Access | cloudflare/cloudflared:latest | None | None | jellyfin | No | Provides outbound tunnel access |
| radarr | Media Automation | lscr.io/linuxserver/radarr:latest | 7878/tcp | /config, /downloads, /movies | prowlarr, qbittorrent | Yes | Movie acquisition and organization |
| sonarr | Media Automation | lscr.io/linuxserver/sonarr:latest | 8989/tcp | /config, /downloads, /tv | prowlarr, qbittorrent | Yes | TV acquisition and organization |
| prowlarr | Media Automation | lscr.io/linuxserver/prowlarr:latest | 9696/tcp | /config | None | Yes | Indexer management |
| qbittorrent | Torrent | lscr.io/linuxserver/qbittorrent:latest | via gluetun | /config, /downloads | gluetun | Yes | Torrent client |
| gluetun | VPN | qmcgaw/gluetun:latest | 18080/tcp, 6881/tcp/udp | /gluetun | None | Yes | VPN gateway and network enforcement |
| torrent-watchdog | Automation | python:3.12-alpine | None | /app | gluetun, qbittorrent | Yes | Torrent recovery automation |

---

## Container Details

### jellyfin
- **Purpose:** Media streaming server
- **Ports:** 8096/tcp (HTTP), 8920/tcp (HTTPS)
- **Data Persistence:** /config, /cache
- **Media Mounts:** /media, /media_e
- **Notes:** GPU acceleration supported; externally exposed via tunnel

---

### cloudflared
- **Purpose:** Remote access via outbound tunnel
- **Ports:** None
- **Data Persistence:** None
- **Notes:** Requires external authentication/token

---

### radarr
- **Purpose:** Movie acquisition and library management
- **Ports:** 7878/tcp
- **Data Persistence:** /config
- **Dependencies:** prowlarr, qbittorrent
- **Notes:** Handles import and organization workflows

---

### sonarr
- **Purpose:** TV acquisition and library management
- **Ports:** 8989/tcp
- **Data Persistence:** /config
- **Dependencies:** prowlarr, qbittorrent
- **Notes:** Works in conjunction with indexers and download client

---

### prowlarr
- **Purpose:** Indexer aggregation and management
- **Ports:** 9696/tcp
- **Data Persistence:** /config
- **Notes:** Central service for ARR applications

---

### qbittorrent
- **Purpose:** Torrent client
- **Ports:** Exposed via gluetun
- **Data Persistence:** /config, /downloads
- **Dependencies:** gluetun
- **Notes:** Runs within VPN network namespace

---

### gluetun
- **Purpose:** VPN gateway and network routing enforcement
- **Ports:** 18080/tcp (WebUI proxy), 6881/tcp/udp (torrent)
- **Data Persistence:** /gluetun
- **Notes:** Controls outbound routing and port forwarding

---

### torrent-watchdog
- **Purpose:** Torrent recovery automation
- **Ports:** None
- **Data Persistence:** /app
- **Dependencies:** gluetun, qbittorrent
- **Notes:** Monitors stalled torrents and triggers corrective actions

---

## Notes
- All paths are container-relative; host mappings are implementation-specific.
- This document defines the HARBOR platform only.
- Networking and routing behavior are documented separately.
