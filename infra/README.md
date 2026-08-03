# Infrastructure

## Purpose

The `infra` directory contains runtime support scripts used by the HARBOR media
stack. Its `srv` layout identifies the server area where these files are
installed.

```text
infra/
└── srv/
    ├── polly/
    │   ├── polly.py
    │   └── test_polly.py
    └── transmission/
        └── configure.py
```

These scripts run in Python containers defined by
`apps/srv/media/compose.yaml`.

## Polly

`infra/srv/polly/polly.py` keeps Transmission's peer listening port synchronized
with the port forwarded by Gluetun's VPN provider.

Gluetun writes its active forwarded port to
`/tmp/gluetun/forwarded_port` in the shared `gluetun-port` Docker volume. Polly
mounts that volume read-only, polls the file, validates the port, and sends a
Transmission `session-set` request whenever the value changes. The update:

- assigns the forwarded value as Transmission's `peer-port`;
- disables random peer-port selection at Transmission startup; and
- disables Transmission's router-based port-forwarding feature.

Polly and Transmission share Gluetun's network namespace. Polly therefore
reaches Transmission through its loopback RPC endpoint while all three services
remain within the VPN-controlled network path.

If the forwarded-port file is absent or empty, Polly waits for Gluetun to make a
port available. If Gluetun reconnects and writes a different value, Polly
applies the new port. RPC or file errors are logged and retried during the next
polling cycle.

### Polly configuration

| Variable | Default | Purpose |
|---|---|---|
| `GLUETUN_PORT_FILE` | `/tmp/gluetun/forwarded_port` | Location of Gluetun's forwarded-port file |
| `TRANSMISSION_RPC_URL` | `http://127.0.0.1:9091/transmission/rpc` | Transmission RPC endpoint |
| `TRANSMISSION_RPC_USERNAME` | Empty | Optional Transmission RPC username |
| `TRANSMISSION_RPC_PASSWORD` | Empty | Optional Transmission RPC password |
| `POLL_SECONDS` | `10` | Interval between forwarded-port checks |
| `RPC_TIMEOUT_SECONDS` | `15` | Timeout for each Transmission RPC request |

The Compose stack supplies `POLL_SECONDS` from `POLLY_POLL_SECONDS` in the
selected deployment environment file.

### Polly tests

`infra/srv/polly/test_polly.py` verifies forwarded-port file handling and the
Transmission RPC session handshake. Run it from its source directory with
Python 3:

```bash
cd infra/srv/polly
python -m unittest -v
```

The tests use a temporary port file and a local mock RPC server.

## Transmission Config

`infra/srv/transmission/configure.py` prepares the shared download paths and
applies the Transmission session policy required by the Sonarr and Radarr
pipelines.

It runs as the one-shot `transmission-config` service during stack startup. The
script performs these operations in order:

1. Creates `/tv/downloads` and `/movies/downloads` when necessary.
2. Assigns both directories to the configured `PUID` and `PGID`.
3. Applies mode `0775` to both directories.
4. Waits for the Transmission RPC service to become available.
5. Disables Transmission's incomplete-download directory.
6. Disables Transmission's watch directory.
7. Enables a zero seed-ratio limit so completed torrents stop seeding.

Sonarr uses `/tv/downloads` for television acquisitions and Radarr uses
`/movies/downloads` for movie acquisitions. Because each download directory is
inside its corresponding media filesystem, the ARR application can import by
hardlink without crossing filesystems.

Sonarr and Radarr wait for `transmission-config` to exit successfully before
they start. The script retries the Transmission RPC connection until its startup
timeout expires and exits with an error if the required session settings cannot
be applied.

### Transmission Config variables

| Variable | Default | Purpose |
|---|---|---|
| `TRANSMISSION_RPC_URL` | `http://127.0.0.1:9091/transmission/rpc` | Transmission RPC endpoint within Gluetun's network namespace |
| `TV_DOWNLOAD_DIR` | `/tv/downloads` | Television download directory to create and prepare |
| `MOVIES_DOWNLOAD_DIR` | `/movies/downloads` | Movie download directory to create and prepare |
| `PUID` | `1000` | Owner UID applied to both download directories |
| `PGID` | `1000` | Owner GID applied to both download directories |
| `STARTUP_TIMEOUT_SECONDS` | `120` | Maximum time to wait for Transmission RPC availability |

## Deployment

The deployment procedures install the scripts at the host paths mounted by the
Compose stack:

| Repository source | Default host location | Container location |
|---|---|---|
| `infra/srv/polly/polly.py` | `/srv/polly/polly.py` | `/app/polly.py` |
| `infra/srv/transmission/configure.py` | `/srv/transmission-config/configure.py` | `/app/configure.py` |

`POLLY_ROOT` and `TRANSMISSION_CONFIG_ROOT` can select different host locations
through the deployment environment file. Both scripts are mounted read-only
inside their containers.
