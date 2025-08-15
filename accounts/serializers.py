from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from audit.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    login_user = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        return super().validate(data)

    def create(self, data):
        login_user_data = data.pop("login_user", None)
        performed_by_user = None

        print("---------login_user_data-------------------", login_user_data)

        if login_user_data and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        user = CustomUser.objects.create_user(
            username=data['username'],
            email=data.get('email'),
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            user_type=data.get('user_type', 'other'),
            phone_number=data.get('phone_number')
        )
        print("------------performed_by_user---------", performed_by_user)

        audit = UserAuditLog.objects.create(
            action="CREATE",
            performed_by=performed_by_user,
            old_details_of_affected_user=None,
            new_details_of_affected_user=user
        )
        return user
 

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

