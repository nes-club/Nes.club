# posts — Feed & Content

Multi-type post creation, feed rendering, subscriptions, upvoting, RSS, and SEO.

## Post Types

| Constant | Value | Emoji | Description |
|----------|-------|-------|-------------|
| `TYPE_POST` | `post` | 📝 | Plain text |
| `TYPE_INTRO` | `intro` | 🙋‍♀️ | User intro (auto-created on signup) |
| `TYPE_LINK` | `link` | 🔗 | Link with preview |
| `TYPE_QUESTION` | `question` | ❓ | Q&A |
| `TYPE_IDEA` | `idea` | 💡 | Ideas |
| `TYPE_PROJECT` | `project` | 🏗 | Projects |
| `TYPE_EVENT` | `event` | 📅 | Events with date/location |
| `TYPE_BATTLE` | `battle` | 🤜🤛 | Opinion battles |
| `TYPE_WEEKLY_DIGEST` | `weekly_digest` | — | Auto-generated weekly digest |
| `TYPE_GUIDE` | `guide` | 🗺 | Guides |
| `TYPE_THREAD` | `thread` | 🗄 | Threads |
| `TYPE_DOCS` | `docs` | 📚 | Documentation |
| `TYPE_JOB` | `job` | 💼 | Job postings |

All types defined in `posts/models/post.py` with `TYPE_TO_EMOJI` and `TYPE_TO_PREFIX` dicts.

## Models

| Model | Purpose |
|-------|---------|
| `Post` | Main content model |
| `PostVote` | Upvotes (one per user per post) |
| `PostSubscription` | Users following a post's comments |
| `PostView` | View tracking for analytics |
| `LinkedPost` | Internal cross-references between posts |

## Key Post Fields

- `moderation_status`: `none` / `pending` / `approved` / `forgiven` / `rejected`
- `visibility`: `everywhere` / `members_only` / `draft` / `link_only`
- `is_public`: if True, visible to unauthenticated users (world-indexed)
- `html`: cached rendered HTML (updated on save)
- `upvotes`: cached vote count
- `hotness`: float score updated by scheduled task

## Moderation

Auto-approve threshold: `settings.COMMUNITY_APPROVE_UPVOTES` upvotes triggers approval without moderator action.

## Feed Ordering

Default: `-ordering_weight` (hotness). Can be sorted by time, comments, upvotes. Filtered by room, label, author, type.

## Markdown Rendering

`posts/renderers.py` → `common/markdown/club_renderer.py` (mistune 3). Renders to HTML with:
- YouTube/Twitter/iframe embeds
- Link previews
- Code highlighting

HTML cached in `Post.html` field to avoid re-rendering on every page load.

## RSS

- `GET /posts/rss/` — site-wide RSS
- `GET /user/<slug>/rss/` — per-user RSS
