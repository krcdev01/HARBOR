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

### Step 1 — Stop the Jellyfin Provider Stack

    ```bash
    cd /srv/jellyfin && docker compose --env-file /srv/jellyfin/.env.staging -f compose.yaml -f compose.staging.yaml stop
    ```

What: Stops the Jellyfin Provider stack.  
Why: Safely stops the Jellyfin application to allow for backups and diagnostics without risk of data corruption.  Disables external access by shutting down Cloudflare tunnel.
Result: Jellyfin and Cloudflare exit cleanly

---

### Step 2 — Verify all containers stopped

    ```bash
    sudo docker ps
    ```

What: Confirms shutdown completion.  
Why: Ensures no containers remain running.  
Result: No containers listed.

---

### Step 3 — Shut down host

    ```bash
    sudo shutdown -h now
    ```

What: Powers down the server.  
Why: Safe shutdown after all services have stopped.  
Result: Server powers off.