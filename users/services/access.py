from datetime import datetime, timedelta

from users.models.user import User


LONG_ACCESS_DAYS = 365 * 100


def grant_long_membership(user: User) -> None:
    now = datetime.utcnow()
    if user.membership_started_at is None:
        user.membership_started_at = now

    target_expires_at = now + timedelta(days=LONG_ACCESS_DAYS)
    if user.membership_expires_at is None or user.membership_expires_at < target_expires_at:
        user.membership_expires_at = target_expires_at

    if user.membership_platform_type == User.MEMBERSHIP_PLATFORM_PATREON:
        user.membership_platform_type = User.MEMBERSHIP_PLATFORM_DIRECT

    user.save()
