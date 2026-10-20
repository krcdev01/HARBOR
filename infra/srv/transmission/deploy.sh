#!/bin/bash
# Deploy the production Transmission path fix from this checkout.
set -Eeuo pipefail
trap 'rc=$?; echo "Deployment failed (exit $rc); inspect the output above." >&2; exit "$rc"' ERR

[[ $EUID == 0 ]] || { echo "Run with sudo bash $0" >&2; exit 1; }
[[ $# == 0 ]] || { echo "Usage: sudo bash $0" >&2; exit 1; }
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
source_dir="$repo/apps/srv/media"
helper="$repo/infra/srv/transmission/configure.py"
live_dir=/srv/media
env_file="$live_dir/.env.prod"

for command in docker python3 findmnt install; do
    command -v "$command" >/dev/null || { echo "Missing command: $command" >&2; exit 1; }
done
docker compose version >/dev/null
[[ -f "$env_file" && -f "$helper" ]] || { echo "Missing production environment file or configuration helper" >&2; exit 1; }
# Never create download folders underneath unmounted media mount points.
for root in /mnt/movies /mnt/tv; do
    findmnt -rn -M "$root" >/dev/null || { echo "Media filesystem is not mounted: $root" >&2; exit 1; }
done

# Retain the existing Compose project so this cannot create a second stack.
project=$(docker inspect transmission --format '{{index .Config.Labels "com.docker.compose.project"}}')
[[ -n "$project" && "$project" != '<no value>' ]] || { echo "Transmission is not managed by a Compose project" >&2; exit 1; }
compose=(docker compose --project-name "$project" --project-directory "$live_dir" --env-file "$env_file")
candidate=("${compose[@]}" -f "$source_dir/compose.yaml" -f "$source_dir/compose.prod.yaml")

# Resolved config contains secrets: keep it private and never print it.
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
"${candidate[@]}" config --format json > "$work/config.json"
python3 - "$work/config.json" > "$work/paths" <<'PY'
import json
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[1]).read_text())
services = config["services"]

def mounts(name):
    return {m["target"]: m for m in services[name].get("volumes", [])}

def require(condition, message):
    if not condition:
        raise SystemExit(message)

for name in ("transmission", "radarr"):
    mounted = mounts(name)
    require(mounted.get("/movies", {}).get("source") == "/mnt/movies",
            f"{name}: expected /mnt/movies -> /movies")
    legacy = mounted.get("/downloads/complete", {})
    require(legacy.get("source") == "/mnt/movies/downloads" and
            legacy.get("type") == "bind" and not legacy.get("read_only", False) and
            legacy.get("bind", {}).get("create_host_path", False) is False,
            f"{name}: expected existing writable media-drive bind for /downloads/complete")
require(mounts("transmission").get("/tv", {}).get("source") == "/mnt/tv",
        "Transmission: expected /mnt/tv -> /tv")
require(mounts("transmission").get("/config", {}).get("source") == "/srv/media/transmission",
        "Unexpected Transmission configuration directory")
helper_mount = mounts("transmission-config").get("/app/configure.py", {})
helper_path = helper_mount.get("source", "")
require(helper_mount.get("type") == "bind" and Path(helper_path).is_absolute()
        and Path(helper_path).name == "configure.py", "Invalid helper bind mount")
for target, source in (("/tv", "/mnt/tv"), ("/movies", "/mnt/movies")):
    require(mounts("transmission-config").get(target, {}).get("source") == source,
            f"Configuration helper: unexpected mount for {target}")
env = services["transmission"].get("environment", {})
uid, gid = str(env.get("PUID", "")), str(env.get("PGID", ""))
require(uid.isdecimal() and gid.isdecimal(), "PUID and PGID must be numeric")
helper_env = services["transmission-config"].get("environment", {})
require(str(helper_env.get("PUID")) == uid and str(helper_env.get("PGID")) == gid,
        "Transmission and helper must use the same UID/GID")
print(uid)
print(gid)
print(helper_path)
PY
mapfile -t settings < "$work/paths"
uid=${settings[0]}
gid=${settings[1]}
helper_dest=${settings[2]}

# Only the directory roots are prepared; existing downloads are not recursively changed.
install -d -m 0775 -o "$uid" -g "$gid" /mnt/movies/downloads /mnt/tv/downloads
install -d -- "$(dirname -- "$helper_dest")"
install -m 0755 "$helper" "$helper_dest"
install -m 0644 "$source_dir/compose.yaml" "$live_dir/compose.yaml"
install -m 0644 "$source_dir/compose.prod.yaml" "$live_dir/compose.prod.yaml"
live=("${compose[@]}" -f "$live_dir/compose.yaml" -f "$live_dir/compose.prod.yaml")
"${live[@]}" config --quiet

# Keep Gluetun and the rest of the stack running. Use already installed images.
"${live[@]}" up -d --no-deps --no-build --pull never --force-recreate transmission radarr
# Run the helper again even if the previous one-shot container already exited.
"${live[@]}" run --rm --no-deps --pull never transmission-config

# Verify actual write access as Transmission's application identity.
docker exec --user "$uid:$gid" transmission sh -ec '
    for directory in /downloads/complete /movies/downloads /tv/downloads; do
        probe=$(mktemp "$directory/.transmission-write-test.XXXXXX")
        rm -f -- "$probe"
    done
'
docker exec --user "$uid:$gid" radarr sh -ec '
    test -w /downloads/complete && test -w /movies/downloads
'
echo 'PASS: Transmission paths deployed; helper completed; media-drive write checks passed.'
echo 'Existing torrents retain their own locations. Verify Local Data for missing/corrupt entries before resuming them.'
