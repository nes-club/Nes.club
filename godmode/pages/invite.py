from datetime import datetime

from django import forms
from django.template.loader import render_to_string

from notifications.email.invites import send_invited_email
from notifications.telegram.common import send_telegram_message, ADMIN_CHAT
from users.models.user import User


class InviteByEmailForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        required=True,
    )


def invite_user_by_email(request, admin_page):
    if request.method == "POST":
        form = InviteByEmailForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            now = datetime.utcnow()

            user = User.objects.filter(email=email).first()
            if user:
                user.updated_at = now
                user.save()
            else:
                # create new user with that email
                user, is_created = User.objects.get_or_create(
                    email=email,
                    defaults=dict(
                        full_name=email[:email.find("@")],
                        created_at=now,
                        updated_at=now,
                        moderation_status=User.MODERATION_STATUS_INTRO,
                    ),
                )

            if user.moderation_status == User.MODERATION_STATUS_INTRO:
                send_invited_email(request.me, user)
                send_telegram_message(
                    chat=ADMIN_CHAT,
                    text=f"🎁 <b>Юзера '{email}' пригласили в сообщество</b>",
                )

            return render_to_string("godmode/pages/message.html", {
                "title": "🎁 Юзер приглашен",
                "message": f"Сейчас он получит на почту '{email}' уведомление об этом. "
                           f"Ему будет нужно залогиниться по этой почте и заполнить интро."
            }, request=request)
    else:
        form = InviteByEmailForm()

    return render_to_string("godmode/pages/simple_form.html", {
        "form": form
    }, request=request)
