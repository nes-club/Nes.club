# comments — Discussion

Nested comments on posts, upvotes, moderation, and IP logging.

## Models

| Model | Purpose |
|-------|---------|
| `Comment` | Comment with optional reply_to for threading |
| `CommentVote` | Upvotes (one per user per comment) |

## Key Fields

| Field | Purpose |
|-------|---------|
| `reply_to` | Parent comment FK (nullable → root comment) |
| `is_pinned` | Moderator-pinned |
| `is_deleted` | Soft delete flag |
| `deleted_by` | UUID of who deleted (for audit) |
| `html` | Cached rendered HTML |
| `upvotes` | Cached vote count |
| `ip` / `useragent` | Logged for moderation |

## Threading

Max 3 nesting levels enforced at save time. Comments beyond level 3 are flattened to level 3.

## Rendering

Comment body is Markdown, rendered via `common/markdown/club_renderer.py`. HTML cached in `comment.html`.

## Moderation

- Moderators can delete any comment (sets `is_deleted=True`, records `deleted_by`)
- Authors can delete their own comments within a time window
- Pinned comments shown at top of thread

## History

`django-simple-history` tracks edits. Excluded fields: `post`, `html`, `reply_to`, IP/UA, counters, status flags.
