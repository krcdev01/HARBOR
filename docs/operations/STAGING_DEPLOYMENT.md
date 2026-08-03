# Deployment Plan

## Purpose

This document describes the ordered procedure used to deploy HARBOR to the
personal staging environment. The staging server validates repository changes
before they are deployed to production.

## Server Buildout Plan

### Phase 0 - Prerequisites

The staging environment requires:

- Ubuntu Server
- Docker Engine and the Docker Compose plugin
- UFW
- Git
- One deployment account identity shared by the HARBOR services for filesystem access
- `/dev/net/tun` for Gluetun
- A writable television mount at `/mnt/tv`
- A writable movie mount at `/mnt/movies`

The staging override also expects the production Samba shares at:

- `/mnt/prod-tv`
- `/mnt/prod-movies`

These shares must be mounted with credentials that provide read-only access to
production content. The staging override maps the following folders into
Jellyfin:

```text
/mnt/prod-tv/Videos
/mnt/prod-movies/videos
```

Before deployment, confirm the host prerequisites:

```bash
docker --version
docker compose version
git --version
ls -l /dev/net/tun
findmnt /mnt/tv
findmnt /mnt/movies
findmnt /mnt/prod-tv
findmnt /mnt/prod-movies
```

Do not continue until Docker is available, `/dev/net/tun` exists, and each
required mount resolves to its expected source.

### Phase 1 - Foundation Setup

1. Pull down the HARBOR repository.

   Create the workspace and clone the repository if it is not already present:

   ```bash
   mkdir -p ~/workspace
   cd ~/workspace
   git clone git@github.com:krcdev01/HARBOR.git
   ```

   For an existing staging checkout, update its current branch:

   ```bash
   cd ~/workspace/HARBOR
   git pull --ff-only
   git status --short
   ```

   Review and resolve any working-tree changes before continuing.

2. Acquire the Cloudflare token for staging external access.

   Create or select the staging Cloudflare Tunnel and configure:

   - Tunnel type: Cloudflared
   - Tunnel name: `jellyfin-cave-staging`
   - Device operating system: Docker
   - Subdomain: `staging`
   - Domain: the external HARBOR domain
   - Service: `http://jellyfin:8096`

   Retain the generated tunnel token for the staging environment file.

### Phase 2 - Media Stack Installation

1. Create the application and supporting-script directories.

   ```bash
   sudo install -d -m 0755 \
     /srv/media \
     /srv/polly \
     /srv/transmission-config
   ```

2. Install the shared media stack and staging override.

   ```bash
   sudo cp -a ~/workspace/HARBOR/apps/srv/media/. /srv/media/
   ```

   This copies `compose.yaml`, `compose.staging.yaml`, the environment template,
   and the related deployment files, including hidden files.

3. Install Polly.

   ```bash
   sudo install -m 0755 \
     ~/workspace/HARBOR/infra/srv/polly/polly.py \
     /srv/polly/polly.py
   ```

4. Install Transmission Config.

   ```bash
   sudo install -m 0755 \
     ~/workspace/HARBOR/infra/srv/transmission/configure.py \
     /srv/transmission-config/configure.py
   ```

5. Create the staging environment file on a new deployment.

   If `/srv/media/.env.staging` does not already exist, create it from the
   template:

   ```bash
   sudo cp /srv/media/.env.staging.template /srv/media/.env.staging
   sudo chown serveradmin:serveradmin /srv/media/.env.staging
   sudo chmod 600 /srv/media/.env.staging
   ```

6. Edit the staging environment file.

   ```bash
   sudo nano /srv/media/.env.staging
   ```

   Confirm the deployment account IDs before assigning `PUID` and `PGID`:

   ```bash
   id -u serveradmin
   id -g serveradmin
   ```

   Use these same numeric IDs throughout the environment file. Transmission,
   Transmission Config, Prowlarr, Sonarr, and Radarr must use the same account
   identity so that downloaded files can be read, imported, hardlinked, and
   removed across the stack.

   Set every required value:

   ```dotenv
   TZ=America/New_York
   TV_ROOT=/mnt/tv
   MOVIES_ROOT=/mnt/movies
   PUID=1000
   PGID=1000
   MEDIA_CONFIG_ROOT=/srv/media

   JELLYFIN_PUBLISHED_SERVER_URL=https://staging.[EXTERNALURL].com
   CLOUDFLARED_TOKEN=replace-with-staging-cloudflare-tunnel-token

   VPN_SP=protonvpn
   OPENVPN_USER=replace-with-openvpn-username
   OPENVPN_PASSWORD=replace-with-openvpn-password

   POLLY_ROOT=/srv/polly
   POLLY_POLL_SECONDS=10
   TRANSMISSION_CONFIG_ROOT=/srv/transmission-config
   ```

7. Validate the staging Compose configuration.

   ```bash
   cd /srv/media

   sudo docker compose \
     --env-file .env.staging \
     -f compose.yaml \
     -f compose.staging.yaml \
     config --quiet
   ```

   Do not continue if Compose reports a configuration error.

8. Pull the container images.

   ```bash
   sudo docker compose \
     --env-file .env.staging \
     -f compose.yaml \
     -f compose.staging.yaml \
     pull
   ```

   This installs the images for Jellyfin, Cloudflared, Gluetun, Transmission,
   Transmission Config, Polly, Prowlarr, Sonarr, and Radarr.

9. Stop an existing staging stack.

   ```bash
   sudo docker compose \
     --env-file .env.staging \
     -f compose.yaml \
     -f compose.staging.yaml \
     down
   ```

   Do not use `--volumes`.

10. Start the staging stack.

    ```bash
    sudo docker compose \
      --env-file .env.staging \
      -f compose.yaml \
      -f compose.staging.yaml \
      up -d
    ```

### Phase 3 - Container Validation

1. Confirm the state of every container.

   ```bash
   cd /srv/media

   sudo docker compose \
     --env-file .env.staging \
     -f compose.yaml \
     -f compose.staging.yaml \
     ps -a
   ```

   Confirm:

   - Gluetun becomes healthy.
   - Jellyfin becomes healthy.
   - Transmission, Polly, Prowlarr, Sonarr, Radarr, and Cloudflared remain up.
   - Transmission Config finishes with `Exited (0)`.

2. Confirm that Gluetun connected and obtained a forwarded peer port.

   ```bash
   sudo docker logs gluetun 2>&1 \
     | grep -E 'port forwarded|allowed input port|writing port file' \
     | tail -20
   ```

   The log must show a forwarded port, a matching firewall rule on `tun0`, and
   the forwarded-port file being written.

3. Confirm that Transmission and Prowlarr use Gluetun's network namespace.

   ```bash
   sudo docker inspect --format '{{.HostConfig.NetworkMode}}' transmission
   sudo docker inspect --format '{{.HostConfig.NetworkMode}}' prowlarr
   ```

   Both results must begin with `container:`.

4. Confirm that Transmission Config completed successfully.

   ```bash
   sudo docker logs transmission-config
   ```

   Confirm the download directories exist:

   ```bash
   ls -ld /mnt/tv/downloads /mnt/movies/downloads
   ```

5. Confirm that Polly synchronized Transmission's peer port.

   ```bash
   sudo docker logs --tail=50 polly
   sudo docker exec gluetun cat /tmp/gluetun/forwarded_port
   ```

   The port reported by Polly must match the value in Gluetun's forwarded-port
   file.

6. Confirm write access to the staging download locations.

   First confirm that the LinuxServer containers resolved the shared identity
   to the configured UID and GID:

   ```bash
   sudo docker exec transmission id abc
   sudo docker exec prowlarr id abc
   sudo docker exec sonarr id abc
   sudo docker exec radarr id abc
   ```

   Each result must report the same configured UID and GID. Then run the
   storage checks using that identity:

   ```bash
   sudo docker exec --user 1000:1000 transmission \
     sh -c 'test -w /tv/downloads && test -w /movies/downloads'

   sudo docker exec --user 1000:1000 sonarr \
     sh -c 'test -w /tv && test -w /tv/downloads'

   sudo docker exec --user 1000:1000 radarr \
     sh -c 'test -w /movies && test -w /movies/downloads'
   ```

   Each command must exit without output and return status `0`.

### Phase 4 - Application Connectivity

1. Confirm that each local interface is reachable.

   Open each address from a system on the staging network:

   ```text
   Jellyfin:     http://stageserver:8096
   Transmission: http://stageserver:18080
   Prowlarr:     http://stageserver:9696
   Sonarr:       http://stageserver:8989
   Radarr:       http://stageserver:7878
   ```

   Complete initial authentication where prompted and confirm that each
   interface can be reopened with the configured credentials.

2. Configure Sonarr to communicate with Transmission.

   In Sonarr, open `Settings → Download Clients`, add Transmission, and set:

   ```text
   Host: gluetun
   Port: 9091
   URL Base: /transmission/
   Category: blank
   Directory: /tv/downloads
   ```

   Test the connection and save it only after the test succeeds.

3. Configure Radarr to communicate with Transmission.

   In Radarr, open `Settings → Download Clients`, add Transmission, and set:

   ```text
   Host: gluetun
   Port: 9091
   URL Base: /transmission/
   Category: blank
   Directory: /movies/downloads
   ```

   Test the connection and save it only after the test succeeds.

4. Configure Prowlarr to communicate with Sonarr.

   Retrieve the Sonarr API key from `Settings → General`. In Prowlarr, open
   `Settings → Apps`, add Sonarr, and set its service address to:

   ```text
   http://sonarr:8989
   ```

   Enter the Sonarr API key, test the connection, and save it only after the
   test succeeds.

5. Configure Prowlarr to communicate with Radarr.

   Retrieve the Radarr API key from `Settings → General`. In Prowlarr, open
   `Settings → Apps`, add Radarr, and set its service address to:

   ```text
   http://radarr:7878
   ```

   Enter the Radarr API key, test the connection, and save it only after the
   test succeeds.

6. Confirm that the staging tunnel reaches Jellyfin.

   Open the staging external URL configured in Cloudflare. Confirm that the
   request reaches the staging Jellyfin interface.

### Phase 5 - Completion

The staging deployment is complete only after:

1. Every long-running container is up.
2. Gluetun is healthy and has a forwarded port.
3. Transmission and Prowlarr use Gluetun's network namespace.
4. Transmission Config exits successfully.
5. Polly synchronizes the forwarded port to Transmission.
6. Transmission, Sonarr, and Radarr can write to their assigned download paths.
7. Sonarr and Radarr successfully test their Transmission connections.
8. Prowlarr successfully tests its Sonarr and Radarr connections.
9. Each local web interface is reachable.
10. The staging Cloudflare URL reaches Jellyfin.
