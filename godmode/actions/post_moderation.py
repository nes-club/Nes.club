from datetime import datetime

from django.shortcuts import render
from django_q.tasks import async_task

from bot.handlers.common import PostRejectReason
from notifications.telegram.posts import notify_post_approved, announce_in_club_chats, notify_post_rejected, \
    notify_post_collectible_tag_owners, notify_post_room_subscribers
from posts.models.post import Post
from search.models import SearchIndex


def post_approve_post(request, post: Post, **context):
    if post.moderation_status in [Post.MODERATION_APPROVED, Post.MODERATION_FORGIVEN, Post.MODERATION_REJECTED]:
        return render(request, "godmode/message.html", {
            **context,
            "title": "Пост уже отмодерирован",
            "message": f"Пост «{post.title}» уже имеет статус {post.moderation_status}.",
        })

    post.moderation_status = Post.MODERATION_APPROVED
    post.visibility = Post.VISIBILITY_EVERYWHERE
    post.last_activity_at = datetime.utcnow()
    post.published_at = datetime.utcnow()
    post.save()

    notify_post_approved(post)
    announce_in_club_chats(post)

    if post.collectible_tag_code:
        async_task(notify_post_collectible_tag_owners, post)

    if post.room_id:
        async_task(notify_post_room_subscribers, post)

    SearchIndex.update_post_index(post)

    return render(request, "godmode/message.html", {
        **context,
        "title": f"✅ Пост «{post.title}» одобрен",
        "message": "Статус сменен на approved.",
    })


def post_reject_post(request, post: Post, **context):
    if post.moderation_status in [Post.MODERATION_APPROVED, Post.MODERATION_FORGIVEN, Post.MODERATION_REJECTED]:
        return render(request, "godmode/message.html", {
            **context,
            "title": "Пост уже отмодерирован",
            "message": f"Пост «{post.title}» уже имеет статус {post.moderation_status}.",
        })

    post.moderation_status = Post.MODERATION_REJECTED
    post.unpublish()
    post.save()

    notify_post_rejected(post, PostRejectReason.draft)
    SearchIndex.update_post_index(post)

    return render(request, "godmode/message.html", {
        **context,
        "title": f"❌ Пост «{post.title}» отклонен",
        "message": "Статус сменен на rejected.",
    })
