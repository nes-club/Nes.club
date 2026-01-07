from datetime import datetime, timedelta

from club.exceptions import BadRequest, InsufficientFunds
from users.models.user import User


LONG_ACCESS_DAYS = 365 * 1000


def gift_membership_days(days, from_user, to_user, deduct_from_original_user=True):
    if days <= 0:
        raise BadRequest(message="Количество дней должно быть больше 0")

    amount = timedelta(days=days)

    if deduct_from_original_user and from_user.membership_expires_at - amount <= datetime.utcnow():
        raise InsufficientFunds()

    if to_user.membership_expires_at <= datetime.utcnow():
        to_user.membership_expires_at = datetime.utcnow()
    to_user.membership_expires_at += amount
    to_user.membership_platform_type = User.MEMBERSHIP_PLATFORM_DIRECT
    to_user.save()

    if deduct_from_original_user:
        from_user.membership_expires_at -= amount
        from_user.save()

    return to_user.membership_expires_at


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
