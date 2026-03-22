import logging
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async

from django.conf import settings
from django.urls import reverse
from django_q.tasks import async_task
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.common import UserRejectReason, PostRejectReason
from bot.decorators import is_moderator
from notifications.email.users import send_welcome_drink, send_user_rejected_email
from notifications.telegram.posts import notify_post_approved, announce_in_club_chats, \
    notify_post_rejected, notify_post_collectible_tag_owners, notify_post_room_subscribers
from notifications.telegram.users import notify_user_profile_approved, notify_user_profile_rejected
from posts.models.post import Post
from posts.models.subscriptions import PostSubscription
from search.models import SearchIndex
from users.models.user import User

log = logging.getLogger(__name__)


@is_moderator
async def approve_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, post_id = update.callback_query.data.split(":", 1)

    def _approve():
        p = Post.objects.get(id=post_id)
        if p.moderation_status in [Post.MODERATION_APPROVED, Post.MODERATION_FORGIVEN, Post.MODERATION_REJECTED]:
            return p, False
        p.moderation_status = Post.MODERATION_APPROVED
        p.visibility = Post.VISIBILITY_EVERYWHERE
        p.last_activity_at = datetime.utcnow()
        p.published_at = datetime.utcnow()
        p.save()
        notify_post_approved(p)
        announce_in_club_chats(p)
        SearchIndex.update_post_index(p)
        return p, True
    post, changed = await sync_to_async(_approve)()

    if not changed:
        await update.effective_chat.send_message(f"Пост «{post.title}» уже был отмодерирован ранее: {post.moderation_status}")
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    post_url = settings.APP_HOST + reverse("show_post", kwargs={
        "post_type": post.type,
        "post_slug": post.slug,
    })

    if post.room_id and post.is_room_only:
        await update.effective_chat.send_message(
            f"😎 Пост «{post.title}» хорош для комнаты «{post.room.title}», "
            f"но не будет отображаться на главной ({update.effective_user.full_name}): {post_url}",
            disable_web_page_preview=True
        )
    else:
        await update.effective_chat.send_message(
            f"👍 Пост «{post.title}» одобрен ({update.effective_user.full_name}): {post_url}",
            disable_web_page_preview=True
        )

    # hide buttons
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    if post.collectible_tag_code:
        async_task(notify_post_collectible_tag_owners, post)

    if post.room_id:
        async_task(notify_post_room_subscribers, post)

    return None


@is_moderator
async def forgive_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, post_id = update.callback_query.data.split(":", 1)

    def _forgive():
        p = Post.objects.get(id=post_id)
        if p.moderation_status in [Post.MODERATION_APPROVED, Post.MODERATION_FORGIVEN, Post.MODERATION_REJECTED]:
            return p, False
        p.moderation_status = Post.MODERATION_FORGIVEN
        p.visibility = Post.VISIBILITY_EVERYWHERE
        p.last_activity_at = datetime.utcnow()
        p.published_at = datetime.utcnow()
        p.collectible_tag_code = None
        p.save()
        SearchIndex.update_post_index(p)
        return p, True
    post, changed = await sync_to_async(_forgive)()

    if not changed:
        await update.effective_chat.send_message(f"Пост «{post.title}» уже был отмодерирован ранее: {post.moderation_status}")
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    post_url = settings.APP_HOST + reverse("show_post", kwargs={
        "post_type": post.type,
        "post_slug": post.slug,
    })

    await update.effective_chat.send_message(
        f"😕 Пост «{post.title}» не одобрен, но оставлен на сайте ({update.effective_user.full_name}): {post_url}",
        disable_web_page_preview=True
    )

    # hide buttons
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    return None


@is_moderator
async def reject_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code, post_id = update.callback_query.data.split(":", 1)
    reason = {
        "reject_post": PostRejectReason.draft,
        "reject_post_title": PostRejectReason.title,
        "reject_post_design": PostRejectReason.design,
        "reject_post_dyor": PostRejectReason.dyor,
        "reject_post_duplicate": PostRejectReason.duplicate,
        "reject_post_chat": PostRejectReason.chat,
        "reject_post_tldr": PostRejectReason.tldr,
        "reject_post_github": PostRejectReason.github,
        "reject_post_bias": PostRejectReason.bias,
        "reject_post_hot": PostRejectReason.hot,
        "reject_post_ad": PostRejectReason.ad,
        "reject_post_inside": PostRejectReason.inside,
        "reject_post_value": PostRejectReason.value,
        "reject_post_draft": PostRejectReason.draft,
        "reject_post_false_dilemma": PostRejectReason.false_dilemma,
    }.get(code) or PostRejectReason.draft

    def _reject():
        p = Post.objects.get(id=post_id)
        if p.moderation_status in [Post.MODERATION_APPROVED, Post.MODERATION_FORGIVEN, Post.MODERATION_REJECTED]:
            return p, False
        p.moderation_status = Post.MODERATION_REJECTED
        p.unpublish()
        SearchIndex.update_post_index(p)
        notify_post_rejected(p, reason)
        return p, True
    post, changed = await sync_to_async(_reject)()

    if not changed:
        await update.effective_chat.send_message(f"Пост «{post.title}» уже был отмодерирован ранее: {post.moderation_status}")
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    await update.effective_chat.send_message(
        f"👎 Пост «{post.title}» перенесен в черновики по причине «{reason.value}» ({update.effective_user.full_name})"
    )

    # hide buttons
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    return None


@is_moderator
async def approve_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, user_id = update.callback_query.data.split(":", 1)

    def _approve_user():
        u = User.objects.get(id=user_id)
        if u.moderation_status in [User.MODERATION_STATUS_APPROVED, User.MODERATION_STATUS_REJECTED]:
            return u, None, u.moderation_status
        u.moderation_status = User.MODERATION_STATUS_APPROVED
        if u.created_at > datetime.utcnow() - timedelta(days=30):
            u.created_at = datetime.utcnow()
        u.save()
        i = Post.objects.filter(author=u, type=Post.TYPE_INTRO).first()
        if i:
            i.moderation_status = Post.MODERATION_APPROVED
            i.visibility = Post.VISIBILITY_EVERYWHERE
            i.last_activity_at = datetime.utcnow()
            if not i.published_at:
                i.published_at = datetime.utcnow()
            i.save()
            PostSubscription.subscribe(u, i, type=PostSubscription.TYPE_ALL_COMMENTS)
        SearchIndex.update_user_index(u)
        notify_user_profile_approved(u)
        send_welcome_drink(u)
        announce_in_club_chats(i)
        return u, i, None
    user, intro, prev_status = await sync_to_async(_approve_user)()

    if prev_status == User.MODERATION_STATUS_APPROVED:
        await update.effective_chat.send_message(f"Пользователь «{user.full_name}» уже одобрен")
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    if prev_status == User.MODERATION_STATUS_REJECTED:
        await update.effective_chat.send_message(f"Пользователь «{user.full_name}» уже был отклонен")
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    await update.effective_chat.send_message(
        f"✅ Пользователь «{user.full_name}» одобрен ({update.effective_user.full_name})"
    )

    # hide buttons
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    return None


@is_moderator
async def reject_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code, user_id = update.callback_query.data.split(":", 1)
    reason = {
        "reject_user": UserRejectReason.intro,
        "reject_user_intro": UserRejectReason.intro,
        "reject_user_data": UserRejectReason.data,
        "reject_user_aggression": UserRejectReason.aggression,
        "reject_user_general": UserRejectReason.general,
        "reject_user_name": UserRejectReason.name,
    }.get(code) or UserRejectReason.intro

    def _reject_user():
        u = User.objects.get(id=user_id)
        if u.moderation_status in [User.MODERATION_STATUS_REJECTED, User.MODERATION_STATUS_APPROVED]:
            return u, u.moderation_status
        u.moderation_status = User.MODERATION_STATUS_REJECTED
        u.save()
        notify_user_profile_rejected(u, reason)
        send_user_rejected_email(u, reason)
        return u, None
    user, prev_status = await sync_to_async(_reject_user)()

    if prev_status == User.MODERATION_STATUS_REJECTED:
        await update.effective_chat.send_message(
            f"Пользователь «{user.full_name}» уже был отклонен и пошел все переделывать"
        )
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    if prev_status == User.MODERATION_STATUS_APPROVED:
        await update.effective_chat.send_message(
            f"Пользователь «{user.full_name}» уже был принят, его нельзя реджектить"
        )
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return None

    await update.effective_chat.send_message(
        f"❌ Пользователь «{user.full_name}» отклонен по причине «{reason.value}» ({update.effective_user.full_name})"
    )

    # hide buttons
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    return None
