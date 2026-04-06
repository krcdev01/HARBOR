# Troubleshooting

This document outlines common issues and resolutions for the system.

## Users are unable to connect or log in

- Check that external URL is accessible
- Check that docker instances for jellyfin and cloudflared are running and healthy
- Confirm remote user can access URL from remote location
- Recreate the connection in the application profile
- Reset user's credentials

---

## Wrong movie or TV metadata

This issue can present as misidentified content or database inconsistency.

- Open the jellyfin web UI and locate the content
- Obtain correct metadata ID (IMDb for movies, TVDB for series)
- Use the "Identify" function and enter the correct ID
- Replace existing images and confirm correction

---

## Playback suddenly stops (all content)

This is typically caused by driver or kernel mismatch.

- Verify system updates
- Confirm hardware acceleration compatibility
- Review logs for driver errors

---

## Some content does not play

- Check health of the jellyfin container
- Restart jellyfin
- Run library scan
- Review logs if issue persists

---

## "Ghost" Metadata

Occurs when content is moved between libraries.

- Remove duplicate entries from UI
- If unresolved, treat as database issue and escalate

---

## Notes

- Advanced issues require log review and deeper triage
