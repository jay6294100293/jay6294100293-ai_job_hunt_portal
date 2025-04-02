from django.db import models

# Create your models here.
# auth_app/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    api_key_limit = models.IntegerField(default=100)
    subscription_type = models.CharField(max_length=20, default='free')
    chatgpt_api_key = models.CharField(max_length=255, blank=True, null=True)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.email
