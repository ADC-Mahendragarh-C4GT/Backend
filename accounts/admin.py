from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "user_type", "isActive", "is_staff")
    list_filter = ("user_type", "isActive", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name", "isActive")
    ordering = ("username", "-isActive")

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("user_type", "phone_number")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("user_type", "phone_number")}),
    )