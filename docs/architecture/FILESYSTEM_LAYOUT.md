# Filesystem Layout

## Repository Layout

HARBOR organizes deployable files beneath a repository path that identifies
their destination area on the server. Files below a `srv` directory are
installed beneath `/srv` on the target host.

```text
HARBOR/
├── apps/
│   └── srv/
│       └── media/
│           ├── .env.prod.template
│           ├── .env.staging.template
│           ├── .gitignore
│           ├── compose.yaml
│           ├── compose.prod.yaml
│           └── compose.staging.yaml
├── infra/
│   └── srv/
│       ├── polly/
│       │   ├── polly.py
│       │   └── test_polly.py
│       └── transmission/
│           └── configure.py
└── docs/
    ├── architecture/
    └── operations/
```

## Deployment Mapping

| Repository path | Server destination | Purpose |
|---|---|---|
| `apps/srv/media/` | `/srv/media/` | Docker Compose definitions, environment templates, and persistent application configuration root |
| `infra/srv/polly/polly.py` | `/srv/polly/polly.py` | Runtime script that synchronizes Transmission's peer port |
| `infra/srv/transmission/configure.py` | `/srv/transmission-config/configure.py` | One-shot Transmission configuration script mounted by the media stack |

The files under `apps` define the deployed application stack. The files under
`infra` support that stack at runtime and are copied to the host paths mounted
by Compose.

## Deployed Media Stack

The `/srv/media` directory contains the selected environment file and the
Compose files used to operate the stack:

```text
/srv/media/
├── .env.prod                 # production only
├── .env.staging              # staging only
├── compose.yaml
├── compose.prod.yaml
├── compose.staging.yaml
├── jellyfin/
├── prowlarr/
├── radarr/
├── seerr/
├── sonarr/
└── transmission/
```

The application configuration directories are bind-mounted into their
corresponding containers through `MEDIA_CONFIG_ROOT=/srv/media`.

## Supporting Runtime Files

```text
/srv/
├── polly/
│   └── polly.py
└── transmission-config/
    └── configure.py
```

`POLLY_ROOT` and `TRANSMISSION_CONFIG_ROOT` select these host directories for
the mounts declared in `compose.yaml`.

## Media Mounts

The repository does not encode the production server's physical disk layout.
The environment file supplies the host media roots used by Compose:

```dotenv
TV_ROOT=/mnt/tv
MOVIES_ROOT=/mnt/movies
```

These roots provide the following paths to the stack:

| Host path | Use |
|---|---|
| `${TV_ROOT}/Videos` | Television library served by Jellyfin and managed by Sonarr |
| `${TV_ROOT}/downloads` | Television download pipeline shared by Transmission and Sonarr |
| `${MOVIES_ROOT}/videos` | Movie library served by Jellyfin and managed by Radarr |
| `${MOVIES_ROOT}/downloads` | Movie download pipeline shared by Transmission and Radarr |

The staging override additionally mounts the production Samba shares from
`/mnt/prod-tv` and `/mnt/prod-movies` into Jellyfin as read-only libraries.
