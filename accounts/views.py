from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login
from .serializers import *
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully','status': True, "data" : serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'User registration failed','status': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')
        user = CustomUser.objects.filter(email=email, user_type=user_type).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'user_username':user.username,
                'userFirstName': user.first_name,
                'userLastName':user.last_name
            }, status=status.HTTP_200_OK)
        
        return Response({'message': 'Invalid Credentials','status': False}, status=status.HTTP_400_BAD_REQUEST)

        # serializer = LoginSerializer(data=data)
        # if serializer.is_valid():
        #     user = serializer.validated_data
        #     login(request, user)
        #     return Response({'message': 'Login successful'})
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = []

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = []

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class UserTypeListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        choices = [
            {"value": value, "label": label}
            for value, label in CustomUser.USER_TYPE_CHOICES
        ]
        return Response(choices)