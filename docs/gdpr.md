# gdpr — Data Export & Account Deletion

GDPR compliance: user data export as a downloadable archive, and account deletion.

## Models

`DataRequests` — tracks export/deletion requests with rate limiting (one archive per day per user).

## Data Export

`gdpr/archive.py` — generates a JSON archive containing:
- User profile data
- All posts authored by the user
- All comments
- Badges received
- Statistics

Rate-limited: one request per day. The archive is stored temporarily and cleaned up after 3 days by the `cleanup_gdpr_downloads` scheduled task.

`cleanup_gdpr_downloads` management command (`gdpr/management/commands/`) deletes files older than 3 days from `settings.GDPR_ARCHIVE_STORAGE_PATH`.

## Account Deletion ("Forget Me")

`gdpr/forget.py` — deletion pipeline:
- Sets `User.deleted_at` and `moderation_status = "deleted"`
- Anonymizes personal data fields
- Retains moderation history (for safety)
- Revokes all sessions

User cannot log in after deletion.

## Views

- `GET /gdpr/` — GDPR overview page
- `POST /gdpr/export/` — request data archive
- `POST /gdpr/forget/` — initiate account deletion (requires confirmation)
- `GET /gdpr/download/<token>/` — download generated archive
