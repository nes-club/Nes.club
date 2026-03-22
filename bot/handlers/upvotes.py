import logging

from asgiref.sync import sync_to_async

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.common import get_club_user, get_club_comment, get_club_post
from bot.config import COMMENT_EMOJI_RE, POST_EMOJI_RE
from bot.decorators import is_club_member
from comments.models import CommentVote, Comment
from posts.models.post import Post
from posts.models.votes import PostVote

log = logging.getLogger(__name__)


@is_club_member
async def upvote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("Upvote handler triggered")

    if not update.message or not update.message.reply_to_message:
        return None

    user = await get_club_user(update)
    if not user:
        return None

    reply_text_start = (
        update.message.reply_to_message.text or
        update.message.reply_to_message.caption or
        ""
    )[:10]

    if COMMENT_EMOJI_RE.match(reply_text_start):
        comment = await get_club_comment(update)
        if comment:
            _, is_created = await sync_to_async(CommentVote.upvote)(user=user, comment=comment)
            await update.message.reply_text(f"➜ Заплюсовано 👍" if is_created else "➜ Ты уже плюсовал, поц")

    if POST_EMOJI_RE.match(reply_text_start):
        post = await get_club_post(update)
        if post:
            _, is_created = await sync_to_async(PostVote.upvote)(user=user, post=post)
            await update.message.reply_text("➜ Заплюсовано 👍" if is_created else "➜ Ты уже плюсовал, поц")

    return None


async def upvote_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("Upvote_comment handler triggered")

    user = await get_club_user(update)
    if not user:
        return None

    _, comment_id = update.callback_query.data.split(":", 1)
    def _upvote_comment():
        c = Comment.objects.filter(id=comment_id).select_related("post").first()
        if not c:
            return None, None
        _, created = CommentVote.upvote(user=user, comment=c)
        return c, created
    comment, is_created = await sync_to_async(_upvote_comment)()
    if not comment:
        log.info("Original comment not found. Skipping.")
        return None

    if is_created:
        await update.callback_query.answer(text="Комментарий заплюсован 👍")
    else:
        await update.callback_query.answer(text="Вы уже плюсовали этот комментарий")

    return None


async def upvote_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("Upvote_post handler triggered")

    user = await get_club_user(update)
    if not user:
        return None

    _, post_id = update.callback_query.data.split(":", 1)
    def _upvote_post():
        p = Post.objects.filter(id=post_id).first()
        if not p:
            return None, None
        _, created = PostVote.upvote(user=user, post=p)
        return p, created
    post, is_created = await sync_to_async(_upvote_post)()
    if not post:
        log.info("Original post not found. Skipping.")
        return None

    if is_created:
        await update.callback_query.answer(text="Пост заплюсован 👍")
    else:
        await update.callback_query.answer(text="Вы уже плюсовали этот пост")

    return None
