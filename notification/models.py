from django.db import models
from ecomApp.models import CustomUser

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user_id=models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, default='unread')  # Assuming 'status' can be 'unread' or 'read'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Create your models here.
