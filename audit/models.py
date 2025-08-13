from django.db import models
from django.conf import settings
from accounts.models import CustomUser

class UserAuditLog(models.Model):
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ])
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_by')
    old_details_of_affected_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='old_details')
    new_details_of_affected_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_details')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        old_user = self.old_details_of_affected_user
        performed_by_user = self.performed_by

        old_user_name = f"{old_user.first_name} {old_user.last_name}" if old_user else "Unknown User"
        performed_by_name = f"{performed_by_user.first_name} {performed_by_user.last_name}" if performed_by_user else "Administrator"

        return f"{self.action} on {old_user_name} by {performed_by_name} at {self.timestamp}"

