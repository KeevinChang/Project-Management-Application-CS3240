# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_pm_admin = models.BooleanField(default=False)  
    nickname = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Upload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)