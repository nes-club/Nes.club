from django.http import JsonResponse, HttpResponseNotAllowed

from authn.decorators.api import api
from club.exceptions import ApiAccessDenied
from common.api import API
from invites.models import Invite
from utils.strings import random_string


@api(require_auth=True)
def api_gift_invite_link(request):
    if request.method == "GET":
        user_invites = Invite.for_user(user=request.me)
        return JsonResponse({
            "invites": [invite.to_dict() for invite in user_invites],
        })

    if request.method == "POST":
        if not request.me.is_bank:
            raise ApiAccessDenied(message="Только юзеры с ролью 'bank' могут генерировать инвайты")

        invite = Invite.objects.create(
            user=request.me,
            code=API.get_str(request, "reference") or "bank-" + random_string(length=16),
        )

        return JsonResponse({
            "invite": invite.to_dict(),
        })

    return HttpResponseNotAllowed(permitted_methods=["GET", "POST"])
