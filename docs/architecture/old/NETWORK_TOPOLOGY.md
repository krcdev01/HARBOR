# Network Topology

## Overview

This document describes how services on the server communicate, which services are exposed to the host network, which services are internal-only, and how traffic is routed between containers and external networks.

The system is composed of several functional service groups:

- Media services
- Media automation services
- Torrent services (VPN-routed)
- Infrastructure services
- Remote access tunnel

These services are connected through a combination of:

- Host-published ports
- Docker bridge networks
- Shared network namespaces
- Outbound tunnel connectivity

---

## Host Port Exposure

The following services publish ports directly to the host system:

| Service | Host Port | Protocol | Purpose |
|--------|-----------|----------|---------|
| Jellyfin | 8096 | TCP | Local web interface |
| Jellyfin | 8920 | TCP | HTTPS interface |
| Radarr | 7878 | TCP | Web interface |
| Sonarr | 8989 | TCP | Web interface |
| Prowlarr | 9696 | TCP | Web interface |
| Gluetun | 18080 | TCP | qBittorrent WebUI |
| Gluetun | 6881 | TCP/UDP | Torrent listen port |

All other containers operate without direct host port exposure.

---

## Internal-Only Services

The following containers do not publish ports directly to the host:

| Service | Access Method |
|--------|---------------|
| qBittorrent | Through Gluetun |
| torrent-watchdog | Internal container communication |
| cloudflared | Outbound tunnel only |

These services are intentionally isolated from direct host exposure.

---

## VPN Routing Model (Torrent Stack)

The torrent stack is designed so that all torrent traffic is routed through a VPN container.

Traffic Flow:

Internet ↔ VPN Provider ↔ Gluetun ↔ qBittorrent

Key characteristics:

- qBittorrent shares the network namespace of Gluetun
- Torrent traffic cannot exit the host except through the VPN tunnel
- A killswitch prevents traffic leakage if the VPN connection drops
- The qBittorrent WebUI is exposed through Gluetun on port 18080
- Torrent listen port 6881 is exposed through Gluetun for inbound peer connections
- torrent-watchdog communicates internally with qBittorrent and Gluetun

---

## Remote Access Model

Remote access is provided through a Cloudflare Tunnel.

Traffic Flow:

Remote Client → Cloudflare → Cloudflare Tunnel → cloudflared container → internal service

Characteristics:

- No inbound firewall ports are required for remote access
- cloudflared establishes outbound-only connections
- Selected internal services are exposed through the tunnel

---

## Docker Network Layout

The system uses a user-defined Docker network:

| Network | Purpose |
|--------|---------|
| arrnet | Shared network for ARR stack and Gluetun |

Network behavior:

- ARR services communicate with each other over arrnet
- qBittorrent and torrent-watchdog use Gluetun's network namespace
- Jellyfin operates with direct host port bindings
- cloudflared connects outbound to Cloudflare

---

## Service Dependency Relationships

The following table describes service startup dependencies:

| Service | Depends On |
|--------|------------|
| gluetun | none |
| qbittorrent | gluetun |
| torrent-watchdog | qbittorrent |
| prowlarr | none |
| sonarr | prowlarr, qbittorrent |
| radarr | prowlarr, qbittorrent |
| jellyfin | none |
| cloudflared | jellyfin |
| pihole | none |

These dependencies determine the controlled startup and shutdown order of the system.

---

## Summary

The network topology is designed with the following principles:

- Media and management services are accessible on the local network via host ports
- Torrent traffic is isolated behind a VPN container
- Remote access is provided through an outbound tunnel rather than open inbound ports
- Internal automation services are not exposed to the host network
- Service dependencies dictate startup and shutdown order
