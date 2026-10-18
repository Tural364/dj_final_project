from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("SkillSwap", {"fields": ("role", "bio", "avatar", "is_blocked")}),)
    list_display = ("username", "email", "role", "is_blocked", "is_staff", "is_superuser")
    list_filter = ("role", "is_blocked", "is_staff")
