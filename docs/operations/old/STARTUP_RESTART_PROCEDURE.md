# Controlled Startup/Restart Procedure

## Controlled Startup/Restart Sequence

The startup sequence starts services in dependency order to ensure that network infrastructure, download services, automation services, and media services initialize correctly before external access is enabled.

---

### Step 1 — Start DNS infrastructure
```bash
sudo docker start pihole
```
What: Starts Pi-hole DNS service.  
Why: DNS must be available before other services attempt outbound connections.  
Result: DNS becomes available.

---

### Step 2 — Start VPN container
```bash
sudo docker start gluetun
```
What: Starts VPN container.  
Why: Torrent services require VPN network namespace.  
Result: VPN initializes and establishes connection.

---

### Step 3 — Start torrent client
```bash
sudo docker start qbittorrent
```
What: Starts torrent client.  
Why: Requires VPN container to be running.  
Result: Torrent client becomes operational.

---

### Step 4 — Start torrent automation
```bash
sudo docker start torrent-watchdog
```
What: Starts torrent watchdog service.  
Why: Requires qBittorrent to be running.  
Result: Watchdog begins monitoring torrents.

---

### Step 5 — Start indexer service
```bash
sudo docker start prowlarr
```
What: Starts Prowlarr indexer service.  
Why: Provides indexers for Sonarr and Radarr.  
Result: Indexer service becomes available.

---

### Step 6 — Start TV automation
```bash
sudo docker start sonarr
```
What: Starts Sonarr.  
Why: Requires indexers and torrent client availability.  
Result: Sonarr begins monitoring and importing TV content.

---

### Step 7 — Start movie automation
```bash
sudo docker start radarr
```
What: Starts Radarr.  
Why: Final ARR service in dependency chain.  
Result: Radarr begins monitoring and importing movies.

---

### Step 8 — Start media service
```bash
sudo docker start jellyfin
```
What: Starts Jellyfin media server.  
Why: Media services should start after automation services.  
Result: Media server becomes available.

---

### Step 9 — Enable external access
```bash
sudo docker start cloudflared
```
What: Starts Cloudflare tunnel.  
Why: External access should only be enabled after the system is fully operational.  
Result: Remote access becomes available.

---

### Step 10 — Verify system state
```bash
sudo docker ps
```
What: Lists running containers.  
Why: Confirms the entire stack has started successfully.  
Result: All containers show as running.
