# Production Deployment Plan

## Purpose

This document describes the ordered procedure used to deploy HARBOR to the
production server.

## Server Buildout Plan

### Phase 0 - Prerequisites

The production environment requires:

- Ubuntu Server
- Docker Engine and the Docker Compose plugin
- Git
- UFW
- NVIDIA drivers and the NVIDIA Container Toolkit
- One deployment account identity shared by the HARBOR services for filesystem access
- `/dev/net/tun` for Gluetun
- A writable television mount at `/mnt/tv`
- A writable movie mount at `/mnt/movies`

Before deployment, confirm the host prerequisites:

```bash
docker --version
docker compose version
git --version
nvidia-smi
docker info | grep -i nvidia
ls -l /dev/net/tun
findmnt /mnt/tv
findmnt /mnt/movies
```

Do not continue until Docker is available, the NVIDIA runtime is registered,
`/dev/net/tun` exists, and both production media mounts resolve to their
expected storage.

### Phase 1 - Foundation Setup

1. Pull down the HARBOR repository.

   Create the workspace and clone the repository if it is not already present:

   ```bash
   mkdir -p ~/workspace
   cd ~/workspace
   git clone git@github.com:krcdev01/HARBOR.git
   ```

   For an existing production checkout, update the `main` branch:

   ```bash
   cd ~/workspace/HARBOR
   git switch main
   git pull --ff-only
   git status --short
   ```

   Review and resolve any working-tree changes before continuing.

2. Acquire the Cloudflare token for production external access.

   Create or select the production Cloudflare Tunnel and configure:

   - Tunnel type: Cloudflared
   - Tunnel name: the production Jellyfin tunnel
   - Device operating system: Docker
   - Hostname: the production HARBOR hostname
   - Service: `http://jellyfin:8096`

   Add a separate public hostname for the production request interface with
   the service set to `http://seerr:5055`.

   Retain the generated tunnel token for the production environment file.

### Phase 2 - Media Stack Installation

1. Create the application and supporting-script directories.

   ```bash
   sudo install -d -m 0755 \
     /srv/media \
     /srv/polly \
     /srv/transmission-config
   ```

2. Install the shared media stack and production override.

   ```bash
   sudo cp -a ~/workspace/HARBOR/apps/srv/media/. /srv/media/
   ```

   This copies `compose.yaml`, `compose.prod.yaml`, the environment template,
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

5. Create the production environment file on a new deployment.

   If `/srv/media/.env.prod` does not already exist, create it from the
   template:

   ```bash
   sudo cp /srv/media/.env.prod.template /srv/media/.env.prod
   sudo chown serveradmin:serveradmin /srv/media/.env.prod
   sudo chmod 600 /srv/media/.env.prod
   ```

6. Edit the production environment file.

   ```bash
   sudo nano /srv/media/.env.prod
   ```

   Confirm the deployment account IDs before assigning `PUID` and `PGID`:

   ```bash
   id -u serveradmin
   id -g serveradmin
   ```

   Use these same numeric IDs throughout the environment file. Seerr,
   Transmission, Transmission Config, Prowlarr, Sonarr, and Radarr must use the
   same account identity. Create Seerr's persistent directory with that
   identity:

   ```bash
   sudo install -d -m 0755 \
     -o "$(id -u serveradmin)" \
     -g "$(id -g serveradmin)" \
     /srv/media/seerr
   ```

   Set every required value:

   ```dotenv
   TZ=America/New_York
   TV_ROOT=/mnt/tv
   MOVIES_ROOT=/mnt/movies
   PUID=1000
   PGID=1000
   MEDIA_CONFIG_ROOT=/srv/media

   JELLYFIN_PUBLISHED_SERVER_URL=https://[EXTERNALURL].com
   CLOUDFLARED_TOKEN=replace-with-production-cloudflare-tunnel-token

   VPN_SP=protonvpn
   OPENVPN_USER=replace-with-openvpn-username
   OPENVPN_PASSWORD=replace-with-openvpn-password

   POLLY_ROOT=/srv/polly
   POLLY_POLL_SECONDS=10
   TRANSMISSION_RPC_USERNAME=
   TRANSMISSION_RPC_PASSWORD=
   TRANSMISSION_CONFIG_ROOT=/srv/transmission-config
   ```

7. Validate the production Compose configuration.

   ```bash
   cd /srv/media

   sudo docker compose \
     --env-file .env.prod \
     -f compose.yaml \
     -f compose.prod.yaml \
     config --quiet
   ```

   Do not continue if Compose reports a configuration error.

8. Pull the container images.

   ```bash
   sudo docker compose \
     --env-file .env.prod \
     -f compose.yaml \
     -f compose.prod.yaml \
     pull
   ```

   This installs the images for Jellyfin, Cloudflared, Seerr, Gluetun,
   Transmission, Transmission Config, Polly, Prowlarr, Sonarr, and Radarr.

9. Stop the existing production stack.

   ```bash
   sudo docker compose \
     --env-file .env.prod \
     -f compose.yaml \
     -f compose.prod.yaml \
     down
   ```

   Do not use `--volumes`.

10. Start the production stack.

    ```bash
    sudo docker compose \
      --env-file .env.prod \
      -f compose.yaml \
      -f compose.prod.yaml \
      up -d
    ```

### Phase 3 - Container Validation

1. Confirm the state of every container.

   ```bash
   cd /srv/media

   sudo docker compose \
     --env-file .env.prod \
     -f compose.yaml \
     -f compose.prod.yaml \
     ps -a
   ```

   Confirm:

   - Gluetun becomes healthy.
   - Jellyfin and Seerr become healthy.
   - Transmission, Polly, Prowlarr, Sonarr, Radarr, and Cloudflared remain up.
   - Transmission Config finishes with `Exited (0)`.

2. Confirm that Jellyfin received NVIDIA GPU access.

   ```bash
   sudo docker exec jellyfin nvidia-smi
   ```

   The command must display the production NVIDIA GPU without reporting a
   runtime or device error.

3. Confirm that Gluetun connected and obtained a forwarded peer port.

   ```bash
   sudo docker logs gluetun 2>&1 \
     | grep -E 'port forwarded|allowed input port|writing port file' \
     | tail -20
   ```

   The log must show a forwarded port, a matching firewall rule on `tun0`, and
   the forwarded-port file being written.

4. Confirm that Transmission and Prowlarr use Gluetun's network namespace.

   ```bash
   sudo docker inspect --format '{{.HostConfig.NetworkMode}}' transmission
   sudo docker inspect --format '{{.HostConfig.NetworkMode}}' prowlarr
   ```

   Both results must begin with `container:`.

5. Confirm that Transmission Config completed successfully.

   ```bash
   sudo docker logs transmission-config
   ```

   Confirm the download directories exist:

   ```bash
   ls -ld /mnt/tv/downloads /mnt/movies/downloads
   ```

6. Confirm that Polly synchronized Transmission's peer port.

   ```bash
   sudo docker logs --tail=50 polly
   sudo docker exec gluetun cat /tmp/gluetun/forwarded_port
   ```

   The port reported by Polly must match the value in Gluetun's forwarded-port
   file.

7. Confirm write access to the production download locations.

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

   Open each address from a system on the production network:

   ```text
   Jellyfin:     http://library:8096
   Seerr:        http://library:5055
   Transmission: http://library:18080
   Prowlarr:     http://library:9696
   Sonarr:       http://library:8989
   Radarr:       http://library:7878
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

6. Configure Seerr.

   Sign in with a Jellyfin administrator account. Connect Seerr to Jellyfin at
   `http://jellyfin:8096`, Sonarr at `sonarr:8989`, and Radarr at
   `radarr:7878`. Select the production Jellyfin libraries, configure the
   intended quality profiles and library root folders, enable service scans and
   automatic searches, and run Seerr's initial library scan.

   Set the Seerr Application URL to its production external hostname. Configure
   ordinary users to request media without automatic approval and reserve
   approval for an administrator or a user with Manage Requests permission.
   Configure and test the required notification agents, including Media
   Available notifications.

7. Confirm the production tunnels reach Jellyfin and Seerr.

   Open the production external URL configured in Cloudflare. Confirm that the
   request reaches the production Jellyfin interface.

   Open the production Seerr URL. Confirm that a Jellyfin user can sign in and
   submit a request for administrative approval.

### Phase 5 - Completion

The production deployment is complete only after:

1. Every long-running container is up.
2. Jellyfin can access the NVIDIA GPU.
3. Gluetun is healthy and has a forwarded port.
4. Transmission and Prowlarr use Gluetun's network namespace.
5. Transmission Config exits successfully.
6. Polly synchronizes the forwarded port to Transmission.
7. Transmission, Sonarr, and Radarr can write to their assigned production paths.
8. Sonarr and Radarr successfully test their Transmission connections.
9. Prowlarr successfully tests its Sonarr and Radarr connections.
10. Seerr connects to Jellyfin, Sonarr, and Radarr; users can submit requests;
    and approved requests enter the correct acquisition pipeline.
11. Each local web interface is reachable.
12. The production Cloudflare URLs reach Jellyfin and Seerr.
