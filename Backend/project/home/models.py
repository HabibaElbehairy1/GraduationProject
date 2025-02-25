
from django.conf import settings
from django.db import models
from django.db import models
import uuid

class ClintReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.TextField()
    date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='ClintReview/') 

    def __str__(self):
        return f"Review by {self.user.first_name} {self.user.last_name}"



class Contact(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField مناسب هنا لزيادة الأداء
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
