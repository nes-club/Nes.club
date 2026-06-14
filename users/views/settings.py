from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render

from authn.decorators.auth import require_auth
from search.models import SearchIndex
from users.forms.profile import ProfileEditForm, NotificationsEditForm
from users.models.user import User
from utils.strings import random_hash


@require_auth
def profile_settings(request, user_slug):
    if user_slug == "me" and request.me:
        return redirect("profile_settings", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    return render(request, "users/edit/index.html", {"user": user})


@require_auth
def edit_profile(request, user_slug):
    if user_slug == "me" and request.me:
        return redirect("edit_profile", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            SearchIndex.update_user_index(user)
    else:
        form = ProfileEditForm(instance=user)

    return render(request, "users/edit/profile.html", {"form": form, "user": user})


@require_auth
def edit_account(request, user_slug):
    if user_slug == "me" and request.me:
        return redirect("edit_account", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    if request.method == "POST" and request.POST.get("regenerate"):
        user.secret_hash = random_hash(length=16)
        user.save()
        return redirect("edit_account", user.slug, permanent=False)

    return render(request, "users/edit/account.html", {"user": user})


@require_auth
def edit_notifications(request, user_slug):
    if user_slug == "me" and request.me:
        return redirect("edit_notifications", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    if request.method == "POST":
        form = NotificationsEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect("profile", user.slug)
    else:
        form = NotificationsEditForm(instance=user)

    return render(request, "users/edit/notifications.html", {"form": form, "user": user})


@require_auth
def edit_bot(request, user_slug):
    if user_slug == "me" and request.me:
        return redirect("edit_bot", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    return render(request, "users/edit/bot.html", {"user": user})
