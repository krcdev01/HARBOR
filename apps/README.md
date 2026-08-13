# Applications

## Purpose

The `apps` directory contains the containerized services that make up HARBOR.
Its layout mirrors the intended deployment beneath `/srv` on the host.

## Directory Layout

```text
apps/
└── srv/
    └── media/
```

| Repository path | Host path | Purpose |
|---|---|---|
| `apps/srv/media` | `/srv/media` | Media streaming, acquisition, organization, and remote-access stack |

## Media Stack

`apps/srv/media` defines a shared Docker Compose stack with production and
staging overrides.

| Service | Purpose |
|---|---|
| Jellyfin | Serves the organized television and movie libraries |
| Cloudflared | Connects Jellyfin to its configured Cloudflare Tunnel |
| Seerr | Accepts user requests, manages approval, submits approved media to Sonarr or Radarr, and reports availability |
| Gluetun | Provides the VPN network namespace and firewall for download-related traffic |
| Transmission | Downloads television and movie releases selected by Sonarr and Radarr |
| Polly | Synchronizes Transmission's peer port with the port forwarded by the VPN provider |
| Prowlarr | Supplies indexers to Sonarr and Radarr through the VPN connection |
| Sonarr | Monitors, acquires, imports, and organizes television series |
| Radarr | Monitors, acquires, imports, and organizes movies |
| Transmission Config | Applies Transmission session policy and prepares the television and movie download directories during startup |

Transmission, Polly, and Prowlarr share Gluetun's network namespace. Sonarr
and Radarr communicate with Transmission through Gluetun while retaining
direct access to their respective media storage paths. Seerr uses the stack's
default Docker network and communicates with Jellyfin, Sonarr, and Radarr by
service name.

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Defines the shared services, ports, networks, storage mounts, startup dependencies, and persistent Docker volume |
| `compose.prod.yaml` | Adds NVIDIA runtime and GPU access for the production Jellyfin service |
| `compose.staging.yaml` | Keeps Jellyfin CPU-only and adds read-only production-library mounts for staging validation |
| `.env.prod.template` | Lists the production paths, service identity, tunnel, VPN, Polly, and Transmission configuration variables |
| `.env.staging.template` | Lists the equivalent staging variables and staging-specific published Jellyfin URL |
| `.gitignore` | Excludes deployed environment files from source control |

## Deployment

Copy the contents of `apps/srv/media` to `/srv/media` on the target host. Create
the applicable environment file from its template and replace its placeholder
values with the target environment's paths and credentials.

Start production with:

```bash
cd /srv/media
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d
```

Start staging with:

```bash
cd /srv/media
docker compose --env-file .env.staging -f compose.yaml -f compose.staging.yaml up -d
```

The media stack mounts the Polly and Transmission configuration scripts from
the host paths selected by `POLLY_ROOT` and `TRANSMISSION_CONFIG_ROOT`. Their
repository sources are `infra/srv/polly/polly.py` and
`infra/srv/transmission/configure.py`.
