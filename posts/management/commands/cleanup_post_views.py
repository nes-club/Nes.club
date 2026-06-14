import logging

from django.core.management import BaseCommand
from django.db import connection

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cleans up old and useless anonymous post views to save DB space"

    def handle(self, *args, **options):
        # cleanup anonymous post_views older than 3 days
        with connection.cursor() as cursor:
            cursor.execute("""
                delete from post_views where user_id is null and last_view_at < now() - interval '3 days'
            """)

        self.stdout.write("Done 🥙")
