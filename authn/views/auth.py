from datetime import datetime

from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django_q.tasks import async_task

from authn.models.session import Code
from invites.models import Invite
from notifications.email.users import send_auth_email
from notifications.telegram.users import notify_user_auth
from users.models.user import User
from users.services.access import grant_long_membership

from authn.decorators.auth import require_auth
from authn.models.session import Session


def join(request):
    if request.me:
        return redirect("profile", request.me.slug)

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        if not request.POST.get("iconsent"):
            return render(request, "auth/join.html", {
                "error": "Нужно согласиться с правилами и обработкой данных.",
                "email": email,
                "invite_code": request.POST.get("invite_code"),
            })
        invite_code = (request.POST.get("invite_code") or "").strip().upper()

        if not email or "@" not in email:
            return render(request, "auth/join.html", {
                "error": "Укажите корректный email.",
                "email": email,
                "invite_code": invite_code,
            })

        is_nes_email = email.endswith("@nes.ru")
        invite = None
        if not is_nes_email:
            if not invite_code:
                return render(request, "auth/join.html", {
                    "error": "Для адресов вне @nes.ru нужен инвайт-код.",
                    "email": email,
                    "invite_code": invite_code,
                })

            invite = Invite.objects.filter(code=invite_code).first()
            if not invite or invite.is_expired or invite.is_used:
                return render(request, "auth/join.html", {
                    "error": "Инвайт-код недействителен или уже использован.",
                    "email": email,
                    "invite_code": invite_code,
                })

        now = datetime.utcnow()
        user, _ = User.objects.get_or_create(
            email=email,
            defaults=dict(
                membership_platform_type=User.MEMBERSHIP_PLATFORM_DIRECT,
                full_name=email.split("@")[0],
                membership_started_at=now,
                membership_expires_at=now,
                created_at=now,
                updated_at=now,
                moderation_status=User.MODERATION_STATUS_INTRO,
            ),
        )

        grant_long_membership(user)

        if invite:
            invite.used_at = now
            invite.invited_user = user
            invite.invited_email = email
            invite.save()

        code = Code.create_for_user(user=user, recipient=user.email)
        async_task(send_auth_email, user, code)
        async_task(notify_user_auth, user, code)

        return render(request, "auth/email.html", {
            "email": user.email,
            "goto": None,
            "restore": user.deleted_at is not None,
        })

    return render(request, "auth/join.html")


def login(request):
    if request.me:
        return redirect("profile", request.me.slug)

    return render(request, "auth/login.html", {
        "goto": request.GET.get("goto"),
        "email": request.GET.get("email"),
    })


@require_auth
@require_http_methods(["POST"])
def logout(request):
    token = request.COOKIES.get("token")
    Session.objects.filter(token=token).delete()
    cache.delete(f"token:{token}:session")
    return redirect("index")
