# frontend — Vue.js 2 + Webpack 5

Client-side interactivity via Vue.js 2 components embedded in Django templates. Not a SPA.

## Architecture

- Django renders full HTML pages server-side
- Vue.js components are mounted on specific DOM elements for interactivity
- No Vuex, no Vue Router — each component is independent

## Build

```bash
# Development (hot reload)
npm run dev

# Production
npm run build
```

Output goes to `frontend/static/dist/`. Webpack generates `webpack-stats.json` for Django integration via `django-webpack-loader`.

## Entry Point

`frontend/static/js/main.js`:
- Imports and globally registers all Vue components
- Creates the root Vue instance
- **Disables `{{ }}` delimiters** (`delimiters: ['[[', ']]']`) to prevent conflicts with Django templates
- Use `[[ variable ]]` syntax in Vue templates within Django HTML

## Key Vue Components

| Component | Purpose |
|-----------|---------|
| `PostUpvote` | Upvote button with animated count |
| `PostBookmark` | Save/unsave post |
| `PostRSVP` | Event RSVP button |
| `CommentUpvote` | Comment vote |
| `MarkdownEditor` | Post/comment Markdown editor |
| `PeopleMap` | Alumni map (Leaflet-based geolocation) |
| `UserTag` | Tag toggling on user profile |
| `FriendButton` | Add/remove friend |
| `TagSelect` | Multi-select for tags (post labels, user tags) |
| `LocationSelect` | Country + city selection |
| `ThemeSwitcher` | Dark/light mode toggle |
| `Clicker` | Poll / reaction button |
| `InputLengthCounter` | Character counter for textareas (used in intro form) |

## Django Template Integration

```html
{# Load webpack assets #}
{% load render_bundle from webpack_loader %}
{% render_bundle 'main' 'css' %}
{% render_bundle 'main' 'js' %}

{# Mount a Vue component #}
<post-upvote :post-id="{{ post.id }}" :initial-count="{{ post.upvotes }}"></post-upvote>
```

## CSS

PostCSS with autoprefixer. Main stylesheet at `frontend/static/css/`. Extracted by MiniCssExtractPlugin into separate `.css` bundle.

## Fonts & Static Assets

Font files and images in `frontend/static/`. Processed by file-loader, output to `dist/` with hashed filenames.
