# Change Management

## Purpose

This document defines how changes to the server are made, tested, documented, and deployed. The goal is to maintain a stable system that can be rebuilt and recovered at any time.

This server is operated by a single administrator. Change management exists to prevent untested or undocumented changes from breaking the system.

---

## Change Philosophy

The server is treated as a managed system, not a personal workstation.
Changes are controlled to ensure stability, recoverability, and reproducibility.

The repositories are the source of truth for how the system is built and configured.
The running server should always match the repositories and documentation.

If the server cannot be rebuilt from the repositories and documentation, the change process has failed.

---

## Change Process

Change Management is a workflow in process of design.  The expected workflow is as follows:

Develop → Validate → Commit → Test → Document → Deploy

### Develop

All programmatic design and composition is to be built on local user workstations.

### Validate

All functionality developed on workstations is tested and debugged to ensure proper expected behavior prior to committing to the repository.

### Commit

Changes to infrastructure, applications, or configuration are committed to the appropriate repository:

homeserver-infra
homeserver-apps
homeserver-docs

### Test

All changes are tested in the test environment (VM) before being deployed to production.

### Document

Documentation is updated to reflect the change so that the system can be rebuilt and maintained in the future.

### Deploy

After testing, committing, and documenting, the change is deployed to the production server.

---

## Emergency Changes

If the system is down or severely impaired, changes may be made directly to production to restore service.

After an emergency change:

The change must be replicated in the test environment.
The repositories must be updated.
Documentation must be updated.
The change must be committed.

Production and repositories must be brought back into sync.

---

## Rollback

If a change causes problems in production, the system should be returned to the last known working state by:

Reverting the change in Git, or
Restoring previous configuration files, or
Restoring from backup if necessary

Changes should be reversible whenever possible.

---

## Summary

- test changes before deploying
- commit changes to Git
- document changes
- deploy to production
- keep production and repositories in sync
- be able to roll back if something breaks

If these rules are followed, the system will remain stable, recoverable, and maintainable.