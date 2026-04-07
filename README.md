# HARBOR

## Overview

This repository defines a containerized media and network stack that provides:

- Media streaming
- Automated media acquisition and organization
- VPN-routed download traffic
- Remote access through an outbound tunnel

All services are deployed using Docker and are designed to run on systems that meet the required hardware and storage constraints.

---

## What This Repository Contains

- Container definitions and configuration
- Required environment variables and configuration patterns
- Architecture documentation
- Operational procedures (startup, shutdown, troubleshooting)
- Data persistence requirements

---

## What This Repository Does Not Contain

- Host operating system configuration
- Hardware-specific setup
- Backup implementation
- Network infrastructure outside the stack
- Secrets or credentials

These concerns are handled outside this repository.

---

## Requirements

Minimum requirements for deployment:

- Linux-based host system
- Docker and Docker Compose
- Persistent storage for:
  - media libraries
  - downloads
  - application configuration
- Network access for:
  - container image pulls
  - VPN provider
  - external services (indexers, tunnel provider)

---

## Deployment Overview

1. Prepare host system with Docker installed
2. Define required environment variables
3. Map host storage to required container paths
4. Deploy containers using provided configuration
5. Verify service availability

Detailed deployment instructions are located in the documentation.

---

## Documentation

See the `docs/` directory for:

- Architecture
  - container inventory
  - network topology
  - filesystem layout
- Operations
  - startup and shutdown procedures
  - troubleshooting
  - secrets and configuration
  - persistence requirements

---

## Design Principles

- Services are isolated in containers
- Network exposure is minimized
- State is externalized and recoverable
- The system can be redeployed from repository contents

---

## Summary

This repository defines a complete, deployable service stack.

All required behavior, structure, and operation are documented within this repository.