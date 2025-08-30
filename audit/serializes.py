from rest_framework import serializers

class AuditLogReportSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)

from rest_framework import serializers

class AuditLogSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()
    old_details = serializers.SerializerMethodField()
    new_details = serializers.SerializerMethodField()
    performed_by = serializers.SerializerMethodField()

    def get_old_details(self, obj):
        if hasattr(obj, "get_old_details"):
            return obj.get_old_details()
        # fallback if no helper method
        for field in obj._meta.fields:
            if field.name.startswith("old_details"):
                return getattr(obj, field.name, {})
        return {}

    def get_new_details(self, obj):
        if hasattr(obj, "get_new_details"):
            return obj.get_new_details()
        for field in obj._meta.fields:
            if field.name.startswith("new_details"):
                return getattr(obj, field.name, {})
        return {}

    def get_performed_by(self, obj):
        if obj.performed_by:
            return {
                "id": obj.performed_by.id,
                "username": obj.performed_by.username,
                "first_name": obj.performed_by.first_name,
                "last_name": obj.performed_by.last_name,
                "user_type": obj.performed_by.user_type,
            }
        return {"id": None, "username": "system", "first_name": "", "last_name": "", "user_type": ""}
