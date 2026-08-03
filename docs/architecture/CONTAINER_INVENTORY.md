# Container Inventory

## Overview

The HARBOR media stack is defined by `apps/srv/media/compose.yaml`. Production
and staging apply their environment-specific Compose override to this shared
definition.

## Container Summary

| Container | Image | Interface | Persistent paths | Dependencies | Purpose |
|---|---|---|---|---|---|
| Jellyfin | `jellyfin/jellyfin:10.11` | `8096`, `8920` | `/config`, `/cache` | None | Serves the television and movie libraries |
| Cloudflared | `cloudflare/cloudflared:latest` | Outbound tunnel | None | Jellyfin | Connects Jellyfin to the configured Cloudflare Tunnel |
| Gluetun | `qmcgaw/gluetun:latest` | `18080` for Transmission, `9696` for Prowlarr | Shared forwarded-port volume | None | Provides the VPN network namespace, firewall, and forwarded peer port |
| Transmission | `lscr.io/linuxserver/transmission:latest` | Through Gluetun | `/config` | Gluetun | Downloads releases to the television or movie storage pipeline |
| Transmission Config | `python:3.12-alpine` | None | None | Gluetun, Transmission | Prepares the download directories and applies Transmission session policy |
| Polly | `python:3.12-alpine` | None | None | Gluetun, Transmission | Synchronizes Transmission's peer port with Gluetun's forwarded port |
| Prowlarr | `lscr.io/linuxserver/prowlarr:latest` | `9696` through Gluetun | `/config` | Gluetun | Supplies indexers to Sonarr and Radarr |
| Sonarr | `lscr.io/linuxserver/sonarr:latest` | `8989` | `/config` | Transmission Config | Acquires, imports, and organizes television series |
| Radarr | `lscr.io/linuxserver/radarr:latest` | `7878` | `/config` | Transmission Config | Acquires, imports, and organizes movies |

## Storage and Network Relationships

- Jellyfin mounts `${TV_ROOT}/Videos` at `/tv` and
  `${MOVIES_ROOT}/videos` at `/movies`.
- Transmission mounts `${TV_ROOT}` at `/tv` and `${MOVIES_ROOT}` at
  `/movies` so each download pipeline remains on its corresponding storage.
- Sonarr mounts `${TV_ROOT}` at `/tv`.
- Radarr mounts `${MOVIES_ROOT}` at `/movies`.
- Transmission Config mounts both media roots to prepare `/tv/downloads` and
  `/movies/downloads`.
- Transmission and Prowlarr share Gluetun's network namespace. Their published
  web interfaces and all of their outbound traffic pass through Gluetun.
- Polly shares Gluetun's network namespace and reads its forwarded-port file
  from the `gluetun-port` volume.
- Sonarr and Radarr reach Transmission at `gluetun:9091` and retain their own
  normal stack networking for communication with Prowlarr.

## Environment Differences

Production applies `compose.prod.yaml`, which gives Jellyfin access to the
NVIDIA runtime and GPU.

Staging applies `compose.staging.yaml`, which keeps Jellyfin CPU-only and adds
read-only mounts of the production television and movie libraries for playback
testing.
