import logging
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db import OperationalError

from comments.models import Comment
from posts.models.post import Post
from search.models import SearchIndex
from users.models.user import User
from utils.queryset import chunked_queryset

log = logging.getLogger(__name__)

# The index is maintained live on every post/comment/user edit (see SearchIndex.update_*_index
# callers across the app). This command is only a safety net that re-indexes recently changed
# records to catch anything the live hooks missed — so by default it works incrementally.
DEFAULT_INCREMENTAL_DAYS = 8


class Command(BaseCommand):
    help = "Incrementally rebuild the search index for recently changed posts, comments and users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=DEFAULT_INCREMENTAL_DAYS,
            help=f"Reindex records updated within the last N days (default: {DEFAULT_INCREMENTAL_DAYS})",
        )
        parser.add_argument(
            "--full", action="store_true",
            help="Full rebuild from scratch (slow — wipes and reindexes the entire index)",
        )

    def handle(self, *args, **options):
        is_full = options["full"]
        since = None if is_full else datetime.utcnow() - timedelta(days=options["days"])

        if is_full:
            SearchIndex.objects.all().delete()

        indexed_comment_count = 0
        indexed_post_count = 0
        indexed_user_count = 0

        comments = Comment.visible_objects().filter(is_deleted=False, post__visibility=Post.VISIBILITY_EVERYWHERE)
        posts = Post.visible_objects()
        users = User.objects.filter(moderation_status=User.MODERATION_STATUS_APPROVED)

        if since is not None:
            comments = comments.filter(updated_at__gte=since)
            posts = posts.filter(updated_at__gte=since)
            users = users.filter(updated_at__gte=since)

        for chunk in chunked_queryset(comments):
            for comment in chunk:
                self.stdout.write(f"Indexing comment: {comment.id}")

                try:
                    SearchIndex.update_comment_index(comment)
                except OperationalError as ex:
                    log.exception("Failed to update comment index", exc_info=ex)
                    continue

                indexed_comment_count += 1

        for chunk in chunked_queryset(posts):
            for post in chunk:
                self.stdout.write(f"Indexing post: {post.slug}")

                try:
                    SearchIndex.update_post_index(post)
                except OperationalError as ex:
                    log.exception("Failed to update post index", exc_info=ex)
                    continue

                indexed_post_count += 1

        for chunk in chunked_queryset(users):
            for user in chunk:
                self.stdout.write(f"Indexing user: {user.slug}")

                try:
                    SearchIndex.update_user_index(user)
                except OperationalError as ex:
                    log.exception("Failed to update user index", exc_info=ex)
                    continue

                try:
                    SearchIndex.update_user_tags(user)
                except OperationalError as ex:
                    log.exception("Failed to update user tags", exc_info=ex)
                    continue

                indexed_user_count += 1

        mode = "full" if is_full else f"incremental (last {options['days']}d)"
        self.stdout.write(
            f"Done 🥙 [{mode}] "
            f"Comments: {indexed_comment_count} Posts: {indexed_post_count} Users: {indexed_user_count}"
        )
