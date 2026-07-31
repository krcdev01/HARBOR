# Jellyfin + Cloudflared Compose Environment Split

This directory uses a shared Compose file plus environment-specific override files.

## Files

- `compose.yaml` — shared Jellyfin and Cloudflared service definitions
- `compose.prod.yaml` — production-only GPU/NVIDIA settings
- `compose.staging.yaml` — staging override; currently keeps staging CPU-only
- `.env.prod.template` — production environment template
- `.env.staging.template` — staging environment template

Copy the appropriate template to a real `.env` file on the target host. Do not commit real tunnel tokens.

## Production deploy

```bash
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d
```

## Staging deploy

```bash
docker compose --env-file .env.staging -f compose.yaml -f compose.staging.yaml up -d
```

## Cloudflare requirement

Production and staging should use separate Cloudflare Tunnel tokens unless you deliberately route both hostnames through the same tunnel. The staging tunnel should route:

```text
staging.torrentialspoils.com -> http://jellyfin:8096
```
