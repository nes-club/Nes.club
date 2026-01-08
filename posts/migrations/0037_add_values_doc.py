from datetime import datetime

from django.db import migrations

from club.settings import MODERATOR_USERNAME


DOC = {
    "slug": "values",
    "type": "docs",
    "title": "Ценности сообщества",
    "text": (
        "### Зачем мы здесь\n\n"
        "Это пространство выпускников, сотрудников и друзей РЭШ для общения, поддержки и обмена опытом.\n\n"
        "### Как мы общаемся\n\n"
        "- Уважение к участникам и их времени\n"
        "- Полезность и конструктивность\n"
        "- Честность и открытость, без анонимности\n"
        "- Вежливость даже в споре\n\n"
        "### Чего мы не принимаем\n\n"
        "- Токсичность и оскорбления\n"
        "- Травлю и охоту на ведьм\n"
        "- Мошенничество и спам\n\n"
        "Если сомневаетесь — напишите модераторам."
    ),
    "is_visible": True,
    "is_visible_in_feeds": False,
    "is_public": True,
}


def insert_values_doc(apps, schema_editor):
    User = apps.get_model("users", "User")
    Post = apps.get_model("posts", "Post")

    author = User.objects.filter(slug=MODERATOR_USERNAME).first()
    if not author:
        return

    now = datetime.utcnow()

    Post.objects.get_or_create(
        slug=DOC["slug"],
        defaults={
            "type": DOC["type"],
            "title": DOC["title"],
            "text": DOC["text"],
            "author": author,
            "created_at": now,
            "updated_at": now,
            "last_activity_at": now,
            "published_at": now,
            "is_commentable": False,
            "is_public": DOC["is_public"],
            "visibility": "everywhere" if DOC["is_visible"] else "draft",
            "moderation_status": "approved",
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0036_alter_post_moderation_status"),
    ]

    operations = [
        migrations.RunPython(insert_values_doc),
    ]
