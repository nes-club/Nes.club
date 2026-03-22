# common — Shared Utilities

Shared code used across all apps: markdown rendering, image processing, data catalogs, and utilities.

## Markdown Rendering

`common/markdown/` — multi-renderer architecture. Same source markdown → different output formats:

| Renderer | Output | Used for |
|----------|--------|---------|
| `club_renderer.py` | HTML with embeds | Web pages |
| `email_renderer.py` | Plain HTML | Email digests |
| `telegram_renderer.py` | Telegram-compatible HTML | Bot messages |
| `plain_renderer.py` | Plain text | OG descriptions |

All renderers use mistune 3 with custom plugins in `markdown/plugins/`:
- YouTube/Twitter/video embeds
- Link preview cards
- Code block highlighting
- Club-specific syntax extensions

## Image Processing

`common/images.py` — resize and optimize uploaded images. Used by `ImageUploadField` in forms.

`ImageUploadField` parameters: `resize=(width, height)`, `convert_to="jpg"`.

## URL Metadata Parser

`common/url_metadata_parser.py` — extracts title, description, og:image from URLs. Used for link-type posts. Depends on `newspaper4k`.

## Data Catalogs

| File | Contents |
|------|---------|
| `data/labels.py` | Post labels/tags catalog with display names and colors |
| `data/countries.py` | Country choices list (used in intro form) |
| `data/colors.py` | Color palette constants |
| `data/greetings.py` | Random greeting strings |

## Models

`ModelDiffMixin` — mixed into User and Post to track field-level changes between saves. Used to detect what changed for notifications.

## Forms

`ImageUploadField` — Django form field that handles image upload, resize, and format conversion.
