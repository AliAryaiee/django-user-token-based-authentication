from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
        User in Admin Panel
    """
    list_display = ["username", "phone", "is_active", "is_staff"]
    list_editable = ["is_active", "is_staff"]
    list_per_page = 10
    # ordering = [""]


# admin.site.register(User)
