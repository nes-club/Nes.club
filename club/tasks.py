"""
Wrapper functions for scheduled management commands.
These are referenced by django-q2 Schedule objects (see setup_schedules management command).
"""
from django.core.management import call_command


def run_delete_users():
    call_command("delete_users")


def run_send_daily_digest():
    call_command("send_daily_digest", production=True)


def run_send_weekly_digest():
    call_command("send_weekly_digest", production=True)


def run_notify_expired_intros():
    call_command("notify_expired_intros", production=True)


def run_send_best_comments():
    call_command("send_best_comments")


def run_cleanup_post_views():
    call_command("cleanup_post_views")


def run_rebuild_search_index():
    call_command("rebuild_search_index")


def run_count_chat_members():
    call_command("count_chat_members")


def run_replay_stuck_reviews():
    call_command("replay_stuck_reviews")


def run_replay_pending_moderation():
    call_command("replay_pending_moderation_posts")


def run_cleanup_gdpr_downloads():
    call_command("cleanup_gdpr_downloads")


def run_update_hotness():
    call_command("update_hotness")


def run_promote_old_post():
    call_command("promote_one_old_post_on_main")
