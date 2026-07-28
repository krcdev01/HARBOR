# Deployment Plan

## Purpose

This document describes the procedure to deploy HARBOR to my personal production environment.  This document is to be used as a baseline for a general deployment plan document in the future that is universally compatible with a single environmental deploy.

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

### - Phase 1 - Foundation/setup

1. Pull down the HARBOR repository

   Make the workspace directory if it does not yet exist, then clone the HOMESERVER repository to your service account home directory:

   ```bash
   mkdir ~/workspace
   
   cd ~/workspace && git clone git@github.com:krcdev01/HARBOR.git
   ```

2. Acquire cloudflare token for external access (optional)

   Create a new cloudflare tunnel on cloudflare.  Configure as follows:
   - Tunnel type: Cloudflared
   - Tunnel name: jellyfin-cave-staging
   - Device Operating System: Docker (Cloudflare will provide you with a command to run to pull down cloudflare with your provided token.  Copy this string for later)
   - Subdomain: staging
   - Domain: [EXTERNALURL].com
   - service: [jellyfin](http://jellyfin:8096)

   **Note: If this step has previously been done on a prior deployment and the cloudflare token was lost, the prior key must be deleted and recreated using the steps above.  Otherwise, you can retrieve the token and skip this step.**

### - Phase 2 - Media Stack Deployment

1. Copy all of the contents in the infra/srv/ directory over to your server, /srv/ as the destination:

   ```bash
   sudo cp -r ~/workspace/HARBOR/infra/srv/* /srv/
   ```

2. In the /srv/media directory, rename and modify .env.staging.template, renaming it to .env.staging:

   ```bash
   sudo mv /srv/media/.env.prod.template /srv/media/.env.prod && sudo nano /srv/media/.env.prod
   ```

3. Edit .env.staging with the following changes:
   - TZ-America/New_York
   - JELLYFIN_PUBLISHED_SERVER_URL=[https://[EXTERNALURL].com][l1]
   - CLOUDFLARED_TOKEN=[REPLACE_WTIH_TOKEN_FROM_P01S02]

4. Deploy the Media stack.

   ```bash
    docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d
    ```

5. Confirm Jellyfin is up and reachable through configured addresses

   - Navigate to your local network server IP and confirm Jellyfin web UI is up.
   - If configured, open a new browser instance and check the configured external URL set up in Cloudflare.

6. Confirm Sonarr is up and reachable

   - Navigate to Sonarr at the server's local network address on port `8989`.
   - Confirm that the Sonarr web interface loads.
   - Complete the initial authentication setup if prompted and confirm that you can log in.

7. Confirm Radarr is up and reachable

   - Navigate to Radarr at the server's local network address on port 7878.
   - Confirm that the Radarr web interface loads.
   - Complete the initial authentication setup if prompted and confirm that you can log in.

### - Phase 3 - Validation

1. Set up Jellyfin

   Jellyfin requires setting up the following in order to provide any service or value:

   - An Admin User
   - A Content Library
   - A defined region and default language
   - Whether or not to enable external connections

   After this, the application will perform a content scan and metadata update of your configured libraries.  This will complete setup.

2. Perform basic Sonarr setup

   Sonarr requires initial authentication and library configuration before it can manage existing television content.

   - Open Sonarr using the server's local network address on port `8989`.
   - Configure the Sonarr authentication username and password if this was not completed during deployment.
   - Log in using the configured credentials.
   - Add the root folders containing the television libraries that Sonarr will manage.
   - Import the existing series from those root folders.
   - Confirm that Sonarr can see the expected series and access their files.

   Automated download clients, indexers, quality profiles, and acquisition rules are configured separately and are outside the scope of this initial deployment procedure.

3. Perform basic Radarr setup

   Radarr requires initial authentication and library configuration before it can manage existing movie content.

   - Open Radarr using the server's local network address on port 7878.
   - Configure the Radarr authentication username and password if this was not completed during deployment.
   - Log in using the configured credentials.
   - Add the root folders containing the movie libraries that Radarr will manage.
   - Import the existing movies from those root folders.
   - Confirm that Radarr can see the expected movies and access their files.
   - Open Settings → Metadata.
   - Add and enable the Kodi/Emby metadata consumer.
   - Enable movie metadata and movie images so that Radarr writes local NFO and artwork files alongside the movie files.
   - Run a refresh and scan against the imported movies.
   - Confirm that Radarr creates the expected NFO, poster, fanart, and related metadata files.

   Automated download clients, indexers, quality profiles, and acquisition rules are configured separately and are outside the scope of this initial deployment procedure

4. Play content to confirm jellyfin is behaving as expected

   - It is highly reccomended to test in a web browser first.  This will allow you to turn on playback info on content and observe server playback behavior.
   - Create a non-admin test user and exclude access to one or more libraries to confirm basic permissions are working
   - A variety of content should be played; including content with multiple language and subtitle tracks
   - Force content to transcode by scaling its resolution down to confirm server can perform server transcoding.

5. Cleanup

   Remove the staging workspace copy of the repository:

   ```shell
   rm -rf ~/workspace/HARBOR
   ```

[l1]: https://www.github.com/krcdev01
