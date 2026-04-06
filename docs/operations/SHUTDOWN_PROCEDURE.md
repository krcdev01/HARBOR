# Controlled Shutdown Procedure

## Controlled Shutdown Sequence

The shutdown sequence stops services in reverse dependency order to prevent database corruption, incomplete file writes, and network interruption during active operations.

---

### Step 0 — Pre-Shutdown Check
```bash
sudo docker ps
```
What: Lists running containers.  
Why: Confirms system state before shutdown.  
Result: All major containers should be visible and running.

---

### Step 1 — Stop the ARR applications
```bash
sudo docker stop radarr sonarr prowlarr
```
What: Stops the ARR management services.  
Why: Prevents new downloads, imports, or file moves.  
Result: ARR containers exit cleanly.

---

### Step 2 — Stop the torrent management helper
```bash
sudo docker stop torrent-watchdog
```
What: Stops the watchdog container.  
Why: Prevents automation from manipulating qBittorrent or VPN during shutdown.  
Result: Watchdog exits.

---

### Step 3 — Stop qBittorrent
```bash
sudo docker stop qbittorrent
```
What: Stops the torrent client.  
Why: Ensures torrent state and partial files are properly written before the network shuts down.  
Result: qBittorrent exits cleanly.

---

### Step 4 — Stop the VPN container
```bash
sudo docker stop gluetun
```
What: Stops the VPN container.  
Why: Network layer can be safely removed after the torrent client exits.  
Result: VPN container stops.

---

### Step 5 — Stop media services
```bash
sudo docker stop jellyfin
```
What: Stops the Jellyfin media server.  
Why: Prevents database writes during shutdown.  
Result: Jellyfin exits cleanly.

---

### Step 6 — Stop external access
```bash
sudo docker stop cloudflared
```
What: Stops the Cloudflare tunnel.  
Why: Prevents inbound connections during shutdown.  
Result: External access disabled.

---

### Step 7 — Stop DNS service
```bash
sudo docker stop pihole
```
What: Stops the Pi-hole DNS service.  
Why: DNS should remain available until all other services are stopped.  
Result: DNS service stops.

---

### Step 8 — Verify all containers stopped
```bash
sudo docker ps
```
What: Confirms shutdown completion.  
Why: Ensures no containers remain running.  
Result: No containers listed.

---

### Step 9 — Shut down host
```bash
sudo shutdown now
```
What: Powers down the server.  
Why: Safe shutdown after all services have stopped.  
Result: Server powers off.
