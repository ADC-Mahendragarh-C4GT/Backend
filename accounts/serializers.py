from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'user_type', 'phone_number']

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data.get('user_type', 'other'),
            phone_number=validated_data.get('phone_number')
        )


from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']
        user_type = data['user_type']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if user.user_type != user_type:
            raise serializers.ValidationError("Invalid user type")

        # Authenticate with username and password
        user = authenticate(username=user.username, password=password)
        if user and user.is_active:
            return user

        raise serializers.ValidationError("Invalid email or password")
