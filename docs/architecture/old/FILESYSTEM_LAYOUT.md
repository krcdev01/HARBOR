# Filesystem Layout

## Overview

This document defines the filesystem layout expected by a HARBOR deployment.

It documents the logical storage roles and directory structure required by the platform. It does not prescribe specific host mount points, filesystems, disk models, or server-specific backup policy.

---

## Media Storage

### TV Library
Path: `/tv`  
Purpose: Primary television series library.

Managed by:
- Sonarr (import and organization)
- Jellyfin (media playback)

Directory structure:

```text
/tv
└── Videos
    ├── Family TV
    ├── Judgement
    ├── New and Requested
    └── Series Shows
        ├── Adult Swim
        ├── Anime
        ├── Permanent Collection
        └── Star Trek
```

Notes:

- `Videos` is a case-sensitive path and is required by the current Sonarr path model.
- Folder names under `Videos` represent the expected organizational structure for the HARBOR TV library.
- `Family TV` is intended for children and family-safe television content.
- `Judgement` is a holding area for content under review for deletion.
- `New and Requested` is the default landing area for newly imported television content.
- `Series Shows` is the primary long-term series collection.

---

### Movie Library
Path: `/movies`  
Purpose: Primary movie library.

Managed by:
- Radarr (import and organization)
- Jellyfin (playback)

Directory structure:

```text
/movies
└── videos
    ├── Family
    ├── Judgement
    ├── New and Requested
    └── Permanent Movies
        ├── Anime Movies
        ├── Evergreen
        ├── MCU The Infinity Saga
        └── Star Trek
```

Notes:

- `videos` is intentionally lowercase and should remain consistent with the application path model.
- `Family` is intended for children and family-safe films.
- `Judgement` is a holding area for films under review for deletion.
- `New and Requested` is the default landing area for newly imported films.
- `Permanent Movies` is the primary long-term movie collection.

---

## Download Storage

### Downloads Root
Path: `/downloads`  
Purpose: qBittorrent download, staging, and seeding storage.

Structure:

```text
/downloads/incomplete
/downloads/complete/movies
/downloads/complete/tv
/downloads/complete/seed
```

Directory roles:

- `/downloads/incomplete`  
  Active torrent downloads managed by qBittorrent.

- `/downloads/complete/movies`  
  Completed movie downloads staged for Radarr import.

- `/downloads/complete/tv`  
  Completed television downloads staged for Sonarr import.

- `/downloads/complete/seed`  
  Persistent seeding storage for content that must remain available after import.

---

## Media Lifecycle

Typical media acquisition workflow:

1. qBittorrent downloads content to `/downloads/incomplete`.
2. After completion, content moves to `/downloads/complete/movies` or `/downloads/complete/tv`.
3. Radarr or Sonarr imports the media into the appropriate library directory.
4. Jellyfin scans the library and makes the content available for playback.

---

## Notes

- This document describes the HARBOR filesystem model in logical terms.
- Host-specific mount points, storage devices, and filesystem types belong in the Homeserver repository or another deployment-specific repository.
- If a deployment uses different host paths, those paths must still map into the container/application paths documented here.
