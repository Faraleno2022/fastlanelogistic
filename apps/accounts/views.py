from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserEditForm, UserManagementForm, UserPasswordForm
from .models import User


def _can_manage_users(user):
    return user.is_authenticated and (
        user.is_superuser or getattr(user, "role", "") == User.Role.ADMIN
    )


def _protect_superuser_fields(form, actor):
    if not actor.is_superuser:
        form.fields.pop("is_superuser", None)


def _can_touch_user(actor, target):
    return actor.is_superuser or not target.is_superuser


@login_required
@user_passes_test(_can_manage_users)
def user_list(request):
    users = (
        User.objects.annotate(group_count=Count("groups"))
        .order_by("username")
    )
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
@user_passes_test(_can_manage_users)
def user_create(request):
    form = UserManagementForm(request.POST or None)
    _protect_superuser_fields(form, request.user)
    if form.is_valid():
        user = form.save()
        messages.success(request, f"Utilisateur {user.username} créé.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {
        "form": form,
        "titre": "Ajouter un utilisateur",
        "icone": "person-plus",
    })


@login_required
@user_passes_test(_can_manage_users)
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if not _can_touch_user(request.user, user_obj):
        messages.error(request, "Seul un superuser peut modifier ce compte.")
        return redirect("accounts:user_list")
    form = UserEditForm(request.POST or None, instance=user_obj)
    _protect_superuser_fields(form, request.user)
    if form.is_valid():
        form.save()
        messages.success(request, f"Utilisateur {user_obj.username} mis à jour.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {
        "form": form,
        "titre": f"Modifier {user_obj.username}",
        "icone": "person-gear",
        "user_obj": user_obj,
    })


@login_required
@user_passes_test(_can_manage_users)
def user_password(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if not _can_touch_user(request.user, user_obj):
        messages.error(request, "Seul un superuser peut changer le mot de passe de ce compte.")
        return redirect("accounts:user_list")
    form = UserPasswordForm(request.POST or None)
    if form.is_valid():
        user_obj.set_password(form.cleaned_data["password1"])
        user_obj.save(update_fields=["password"])
        messages.success(request, f"Mot de passe de {user_obj.username} modifié.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_password.html", {
        "form": form,
        "user_obj": user_obj,
    })


@login_required
@user_passes_test(_can_manage_users)
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if not _can_touch_user(request.user, user_obj):
        messages.error(request, "Seul un superuser peut supprimer ce compte.")
        return redirect("accounts:user_list")
    if user_obj.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect("accounts:user_list")
    if request.method == "POST":
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"Utilisateur {username} supprimé.")
        return redirect("accounts:user_list")
    return render(request, "confirm_delete.html", {
        "objet": user_obj,
        "titre": "Supprimer l'utilisateur",
        "message": f"Supprimer l'utilisateur {user_obj.username} ?",
        "retour_url": "accounts:user_list",
    })
