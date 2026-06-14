from datetime import datetime

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from authn.decorators.auth import require_auth
from authn.helpers import set_session_cookie
from authn.models.session import Session
from club.exceptions import AccessDenied
from invites.models import Invite
from users.models.user import User


@require_auth
def list_invites(request):
    return render(request, "invites/list_invites.html", {
        "invites": Invite.for_user(request.me),
    })


def show_invite(request, invite_code):
    invite = get_object_or_404(Invite, code=invite_code)

    if invite.user == request.me:
        return render(request, "invites/edit.html", {
            "invite": invite,
        })

    if invite.is_used:
        return render(request, "error.html", {
            "title": "Этот инвайт-код уже использован 🥲",
            "message": "Кажется, кто-то уже использовал этот инвайт. "
                       "Вы можете связаться с человеком, который вам его подарил, и спросить что случилось."
        })

    if invite.is_expired:
        return render(request, "error.html", {
            "title": "Этот инвайт истек 🥲",
            "message": "Инвайт-код никто не использовал в течение года и он протух. "
                       "По нему больше не получится зарегистрироваться."
        })

    return render(request, "invites/show.html", {
        "invite": invite
    })


def activate_invite(request, invite_code):
    invite = get_object_or_404(Invite, code=invite_code)

    if invite.is_used:
        if request.me and request.me.is_moderator:
            return render(request, "error.html", {
                "title": "Этот инвайт-код уже использован 🥲",
                "message": f"Включен режим модератора. Пользователь: {invite.invited_user.slug if invite.invited_user else '(удалён)'}"
            })

        return render(request, "error.html", {
            "title": "Этот инвайт-код уже использован 🥲",
            "message": "Кажется, кто-то уже использовал этот инвайт. "
                       "Вы можете связаться с человеком, который вам его подарил, и спросить что случилось."
        })

    if invite.is_expired:
        return render(request, "error.html", {
            "title": "Этот инвайт истек 🥲",
            "message": "Инвайт-код никто не использовал в течение года и он протух. "
                       "По нему больше не получится зарегистрироваться."
        })

    email = request.POST.get("email")
    if not email or "@" not in email or "." not in email:
        return render(request, "error.html", {
            "title": "Странный email",
            "message": "Пожалуйста, введите нормальный адрес почты, чтобы зарегистрироваться."
        })

    # create or find existing user
    now = datetime.utcnow()
    email = email.lower().strip()
    user, _ = User.objects.get_or_create(
        email=email,
        defaults=dict(
            full_name=email[:email.find("@")],
            created_at=now,
            updated_at=now,
            moderation_status=User.MODERATION_STATUS_INTRO,
        ),
    )

    # expire the invite
    invite.used_at = now
    invite.invited_user = user
    invite.save()

    # log in user
    session = Session.create_for_user(user)
    redirect_to = reverse("profile", args=[user.slug])
    response = redirect(redirect_to)
    return set_session_cookie(response, user, session)


@require_auth
def godmode_generate_invite_code(request):
    if request.method != "POST":
        raise Http404()

    if not request.me.is_god:
        raise AccessDenied()

    Invite.objects.create(
        user=request.me,
    )

    return redirect("invites")


@require_auth
def create_invite(request):
    if request.method != "POST":
        raise Http404()

    Invite.objects.create(
        user=request.me,
    )

    return redirect("invites")
