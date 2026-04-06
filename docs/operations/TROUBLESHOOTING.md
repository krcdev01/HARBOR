# Troubleshooting

This is a simplified troubleshooting document for common problems encountered on the server.  This document only outlines commonly encountered issues on the server and how they can be qiuckly resolved.

## Users are unable to connect to the server or log in

- Check that external url is accessible
- Check that docker instances for pi-hole, jellyfin and cloudflare are running and healthy
- Confirm remote user can access URL from remote location
- Recreate the connection in the application profile
- Reset user's credentials

---

## Wrong movie or TV metadata

This issue can present in one of two ways: a misidentified program, or as database corruption, where the metadata may be partially present or incomplete, or the metadata is correct but the show does not play.  Database corruption requires reviewing the application logs and advanced triage beyond the scope of this document.  These are troubleshooting steps for correcting misidentified content.  In order to perform these steps, the Jellyfin account must be a server administrator.

- Open the jellyfin app in a web browser and log in, then navigate to the misidentified content either through a library or directly on the content's detail page.  This process will not work at the collection level and is inconsistent from the Jellyfin user home page.
- Open a second tab.  To identify a missing movie, go to imdb.com, look up the movie, and grab the imdb ID (a key inside the imdb URL page that starts with 'tt').  For a TV show, go to thetvdb.com, pull up the show page, and find the Series ID value under the General tab for that show.
- Go back to jellyfin, and click the elipsis for the content, and then 'identify.'  Paste the IMDb Id or TheTVDB Numerical Series Id into the appropriately named field on the pop-up modal and click 'Search'.
- Identify the correct program, click it, then make sure "replace existing images" is checked, then click OK.  Give the system 60 seconds, then refresh the view and confirm the show is now properly identified in descriptions and images.

---

## Users (usually Roku users) report that content suddenly stops playing, including content that previously played.

This is usually caused by an nVidia or kernel driver update mismatch.  At this time this issue should not be encountered as the software on the server has been halted from updating while this documentation is composed.  Previously, the solution involved quarantining either the new drivers or libraries on the new kernel creating driver conflicts.

---

## Users report that some (but not all) content stops playing, usually displaying a throbber indefinitely

- Check health of the jellyfin docker container
- Restart Jellyfin first from either the admin panel or through restarting the docker container
- If issue persists, perform a full library scan on the content in the affected library
- If issue still persists, review the jellyfin application logs and begin advanced triage

---

## "Ghost" Metadata

This usually happens when a movie or TV show has changed libraries, and the problem is often compounded when moving content from a "shared" library (movies and TV shows) to an "exclusive" one (only movies or TV shows).  The metadata will appear in more than one library, but will only play from the library it's supposed to be in.  A user admin has to delete the ghost from the UI.  If this does not work, treat as a metadata database corruption issue and escalate to advanced triage.

---

## INTERNAL - Internet troubleshooting

Remember that DNS issues are now a local problem as ISP DNSs are being bypassed.  After confirming that the modem and router are both able to connect to the ISP and working, if the network loses internet connectivity check to see if the homeserver is up first and if so, log in and check the status of pi-hole and confirm it is running and healthy.  If it is not, restart pi-hole.  You will lose connectivity to the server momentarily then be able to reconnect and confirm it's working properly.

---

## INERNAL - Network Lock

This is due to either pi-hole or the server having a system fault and crashing.  Confirm the server cannot be reached, then power down and restart it.

