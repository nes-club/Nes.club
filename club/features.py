# FEATURE-FLAGS
# Use them to enable/disable different functions
# We recommend to create new feature-flags if you want to add new features or disable existing ones in your fork
# That way you can upstream changes later if needed

# Hide posts feed (main page) from unauthorized users
#   True — feed is only visible to club members, other users will be redirected to landing page
#   False — everyone can view the feed, it becomes the main page
PRIVATE_FEED = True

# Patreon auth is disabled for NES alumni community.
PATREON_AUTH_ENABLED = False
