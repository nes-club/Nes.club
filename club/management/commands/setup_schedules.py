"""
Idempotent setup of django-q2 scheduled tasks.
Replaces the cron container. Run once on deployment (before qcluster starts).
Existing schedules with matching names are left unchanged to preserve any manual edits.
"""
import logging

from django.core.management import BaseCommand
from django_q.models import Schedule

log = logging.getLogger(__name__)

SCHEDULES = [
    # (name, func, cron_expression)
    # Cron format: minute hour day-of-month month day-of-week
    ("notify_expired_intros",         "club.tasks.run_notify_expired_intros",       "0 13 * * 2"),
    ("send_weekly_digest",            "club.tasks.run_send_weekly_digest",          "0 10 * * 1"),
    ("cleanup_post_views",            "club.tasks.run_cleanup_post_views",          "0 2 * * 6"),
    ("rebuild_search_index",          "club.tasks.run_rebuild_search_index",        "0 2 * * 7"),
    ("replay_pending_moderation",     "club.tasks.run_replay_pending_moderation",   "20 */6 * * *"),
    ("update_hotness",                "club.tasks.run_update_hotness",              "13 */6 * * *"),
    ("promote_old_post",              "club.tasks.run_promote_old_post",            "0 7 * * 3,6"),
]


class Command(BaseCommand):
    help = "Register all recurring scheduled tasks in django-q2 (idempotent)"

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for name, func, cron in SCHEDULES:
            _, created = Schedule.objects.get_or_create(
                name=name,
                defaults={
                    "func": func,
                    "schedule_type": Schedule.CRON,
                    "cron": cron,
                    "repeats": -1,  # repeat forever
                },
            )
            if created:
                created_count += 1
                log.info(f"Created schedule: {name} ({cron})")
            else:
                skipped_count += 1

        self.stdout.write(
            f"Schedules: {created_count} created, {skipped_count} already existed. Done 🥙"
        )
