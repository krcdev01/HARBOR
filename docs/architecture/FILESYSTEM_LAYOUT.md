# Filesystem Layout -- What storage exists and what is it used for?

## Media Storage

### TV Library
Mount point: /mnt/tv  
Filesystem: ext4
Purpose: Primary television series library.

Managed by:
- Sonarr (import and organization)
- Jellyfin (media playback)

Directory structure:

/mnt/tv
├── Videos (case-sensitive path required by existing Sonarr configuration)
│   ├── Family TV 
│   ├── Judgement 
│   ├── New and Requested
|   └── Series Shows
│       ├── Adult Swim
│       ├── Anime
│       ├── Permanent Collection
│       └── Star Trek

Notes:

Family TV
Children and Family Shows; intended to be for children to watch independently 7 years or younger.

Judgement  
TV content under review for disposal.

New and Requested
Default Sonarr landing folder for new series episodes

Series Shows  
This is the core collection of Series Content that should be restorable from backup resoures.  These folders are self-explanatory.

---

### Movie Library
Mount point: /mnt/movies  
Filesystem: ext4
Purpose: Primary movie library.

Managed by:
- Radarr (imports and organization)
- Jellyfin (playback)

Directory structure:

/mnt/movies
├── videos
│   ├── Family
│   ├── Judgement
│   ├── New and Requested
│   └── Permanent Movies
│       ├── Anime Movies
│       ├── Evergreen
│       ├── MCU The Infinity Saga
│       └── Star Trek

Notes:

Family
Children and Family Movies; intended to be for children to watch indendently 7 years or younger.

Judgement  
Movies under review for disposal.

New and Requested
Default Radarr landing folder for new films.

Permanent Movies 
This is the core collection of Movies that should be restorable from backup resoures.  These folders are self-explanatory.

---

## Download Storage

### Downloads Root
Mount point: /mnt/downloads
Filesystem: ext4
Purpose: qBittorrent download and seeding storage.

Structure:

/mnt/downloads/incomplete  
/mnt/downloads/complete/movies  
/mnt/downloads/complete/tv  
/mnt/downloads/complete/seed



Directory roles:

/mnt/downloads/incomplete  
Active torrent downloads managed by qBittorrent.

/mnt/downloads/complete/movies  
Completed movie downloads staged for Radarr import.

/mnt/downloads/complete/tv  
Completed TV downloads staged for Sonarr import.

/mnt/downloads/complete/seed  
Permanent seeding storage for private trackers (e.g. MySpleen).

## Media Lifecycle

Typical media acquisition workflow:

1. Torrent is downloaded to `/mnt/downloads/incomplete` by qBittorrent.
2. After completion, files move to `/mnt/downloads/complete/movies` or `/mnt/downloads/complete/tv`.
3. Radarr or Sonarr imports the media into the appropriate library directory.
4. Jellyfin scans the library and makes the content available for playback.
