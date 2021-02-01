from django.contrib import admin

from .models import CustomerEvent, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("last_login", "is_superuser", "is_staff", "is_active", "date_joined")
    raw_id_fields = ("groups", "user_permissions", "addresses")


@admin.register(CustomerEvent)
class CustomerEventAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "type", "parameters", "user")
    list_filter = ("date", "user")
