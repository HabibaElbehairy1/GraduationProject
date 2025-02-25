from django.db import models
from django.conf import settings  # استخدم django.conf بدلاً من استيراد settings مباشرة
import uuid

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID يحسن الأمان ولكن يقلل الأداء قليلاً
    post_name = models.CharField(max_length=50, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username}"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField مناسب هنا لزيادة الأداء
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # صحح الـ related_name إلى صيغة الجمع
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.post_name}"
