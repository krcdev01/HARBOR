# Backup Strategy

## Overview
This server uses Borg Backup to create versioned configuration backups.
The purpose of these backups is to allow full system rebuild and configuration restore.

Backups are performed by the CORSAIR backup system via a systemd timer.


## What Gets Backed Up

The backup includes:

- /etc — system configuration
- /home/serveradmin — user scripts and workspace
- /opt/arrstack — Docker stacks and application configs
- /srv/jellyfin/config — Jellyfin configuration and database
- /srv/pihole — Pi-hole configuration

The backup explicitly EXCLUDES:

- /srv/borg (the backup repository itself)
- Media storage (/mnt/movies, /mnt/tv)
- Downloads (/mnt/downloads)

Media files are considered replaceable and are not backed up.

## Backup Schedule and Retention Policy

The script automatically prunes backups with the following retention:

| Backup Type | Retention |
|---|---|
| Daily | 7 |
| Weekly | 4 |
| Monthly | 6 |

After pruning, the repository is compacted to reclaim space.

Repository Location: /srv/borg/config-repo
Archive Naming Format: corsair-config-YYYY-MM-DD_HH-MM

## Secrets and Credentials

The Borg passphrase is stored at:

/root/.config/corsair/borg.env

This file is backed up by CORSAIR but is NOT stored in Git.  A template exists in the infrastructure repository to replace if lost.

## Restore Philosophy

This backup system is designed so that the entire server can be rebuilt from:

1. Fresh OS install
2. Restore Borg repository
3. Restore configuration files
4. Redeploy Docker stacks
5. Restore application configs

## Recovery Objectives

RPO: 24 hours — Configuration backups run daily. Worst-case data loss is one day of configuration changes.

RTO: Approximately 2-4 hours to rebuild the server from bare metal and restore all services from backup.  

