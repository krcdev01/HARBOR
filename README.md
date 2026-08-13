# HARBOR

HARBOR is a deployable media streaming and acquisition stack. Its name stands
for Home Archival, Reliable Broadcast & On-Demand Repository.

## Capabilities

HARBOR combines the following services into one Docker Compose deployment:

| Service | Capability |
|---|---|
| Jellyfin | Streams the organized television and movie libraries locally and remotely |
| Cloudflared | Publishes Jellyfin through an authenticated Cloudflare Tunnel |
| Seerr | Provides media discovery, user requests, administrative approval, and availability notifications |
| Gluetun | Routes download-related services through a VPN with firewall enforcement and port forwarding |
| Transmission | Downloads releases selected by Sonarr and Radarr into separate television and movie pipelines |
| Transmission Config | Creates the download directories, applies their ownership and permissions, and configures completed torrents to stop seeding |
| Polly | Keeps Transmission's peer listening port synchronized with the port forwarded by the VPN provider |
| Prowlarr | Provides indexer connectivity to Sonarr and Radarr through the VPN |
| Sonarr | Monitors, acquires, imports, and organizes television series |
| Radarr | Monitors, acquires, imports, and organizes movies |

Transmission and Prowlarr share Gluetun's VPN network namespace. Gluetun's
firewall provides the download-path killswitch, and Polly updates Transmission
after the VPN receives or changes its forwarded peer port.

Television downloads remain on the television filesystem and movie downloads
remain on the movie filesystem. This allows Sonarr and Radarr to import completed
downloads using hardlinks within their respective storage pipelines.

## Deployment Environments

The shared media stack supports two deployment environments:

- **Production** uses the production media mounts and enables NVIDIA GPU access
  for Jellyfin through `compose.prod.yaml`.
- **Staging** runs Jellyfin without the NVIDIA runtime and adds read-only mounts
  of the production libraries for validation through `compose.staging.yaml`.

Each environment uses its own environment file for media paths, the shared
service identity, Cloudflare credentials, VPN credentials, and runtime script
locations.

## Requirements

A deployment host requires:

- Ubuntu Server
- Docker Engine and the Docker Compose plugin
- Git
- UFW
- `/dev/net/tun` access for Gluetun
- Writable television and movie storage mounts
- VPN provider credentials with port-forwarding support
- A Cloudflare Tunnel token for remote Jellyfin and Seerr access

Production also requires NVIDIA drivers and the NVIDIA Container Toolkit.
Staging requires read-only access to the production Samba shares used for
playback validation.

## Repository Layout

| Path | Purpose |
|---|---|
| `apps/srv/media` | Shared Compose stack, environment templates, and production and staging overrides |
| `infra/srv/polly` | Polly runtime script and unit tests |
| `infra/srv/transmission` | Transmission startup configuration script |
| `docs/architecture` | Container and filesystem architecture |
| `docs/operations` | Deployment, startup, and shutdown procedures |

The `srv` paths in the repository correspond to files installed beneath `/srv`
on the target server.

## Deploy HARBOR

Clone the repository onto the target server:

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone git@github.com:krcdev01/HARBOR.git
cd HARBOR
```

Then follow the complete ordered procedure for the target environment:

- [Staging deployment](docs/operations/STAGING_DEPLOYMENT.md)
- [Production deployment](docs/operations/PRODUCTION_DEPLOYMENT.md)

Use the documented procedure from beginning to end. Each runbook covers host
validation, repository installation, environment configuration, stack startup,
container validation, storage access, VPN routing, and application connectivity
for its environment.

## Documentation

- [Contributing](CONTRIBUTING.md)
- [Applications](apps/README.md)
- [Infrastructure](infra/README.md)
- [Container inventory](docs/architecture/CONTAINER_INVENTORY.md)
- [Filesystem layout](docs/architecture/FILESYSTEM_LAYOUT.md)
- [Data persistence requirements](docs/architecture/DATA_PERSISTENCE_REQUIREMENTS.md)
- [Start procedure](docs/operations/START_PROCEDURE.md)
- [Shutdown procedure](docs/operations/SHUTDOWN_PROCEDURE.md)
- [Secrets management](docs/operations/SECRETS.md)

## Support

Send support questions to [krcdev01@gmail.com](mailto:krcdev01@gmail.com).
