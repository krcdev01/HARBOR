# SECRETS.md

## Overview

This document defines environment variables and sensitive configuration required by this repository. Values must not be committed.

---

## Gluetun Container

Purpose:
VPN connectivity and torrent network routing.

Required variables:

VPN Credentials
- VPN_SERVICE_PROVIDER
- VPN_TYPE

VPN Account Credentials
- OPENVPN_USER
- OPENVPN_PASSWORD

qBittorrent WebUI Credentials
- QB_USERNAME
- QB_PASSWORD

Gluetun Configuration
- SERVER_COUNTRIES
- FIREWALL
- FIREWALL_INPUT_PORTS

Notes:
- These values must be supplied via environment variables or external `.env` files.
- Files containing these values should be restricted to owner access (600 recommended).

---

## Cloudflared Tunnel

Purpose:
Provides outbound tunnel connectivity.

Required variable:
- CLOUDFLARED_TOKEN

Notes:
- Must not be committed to the repository.
- Should be provided via environment variables or external configuration.

---

## Jellyfin Configuration

Purpose:
Defines externally accessible server URL.

Required variable:
- JELLYFIN_PUBLISHED_SERVER_URL

Notes:
- Not a credential, but treated as sensitive configuration.
- Should not be hardcoded in repository files.
