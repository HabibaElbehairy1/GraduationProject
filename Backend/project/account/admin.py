from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_staff', 'is_superuser')

    def has_add_permission(self, request):
        """Superusers cannot add new users."""
        return False  # Prevent adding any user

    def has_change_permission(self, request, obj=None):
        """Only superusers can edit users."""
        return request.user.is_superuser  # Only superusers can edit

    def get_readonly_fields(self, request, obj=None):
        """Allow superusers to edit only 'is_staff' and 'is_superuser' fields for all users."""
        if request.user.is_superuser:
            return [field.name for field in self.model._meta.fields if field.name not in ['is_staff', 'is_superuser']]
        return [field.name for field in self.model._meta.fields]  # All fields read-only for others


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')

    def has_change_permission(self, request, obj=None):
        return False  # No one can edit user profiles

    def has_add_permission(self, request):
        return False  # No one can add user profiles


admin.site.site_header = "My Shop Admin"
admin.site.site_title = "My Shop Portal"
admin.site.index_title = "Welcome to My Shop Dashboard"
