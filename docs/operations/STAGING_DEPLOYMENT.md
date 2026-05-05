# Deployment Plan

## Purpose

This document describes the procedure to deploy HARBOR to my personal staging environment.  This document is to be used as a baseline for a general deployment plan document in the future that is universally compatible with a single environmental deploy.

## Server Buildout Plan

### Phase 0 - Prerequisite

HARBOR is an AAR media streaming stack designed to be a turnkey-deploy on a sufficiently equipped home media server.  Minimum Requirements are yet to be determined, but development of this process is being done against two different devices:

- An on-demand virtual machine running 2 cores and 8GB of RAM with no hardware graphics accelerator and 10GB staged mounts
- An always-on hardware production server running a Ryzen 5 3600 with 48GB of ram and 29 total TB of drive space

Regardless of the hardware configuration, the environment must be with the following installs:

- Ubuntu Server
- Docker
- UFW
- git
- a shared service account for the AAR stack

Additionally, the following three mounts must exist:

- /mnt/movies
- /mnt/tv
- /mnt/downloads

### - Phase 1 - Foundation/setup

1. Pull down the HARBOR repository

   Clone the HOMESERVER repository to your service account home directory:

   ```bash
   mkdir ~/workspace && cd ~/workspace && git clone git@github.com:krcdev01/HARBOR.git
   ```

2. Acquire cloudflare token for external access (optional)

   Create a new cloudflare tunnel on cloudflare.  Configure as follows:
   - Tunnel type: Cloudflared
   - Tunnel name: jellyfin-cave-staging
   - Device Operating System: Docker (Cloudflare will provide you with a command to run to pull down cloudflare with your provided token.  Copy this string for later)
   - Subdomain: staging
   - Domain: [EXTERNALURL].com
   - service: http://jellyfin:8096

### - Phase 2 - Media Stack Deployment

1. Copy all of the contents in the infra/srv/ directory over to your server, /srv/ as the destination:

   ```bash
   sudo cp -r ~/workspace/HARBOR/infra/srv/* /srv/
   ```

2. In the /srv/jellyfin directory, rename and modify .env.staging.template, renaming it to .env.staging:

   ```bash
   mv /srv/jellyfin/.env.staging.template /srv/jellyfin/.env.staging && nano /srv/jellyfin/.env.staging
   ```

3. Edit .env.staging with the following changes:
   - JELLYFIN_PUBLISHED_SERVER_URL=[https://staging.[EXTERNALURL].com](https://www.gitlab.com/krcdev01)
   - CLOUDFLARED_TOKEN=[REPLACE_WTIH_TOKEN_FROM_P01S02]

4. Deploy the Media stack.

   ```bash
    docker compose --env-file .env.staging -f compose.yaml -f compose.staging.yaml up -d
    ```

5. Confirm Jellyfin is up and reachable through configured addresses

   - Navigate to your local network server IP and confirm Jellyfin web UI is up.
   - If configured, open a new browser instance and check the configured external URL set up in Cloudflare.

### - Phase 4 - Validation

1. Set up Jellyfin

   Jellyfin requires setting up the following in order to provide any service or value:

   - An Admin User
   - A Content Library
   - A defined region and default language
   - Whether or not to enable external connections

   After this, the application will perform a content scan and metadata update of your configured libraries.  This will complete setup.

2. Play content to confirm jellyfin is behaving as expected

   - It is highly reccomended to test in a web browser first.  This will allow you to turn on playback info on content and observe server playback behavior.
   - Create a non-admin test user and exclude access to one or more libraries to confirm basic permissions are working
   - A variety of content should be played; including content with multiple language and subtitle tracks
   - Force content to transcode by scaling its resolution down to confirm server can perform server transcoding.