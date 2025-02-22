
from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user','post_name', 'content', 'created_at', 'updated_at')
    search_fields = ('content', 'user__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'created_at', 'updated_at')
    search_fields = ('comment', 'user__username', 'post__id')