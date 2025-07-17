from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = settings.USER_TYPE_CHOICES

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='other')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
