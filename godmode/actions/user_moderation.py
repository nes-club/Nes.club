from datetime import datetime, timedelta

from django.shortcuts import render

from bot.handlers.common import UserRejectReason
from notifications.email.users import send_user_rejected_email, send_welcome_drink
from notifications.telegram.posts import announce_in_club_chats
from notifications.telegram.users import notify_user_profile_approved, notify_user_profile_rejected
from posts.models.post import Post
from posts.models.subscriptions import PostSubscription
from search.models import SearchIndex
from users.models.user import User


def post_approve_user(request, user: User, **context):
    if user.moderation_status == User.MODERATION_STATUS_APPROVED:
        return render(request, "godmode/message.html", {
            **context,
            "title": "Пользователь уже одобрен",
            "message": f"Юзер {user.full_name} уже в статусе approved.",
        })

    if user.moderation_status == User.MODERATION_STATUS_REJECTED:
        return render(request, "godmode/message.html", {
            **context,
            "title": "Пользователь уже отклонен",
            "message": f"Юзер {user.full_name} уже отклонен и ждет новое интро.",
        })

    user.moderation_status = User.MODERATION_STATUS_APPROVED
    if user.created_at > datetime.utcnow() - timedelta(days=30):
        user.created_at = datetime.utcnow()
    user.save()

    intro = Post.objects.filter(author=user, type=Post.TYPE_INTRO).first()
    if intro:
        intro.moderation_status = Post.MODERATION_APPROVED
        intro.visibility = Post.VISIBILITY_EVERYWHERE
        intro.last_activity_at = datetime.utcnow()
        if not intro.published_at:
            intro.published_at = datetime.utcnow()
        intro.save()

        PostSubscription.subscribe(user, intro, type=PostSubscription.TYPE_ALL_COMMENTS)
        announce_in_club_chats(intro)

    SearchIndex.update_user_index(user)

    notify_user_profile_approved(user)
    send_welcome_drink(user)

    return render(request, "godmode/message.html", {
        **context,
        "title": f"✅ Пользователь {user.full_name} одобрен",
        "message": "Статус сменен на approved.",
    })


def post_reject_user(request, user: User, **context):
    if user.moderation_status == User.MODERATION_STATUS_REJECTED:
        return render(request, "godmode/message.html", {
            **context,
            "title": "Пользователь уже отклонен",
            "message": f"Юзер {user.full_name} уже в статусе rejected.",
        })

    if user.moderation_status == User.MODERATION_STATUS_APPROVED:
        return render(request, "godmode/message.html", {
            **context,
            "title": "Пользователь уже одобрен",
            "message": f"Юзер {user.full_name} уже в статусе approved.",
        })

    user.moderation_status = User.MODERATION_STATUS_REJECTED
    user.save()

    notify_user_profile_rejected(user, UserRejectReason.intro)
    send_user_rejected_email(user, UserRejectReason.intro)

    return render(request, "godmode/message.html", {
        **context,
        "title": f"❌ Пользователь {user.full_name} отклонен",
        "message": "Статус сменен на rejected.",
    })
