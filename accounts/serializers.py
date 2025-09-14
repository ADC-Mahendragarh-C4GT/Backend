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

        isValidEmail = CustomUser.objects.filter(email=data['email']).exists()
        if isValidEmail:
            raise serializers.ValidationError("Email is already taken")

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

        changed_old_details = {}
        changed_new_details = {}
        changed_old_details["id"] = user.id
        changed_new_details["id"] = user.id
        changed_new_details["username"] = user.username
        changed_new_details["email"] = user.email
        changed_new_details["first_name"] = user.first_name
        changed_new_details["last_name"] = user.last_name
        changed_new_details["user_type"] = user.user_type
        changed_new_details["phone_number"] = user.phone_number

        audit = UserAuditLog.objects.create(
            action="CREATE",
            performed_by=performed_by_user,
            old_details_of_affected_user=json.dumps(changed_old_details),
            new_details_of_affected_user=json.dumps(changed_new_details)
        )
        return user
    
    
 

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    
from rest_framework import serializers

class WelcomeEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
