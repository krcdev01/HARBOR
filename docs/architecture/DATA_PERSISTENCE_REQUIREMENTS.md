# Data Persistence Requirements

## Purpose

This document identifies the HARBOR data required to preserve the deployed
media stack across container recreation, host recovery, or migration. It also
identifies runtime data that can be regenerated from the repository or rebuilt
by the applications.

## Persistence Summary

| Data | Host location | Persistence requirement |
|---|---|---|
| Jellyfin configuration | `${MEDIA_CONFIG_ROOT}/jellyfin/config` | Required |
| Jellyfin cache | `${MEDIA_CONFIG_ROOT}/jellyfin/cache` | Rebuildable |
| Transmission configuration and queue state | `${MEDIA_CONFIG_ROOT}/transmission` | Required |
| Prowlarr configuration and database | `${MEDIA_CONFIG_ROOT}/prowlarr` | Required |
| Sonarr configuration and database | `${MEDIA_CONFIG_ROOT}/sonarr` | Required |
| Radarr configuration and database | `${MEDIA_CONFIG_ROOT}/radarr` | Required |
| Television library | `${TV_ROOT}/Videos` | Required |
| Movie library | `${MOVIES_ROOT}/videos` | Required |
| Active television downloads | `${TV_ROOT}/downloads` | Operational |
| Active movie downloads | `${MOVIES_ROOT}/downloads` | Operational |
| Deployment environment file | `/srv/media/.env.prod` or `/srv/media/.env.staging` | Required secret configuration |
| Gluetun forwarded-port volume | Docker volume `gluetun-port` | Ephemeral |
| Polly and Transmission Config scripts | `/srv/polly`, `/srv/transmission-config` | Repository-managed |
| Compose definitions | `/srv/media/compose*.yaml` | Repository-managed |
| Container images and writable layers | Docker storage | Rebuildable |

`MEDIA_CONFIG_ROOT` defaults to `/srv/media`. `TV_ROOT` and `MOVIES_ROOT` are
defined by the selected deployment environment file.

## Application State

The application configuration directories preserve databases, authentication,
service settings, library definitions, indexer and download-client connections,
history, and application-managed metadata.

Back up these directories:

```text
/srv/media/jellyfin/config
/srv/media/transmission
/srv/media/prowlarr
/srv/media/sonarr
/srv/media/radarr
```

The Jellyfin cache at `/srv/media/jellyfin/cache` can be rebuilt by Jellyfin.
Keeping it may shorten recovery time, but it is not required to reconstruct the
service.

Application state must be captured consistently. Stop the media stack before a
filesystem-level copy so SQLite databases and configuration files are not
copied during an active write.

## Media Libraries

The organized television and movie libraries are primary persistent data:

```text
${TV_ROOT}/Videos
${MOVIES_ROOT}/videos
```

Sonarr and Radarr manage these locations, and Jellyfin serves them. A complete
recovery requires restoring the library paths with the same case and directory
structure expected by the Compose mounts and application databases.

The storage platform may provide its own redundancy or backup implementation.
HARBOR requires the organized libraries to remain available at the paths
selected by `TV_ROOT` and `MOVIES_ROOT`.

## Download State

Transmission writes each acquisition into the corresponding storage pipeline:

```text
${TV_ROOT}/downloads
${MOVIES_ROOT}/downloads
```

These directories can contain active downloads and completed files awaiting
import. Preserving them allows interrupted downloads and pending imports to
resume after recovery. If they are excluded from backup, that work may need to
be downloaded again.

Completed imports may be hardlinked between a download directory and its media
library. Backing up both directory trees can cause backup software to store the
same file data twice unless it preserves hardlinks. The organized media
libraries are the authoritative recovery copy after import.

## Secrets and Environment Configuration

The active environment file contains the paths, common service identity,
Cloudflare token, VPN credentials, and optional Transmission RPC credentials
required by the deployment.

```text
/srv/media/.env.prod
/srv/media/.env.staging
```

Preserve the environment file in a secured backup or retain the credentials in
a separate secrets system from which the file can be reconstructed. Maintain
owner-only mode `600` after restoration. Credential handling and rotation are
defined in `docs/operations/SECRETS.md`.

## Repository-Managed Files

The following deployed files are restored from a clean checkout of this
repository:

```text
/srv/media/compose.yaml
/srv/media/compose.prod.yaml
/srv/media/compose.staging.yaml
/srv/polly/polly.py
/srv/transmission-config/configure.py
```

Environment templates are also repository-managed. They provide the required
variable structure but do not replace the active environment file containing
the deployed values.

## Ephemeral Runtime Data

The following state is recreated during deployment or normal operation:

- Docker container writable layers
- Container images
- The `gluetun-port` volume and its forwarded-port file
- Polly's in-memory record of the last applied port
- Transmission Config container state after its successful one-shot run
- Cloudflared container state
- Jellyfin cache data when the cache is excluded from backup

Gluetun obtains a new forwarded port after reconnecting, and Polly applies that
port to Transmission. The forwarded-port volume is therefore runtime
coordination state rather than recovery data.

## Staging Persistence

Staging keeps its own application configuration, environment file, download
directories, and writable staging libraries. Its additional production-library
mounts are read-only Samba views of storage owned by the production server.
Those mounts are not staging backup sources.

## Recovery Order

Restore persistent HARBOR data in this order:

1. Restore or mount the television and movie storage roots.
2. Restore the organized libraries and any retained download state.
3. Restore the application configuration directories beneath
   `MEDIA_CONFIG_ROOT`.
4. Restore the active environment file with the common service account, its
   group, and mode `600`.
5. Check out the required repository revision and reinstall the Compose files,
   Polly, and Transmission Config.
6. Validate the Compose configuration for the target environment.
7. Start the stack and complete the container and application checks in the
   corresponding deployment procedure.
