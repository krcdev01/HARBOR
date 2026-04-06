# Container Inventory

## Overview

This document lists the active Docker containers running on the server and summarizes their role, image, host exposure, storage paths, dependency relationships, and backup relevance.

This is an inventory document. It identifies what exists. It does not describe traffic flow, VPN routing design, or remote access architecture in detail.

---

## Container Summary

| Container | Stack | Image | Host Ports | Config / Data Paths | Depends On | Backup Required | Notes |
|---|---|---|---|---|---|---|---|
| jellyfin | Media | `jellyfin/jellyfin:10.11` | `8096/tcp`, `8920/tcp` | `/srv/jellyfin/config:/config`, `/srv/jellyfin/cache:/cache`, `/mnt/tv/Videos:/media`, `/mnt/movies/videos:/media_e` | None | Yes | Primary media server |
| cloudflared | Remote Access | `cloudflare/cloudflared:latest` | None | None | `jellyfin` | No | Provides outbound Cloudflare Tunnel access |
| pihole | Infrastructure | `pihole/pihole:latest` | `53/tcp`, `53/udp`, `8080/tcp` | `/srv/pihole/etc-pihole:/etc/pihole`, `/srv/pihole/etc-dnsmasq.d:/etc/dnsmasq.d` | None | Yes | Local DNS and network filtering |
| radarr | Media Automation | `lscr.io/linuxserver/radarr:latest` | `7878/tcp` | `/opt/arrstack/radarr:/config`, `/mnt/downloads:/downloads`, `/mnt/movies:/movies` | `prowlarr`, `qbittorrent` | Yes | Archival movie acquisition and management |
| sonarr | Media Automation | `lscr.io/linuxserver/sonarr:latest` | `8989/tcp` | `/opt/arrstack/sonarr:/config`, `/mnt/downloads:/downloads`, `/mnt/tv:/tv` | `prowlarr`, `qbittorrent` | Yes | Archival TV acquisition and management |
| prowlarr | Media Automation | `lscr.io/linuxserver/prowlarr:latest` | `9696/tcp` | `/opt/arrstack/prowlarr:/config` | None | Yes | Indexer management service |
| qbittorrent | Torrent | `lscr.io/linuxserver/qbittorrent:latest` | None directly; exposed through Gluetun on `18080/tcp` | `/opt/arrstack/qbittorrent:/config`, `/mnt/downloads:/downloads` | `gluetun` | Yes | Torrent client running behind VPN |
| gluetun | Torrent / VPN | `qmcgaw/gluetun:latest` | `18080/tcp`, `6881/tcp`, `6881/udp` | `/opt/arrstack/gluetun:/gluetun` | None | Yes | VPN gateway for torrent stack |
| torrent-watchdog | Torrent Automation | `python:3.12-alpine` | None | `/opt/arrstack/gluetun/watchdog:/app` | `gluetun`, `qbittorrent` | Yes | Custom torrent recovery automation |

---

## Container Details

### jellyfin

- **Purpose:** Primary media streaming server
- **Image:** `jellyfin/jellyfin:10.11`
- **Host Ports:** `8096/tcp`, `8920/tcp`
- **Config / Data Paths:**
  - `/srv/jellyfin/config:/config`
  - `/srv/jellyfin/cache:/cache`
  - `/mnt/tv/Videos:/media`
  - `/mnt/movies/videos:/media_e`
- **Depends On:** None
- **Backup Required:** Yes
- **Notes:** Uses NVIDIA runtime and publishes the server for remote access through Cloudflared

---

### cloudflared

- **Purpose:** Cloudflare Tunnel client for remote access
- **Image:** `cloudflare/cloudflared:latest`
- **Host Ports:** None
- **Config / Data Paths:** None
- **Depends On:** `jellyfin`
- **Backup Required:** No
- **Notes:** Uses a tunnel token supplied as environment configuration

---

### pihole

- **Purpose:** Local DNS filtering and ad blocking
- **Image:** `pihole/pihole:latest`
- **Host Ports:** `53/tcp`, `53/udp`, `8080/tcp`
- **Additional Container Ports:** `67/udp`, `123/udp`, `443/tcp`
- **Config / Data Paths:**
  - `/srv/pihole/etc-pihole:/etc/pihole`
  - `/srv/pihole/etc-dnsmasq.d:/etc/dnsmasq.d`
- **Depends On:** None
- **Backup Required:** Yes
- **Notes:** Provides DNS service to local clients and administrative UI on port 8080

---

### radarr

- **Purpose:** Archival movie acquisition and management
- **Image:** `lscr.io/linuxserver/radarr:latest`
- **Host Ports:** `7878/tcp`
- **Config / Data Paths:**
  - `/opt/arrstack/radarr:/config`
  - `/mnt/downloads:/downloads`
  - `/mnt/movies:/movies`
- **Depends On:** `prowlarr`, `qbittorrent`
- **Backup Required:** Yes
- **Notes:** Imports and organizes movies into library paths under `/mnt/movies/videos`

---

### sonarr

- **Purpose:** Archival television acquisition and management
- **Image:** `lscr.io/linuxserver/sonarr:latest`
- **Host Ports:** `8989/tcp`
- **Config / Data Paths:**
  - `/opt/arrstack/sonarr:/config`
  - `/mnt/downloads:/downloads`
  - `/mnt/tv:/tv`
- **Depends On:** `prowlarr`, `qbittorrent`
- **Backup Required:** Yes
- **Notes:** Imports and organizes TV content into library paths under `/mnt/tv`

---

### prowlarr

- **Purpose:** Indexer management for Radarr and Sonarr
- **Image:** `lscr.io/linuxserver/prowlarr:latest`
- **Host Ports:** `9696/tcp`
- **Config / Data Paths:**
  - `/opt/arrstack/prowlarr:/config`
- **Depends On:** None
- **Backup Required:** Yes
- **Notes:** Central indexer service for ARR applications

---

### qbittorrent

- **Purpose:** Torrent client for media acquisition
- **Image:** `lscr.io/linuxserver/qbittorrent:latest`
- **Host Ports:** None directly; WebUI available through Gluetun on `18080/tcp`
- **Config / Data Paths:**
  - `/opt/arrstack/qbittorrent:/config`
  - `/mnt/downloads:/downloads`
- **Depends On:** `gluetun`
- **Backup Required:** Yes
- **Notes:** Runs in Gluetun network namespace

---

### gluetun

- **Purpose:** VPN gateway container for torrent traffic
- **Image:** `qmcgaw/gluetun:latest`
- **Host Ports:** `18080/tcp`, `6881/tcp`, `6881/udp`
- **Additional Container Ports:** `8000/tcp`, `8388/tcp`, `8388/udp`, `8888/tcp`
- **Config / Data Paths:**
  - `/opt/arrstack/gluetun:/gluetun`
- **Depends On:** None
- **Backup Required:** Yes
- **Notes:** Hosts qBittorrent WebUI exposure and torrent listen port while enforcing VPN routing

---

### torrent-watchdog

- **Purpose:** Custom automation for stalled torrent recovery
- **Image:** `python:3.12-alpine`
- **Host Ports:** None
- **Config / Data Paths:**
  - `/opt/arrstack/gluetun/watchdog:/app`
- **Depends On:** `gluetun`, `qbittorrent`
- **Backup Required:** Yes
- **Notes:** Reannounces stalled torrents and can trigger VPN rotation through Gluetun control API

---

## Notes

- Host port exposure in this document is limited to ports published to the host system.
- Additional container ports shown in `docker ps` are included where they are visible but not host-published.
- Network communication patterns, VPN routing design, and tunnel architecture are documented separately in `NETWORK_TOPOLOGY.md`.
- Backup relevance in this document refers to whether the container's configuration or state should be preserved as part of the server's recovery model.