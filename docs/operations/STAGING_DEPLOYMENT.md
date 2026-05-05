# Deployment Plan

## Purpose

This document describes the procedure to deploy HARBOR to my personal staging environment.  This document is to be used as a baseline for a general deployment plan document in the future that is universally compatible with a single environmental deploy.

## Server Buildout Plan

### Phase 0 - Prerequisite

HARBOR is an AAR media streaming stack designed to be a turnkey-deploy on a sufficiently equipped home media server.  Minimum Requirements are yet to be determined, but development of this process is being done against two different devices:

- An on-demand virtual machine running 2 cores and 8GB of RAM with no hardware graphics accelerator and 10GB staged mounts
- An always-on hardware production server running a Ryzen 5 3600 with 48GB of ram and 29 total TB of drive space

Regardless of the hardware configuration, the environment must be with the following installs:

    - Ubuntu Server
    - Docker
    - UFW
    - git
    - a shared service account for the AAR stack

Additionally, the following three mounts must exist:

    - /mnt/movies
    - /mnt/tv
    - /mnt/downloads

### - Phase 1 - Foundation/setup

1. Pull down the HARBOR repository

   Clone the HOMESERVER repository to your service account home directory:

   ```bash
   mkdir ~/workspace && cd ~/workspace && git clone git@github.com:krcdev01/HARBOR.git
   ```

### - Phase 2 - Architecture Deployment

1. Set up or check and make sure Cloudflare is gonna work on the staging server.

### - Phase 3 - Infrastructure Deployment

1. Copy all of the contents in the infra/srv/ directory over to your server, /srv/ as the destination:

   ```bash
   sudo cp -r ~/workspace/HARBOR/infra/srv/* /srv/
   ```

2. Do something that starts everything up.

3. Do Jellyfin setup.

### - Phase 4 - Validation

1. Confirm your jellyfin server is reachable both internally on your local network and externally through the internet.

2. Play content to confirm both audio and video work.

3. If possible, play something that must transcode to confirm transcoding is properly configured.

4. Play something with subtitles to confirm subtitles are working.
