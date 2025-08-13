from django.db import models
from django.conf import settings
from accounts.models import CustomUser

class UserAuditLog(models.Model):
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ])
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    old_details_of_affected_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    new_details_of_affected_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.old_details_of_affected_user.first_name} {self.old_details_of_affected_user.last_name} by {self.performed_by or 'Administrator'} at {self.timestamp}"
