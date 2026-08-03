# Secrets Management

## Environment Files

HARBOR supplies environment templates in `apps/srv/media`:

- `.env.prod.template` for production
- `.env.staging.template` for staging

During deployment, the selected template is copied to `/srv/media` as either
`.env.prod` or `.env.staging`. The deployed environment file contains the
credentials and environment-specific values consumed by Docker Compose.

The environment files are excluded by `apps/srv/media/.gitignore`. Keep the
templates limited to variable names, safe defaults, and placeholder values.

## Values Managed as Secrets

| Variable | Used by | Purpose |
|---|---|---|
| `CLOUDFLARED_TOKEN` | Cloudflared | Authenticates the environment's Cloudflare Tunnel |
| `OPENVPN_USER` | Gluetun | Authenticates the VPN connection |
| `OPENVPN_PASSWORD` | Gluetun | Authenticates the VPN connection |
| `TRANSMISSION_RPC_USERNAME` | Polly | Authenticates Polly to Transmission RPC when RPC authentication is enabled |
| `TRANSMISSION_RPC_PASSWORD` | Polly | Authenticates Polly to Transmission RPC when RPC authentication is enabled |

Production and staging use separate environment files and separate Cloudflare
Tunnel tokens. Store the VPN credentials required by each server only in that
server's deployed environment file.

Application credentials and API keys created through Jellyfin, Transmission,
Prowlarr, Sonarr, or Radarr are stored in their application configuration under
`/srv/media`. Protect that configuration with the same account and filesystem
access controls used for the deployed stack.

## Create the Environment File

Production:

```bash
SERVICE_ACCOUNT=replace-with-common-service-account
sudo cp /srv/media/.env.prod.template /srv/media/.env.prod
sudo chown "${SERVICE_ACCOUNT}:$(id -gn "$SERVICE_ACCOUNT")" /srv/media/.env.prod
sudo chmod 600 /srv/media/.env.prod
sudo nano /srv/media/.env.prod
```

Staging:

```bash
SERVICE_ACCOUNT=replace-with-common-service-account
sudo cp /srv/media/.env.staging.template /srv/media/.env.staging
sudo chown "${SERVICE_ACCOUNT}:$(id -gn "$SERVICE_ACCOUNT")" /srv/media/.env.staging
sudo chmod 600 /srv/media/.env.staging
sudo nano /srv/media/.env.staging
```

Replace every credential placeholder in the selected file. Leave the optional
Transmission RPC credentials empty when Transmission RPC authentication is not
enabled.

Confirm ownership and permissions without displaying the file contents. Use
the command for the active environment:

Production:

```bash
sudo stat -c '%U:%G %a %n' /srv/media/.env.prod
```

Staging:

```bash
sudo stat -c '%U:%G %a %n' /srv/media/.env.staging
```

The active environment file should report the common service account and its
primary group with mode `600`. Only the file used by that server needs to
exist.

## Repository Checks

Before committing or pushing changes, check that deployed environment files are
ignored:

```bash
cd ~/workspace/HARBOR
git check-ignore -v apps/srv/media/.env.prod
git check-ignore -v apps/srv/media/.env.staging
git status --short
```

Review staged changes before every commit:

```bash
git diff --cached --name-only
git diff --cached
```

Environment templates must contain placeholders rather than working tokens,
usernames, passwords, private URLs, or copied application configuration.

## Rotate a Secret

1. Issue a replacement credential through the VPN provider, Cloudflare, or the
   applicable application.
2. Edit the deployed environment file on the affected server.
3. Confirm that the file remains owned by the common service account and its
   primary group with mode `600`.
4. Recreate the affected service using the environment's Compose files.
5. Confirm that the service starts and authenticates successfully.
6. Revoke the previous credential after the replacement has been validated.

For a production credential change, use:

```bash
cd /srv/media
sudo docker compose \
  --env-file .env.prod \
  -f compose.yaml \
  -f compose.prod.yaml \
  up -d --force-recreate SERVICE_NAME
```

For a staging credential change, use:

```bash
cd /srv/media
sudo docker compose \
  --env-file .env.staging \
  -f compose.yaml \
  -f compose.staging.yaml \
  up -d --force-recreate SERVICE_NAME
```

Use `cloudflared` for a tunnel-token change and `gluetun` for VPN credential
changes. Recreate `polly` after changing its Transmission RPC credentials.

## Exposed Credential Response

If a credential is committed, pushed, displayed publicly, or otherwise
exposed:

1. Revoke or rotate the credential immediately.
2. Update the deployed environment file with the replacement.
3. Recreate and validate the affected service.
4. Remove the secret from the repository and its Git history before publishing
   or continuing to distribute the repository.
5. Review the repository for additional copies of the exposed value.

Removing a secret from the latest commit does not remove it from earlier Git
history. Credential rotation remains required even after the history is
cleaned.
