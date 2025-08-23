from django.db import models
from django.conf import settings
from accounts.models import CustomUser
import json

class UserAuditLog(models.Model):
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ])
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_audit_logs')
    old_details_of_affected_user = models.TextField()
    new_details_of_affected_user = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_old_details(self, data: dict):
        self.old_details_of_affected_user = json.dumps(data)

    def get_old_details(self) -> dict:
        return json.loads(self.old_details_of_affected_user) if self.old_details_of_affected_user else {}

    def set_new_details(self, data: dict):
        self.new_details_of_affected_user = json.dumps(data)

    def get_new_details(self) -> dict:
        return json.loads(self.new_details_of_affected_user) if self.new_details_of_affected_user else {}

    def __str__(self):
        old_details = self.get_old_details()
        new_details = self.get_new_details()
        performed_by_user = self.performed_by

        old_user_name = f"{old_details.get('first_name', '')} {old_details.get('last_name', '')}".strip()
        new_user_name = f"{new_details.get('first_name', '')} {new_details.get('last_name', '')}".strip()

        affected_user_name = old_user_name or new_user_name or "Unknown User"
        performed_by_name = f"{performed_by_user.first_name} {performed_by_user.last_name}" if performed_by_user else "Administrator"

        return f"{self.action} User details by {performed_by_name} at {self.timestamp}"


class RoadAuditLog(models.Model):
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ])
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='road_audit_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    old_details_of_affected_road = models.TextField()
    new_details_of_affected_road = models.TextField()
    
    def __str__(self):
        performed_by_user = self.performed_by
        performed_by_name = f"{performed_by_user.first_name} {performed_by_user.last_name}" if performed_by_user else "Administrator"
        return f"{self.action} Road details by {performed_by_name} at {self.timestamp}"

class ContracterAuditLog(models.Model):
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ])
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracter_audit_logs')
    old_details_of_affected_contracter = models.TextField()
    new_details_of_affected_contracter = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_old_details(self, data: dict):
        self.old_details_of_affected_contracter = json.dumps(data)

    def get_old_details(self) -> dict:
        return json.loads(self.old_details_of_affected_contracter) if self.old_details_of_affected_contracter else {}

    def set_new_details(self, data: dict):
        self.new_details_of_affected_contracter = json.dumps(data)

    def get_new_details(self) -> dict:
        return json.loads(self.new_details_of_affected_contracter) if self.new_details_of_affected_contracter else {}

    def __str__(self):
        performed_by_user = self.performed_by

        performed_by_name = f"{performed_by_user.first_name} {performed_by_user.last_name}" if performed_by_user else "Administrator"

        return f"{self.action} Contracter details by {performed_by_name} at {self.timestamp}"
    
    