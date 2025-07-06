from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('JE', 'Junior Engineer'),
        ('AE', 'Assistant Engineer'),
        ('XEN', 'Executive Engineer'),
        ('SE', 'Superintending Engineer'),
        ('CE', 'Chief Engineer'),
        ('JCMC', 'Joint Commissioner, Municipal Corporation'),
        ('CMC', 'Commissioner, Municipal Corporation'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='other')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
