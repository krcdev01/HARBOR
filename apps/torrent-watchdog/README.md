# Torrent Watchdog

## Overview

Torrent Watchdog is a Python service that monitors qBittorrent for stalled torrents that are near completion and attempts automated recovery.

The watchdog performs the following actions:

1. Detects torrents that are near completion but stalled.
2. Reannounces stalled torrents to trackers.
3. If repeated reannounce attempts fail, rotates the VPN server via Gluetun.
4. Continues monitoring in a loop.

This service is designed to resolve the known issue where torrents stall at high completion percentages (e.g., 99.9%).

---

## Architecture

This service runs as a Docker container and shares the network stack with the Gluetun VPN container.

Network Mode:
service:gluetun

This allows the watchdog to:
- Access qBittorrent via localhost
- Access Gluetun control API via localhost
- Operate entirely inside the VPN network namespace

---

## Dependencies

The watchdog depends on:

- Gluetun container
- qBittorrent container
- Gluetun HTTP Control Server
- ProtonVPN port forwarding enabled

Environment variables are supplied via `.env`.

---

## Environment Variables

| Variable | Description |
|---------|-------------|
| QB_URL | qBittorrent WebUI URL |
| QB_USERNAME | qBittorrent username |
| QB_PASSWORD | qBittorrent password |
| GLUETUN_CONTROL_URL | Gluetun control API URL |
| LOOP_SECONDS | Monitoring loop interval |
| STALL_MINUTES | Minutes of inactivity before considered stalled |
| NEAR_END_PROGRESS | Progress threshold for near-complete torrents |
| MIN_DOWNLOAD_BPS | Minimum download speed before considered stalled |
| REANNOUNCE_RETRIES | Reannounce attempts before VPN rotation |
| ROTATE_COOLDOWN_MINUTES | Minimum time between VPN rotations |

---

## File Locations

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| /opt/arrstack/gluetun/watchdog | /app | Watchdog script location |

Primary script:
/opt/arrstack/gluetun/watchdog/watchdog.py

State file (inside container):
/tmp/torrent_watchdog_state.json

---

## How It Works

The watchdog loop:

1. Log into qBittorrent API
2. Retrieve torrent list
3. Identify torrents:
   - Progress > NEAR_END_PROGRESS
   - Download speed < MIN_DOWNLOAD_BPS
   - Stalled longer than STALL_MINUTES
4. Reannounce those torrents
5. If the same torrent is stuck repeatedly:
   - Restart Gluetun VPN container via API
6. Wait LOOP_SECONDS
7. Repeat

---

## Redeployment Procedure

To redeploy the watchdog:

1. Copy `watchdog.py` to:
   /opt/arrstack/gluetun/watchdog/

2. Ensure `.env` file contains required environment variables.

3. Start containers:

   docker compose up -d gluetun qbittorrent torrent-watchdog

4. Verify logs:

   docker logs torrent-watchdog

---

## Logs

Logs are available via Docker:

docker logs torrent-watchdog

---

## Purpose

This service exists to automate recovery from stalled torrents and maintain reliable automated downloads without manual intervention.