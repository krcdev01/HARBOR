# SYSTEM_OVERVIEW.md

## Purpose

This document provides an overview of the system defined in this repository, including its functional roles, major components, data model, and operational characteristics.

---

## System Functions

The system provides the following capabilities:

- Media streaming through a self-hosted media server
- Automated media acquisition and organization
- Secure download routing through a VPN
- Remote access to selected services through an outbound tunnel

---

## Major Components

- Container Platform  
  Docker is used to run services in isolated containers.

- Media Server  
  Jellyfin provides media streaming.

- Media Acquisition  
  Sonarr and Radarr manage media acquisition and organization.  
  qBittorrent provides download functionality.

- VPN Routing  
  Traffic is routed through a VPN container to control outbound network behavior.

- Remote Access  
  A tunnel service provides external access without inbound port exposure.

---

## Data Model

### Media Library
Media content used for streaming. This data is replaceable and not required for system recovery.

### Application Configuration
Configuration and databases for all services. This data is required to restore system state.

### System Configuration
Container definitions and configuration required to deploy the system.

### Working Data
Temporary data such as downloads, caches, and logs. Not required for recovery.

---

## External Dependencies

- VPN provider for network routing
- Tunnel provider for remote access
- Indexers and trackers for media acquisition
- Container registries for images
- Package repositories for system dependencies

---

## Security Model

- Services are isolated in containers
- Only required services are exposed
- Sensitive data is stored outside version control
- VPN routing restricts traffic flow
- Remote access uses outbound connectivity

---

## Recovery Model

The system is designed to be redeployed from repository contents and restored configuration data.

- Deploy containers from configuration
- Restore application state
- Verify service operation

---

## Summary

- Services are containerized and isolated
- Data is separated by recovery importance
- External services provide connectivity and functionality
- System can be redeployed and restored from defined inputs
