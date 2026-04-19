from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "email", "role", "site", "is_active", "is_staff")
    list_filter = ("role", "site", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email", "telephone")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profil métier", {"fields": ("role", "telephone", "site")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profil métier", {"fields": ("role", "telephone", "site", "first_name", "last_name", "email")}),
    )
