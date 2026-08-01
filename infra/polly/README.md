# Polly

Polly keeps Transmission's peer port synchronized with the port assigned by
Gluetun's VPN provider.

Gluetun writes its current forwarded port to a shared Docker volume. Polly
checks that value and updates Transmission through its RPC interface whenever
the port appears or changes. If the VPN disconnects, Gluetun clears the value;
Polly waits and reapplies the assigned port after forwarding returns.

## Deployment

Install the script at the path used by the media stack:

```bash
sudo mkdir -p /srv/polly
sudo cp infra/polly/polly.py /srv/polly/polly.py
sudo chmod 755 /srv/polly/polly.py
```

If Transmission RPC authentication is enabled, set
`TRANSMISSION_RPC_USERNAME` and `TRANSMISSION_RPC_PASSWORD` in the deployment's
environment file.
