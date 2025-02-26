from django.contrib import admin 
from django.contrib.auth import get_user_model
from .models import UserProfile
# Register your models here.

User = get_user_model()
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user','image')



admin.site.site_header = "My Shop Admin"
admin.site.site_title = "My Shop Portal"
admin.site.index_title = "Welcome to My Shop Dashboard"


