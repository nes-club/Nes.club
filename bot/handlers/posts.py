import logging

from asgiref.sync import sync_to_async

from django.urls import reverse
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.common import get_club_user
from club import settings
from posts.models.post import Post
from posts.models.subscriptions import PostSubscription

log = logging.getLogger(__name__)


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_club_user(update)
    if not user or not user.telegram_id:
        return None

    _, post_id = update.callback_query.data.split(":", 1)
    def _subscribe():
        p = Post.objects.filter(id=post_id).first()
        if not p:
            return None, None
        _, created = PostSubscription.subscribe(user=user, post=p, type=PostSubscription.TYPE_TOP_LEVEL_ONLY)
        return p, created
    post, is_created = await sync_to_async(_subscribe)()
    if not post:
        return None

    if user.telegram_id:
        await update.callback_query.answer(
            text=f"Вы подписались на уведомления о новых комментариях к посту «{post.title}» 🔔"
        )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_club_user(update)
    if not user or not user.telegram_id:
        return None

    _, post_id = update.callback_query.data.split(":", 1)
    def _unsubscribe():
        p = Post.objects.filter(id=post_id).first()
        if not p:
            return None, None
        unsubbed = PostSubscription.unsubscribe(user=user, post=p)
        return p, unsubbed
    post, is_unsubscribed = await sync_to_async(_unsubscribe)()
    if not post:
        return None

    if user.telegram_id:
        post_url = settings.APP_HOST + reverse("show_post", kwargs={
            "post_type": post.type,
            "post_slug": post.slug,
        })

        if is_unsubscribed:
            await update.callback_query.answer(
                text=f"Вы отписались от о комментариев к посту «{post.title}» 🔕"
            )
        else:
            await update.callback_query.answer(
                text="Вы и не были подписаны на уведомления к этому посту ❌"
            )
