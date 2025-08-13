from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login
from .serializers import *
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from audit.models import UserAuditLog



class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            UserAuditLog.objects.create(
                action="CREATE",
                performed_by=request.login_user if request.user.is_authenticated else None,
                old_details_of_affected_user=None,
                new_details_of_affected_user=user
            )

            return Response({'message': 'User registered successfully','status': True, "data" : serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'User registration failed','status': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')
        print("Email:------------------------- ", email)
        print("Password:------------------------- ", password)      
        print("User Type:------------------------- ", user_type)
        user = CustomUser.objects.filter(email=email, user_type=user_type).first()
        print("User:------------------------- ", user)
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

    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({
                "detail": "You are not authenticated."
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    

class UpdateUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def patch(self, request, user_id):
        print("Request Data:-------------------- ", request.data)
        print("User ID:-------------------- ", user_id)
        current_user = request.user
        if current_user.id == user_id:
            return Response({
                "message": "You can't change your own details. Please contact another JE to update your profile.",
                "status": False
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found", "status": False}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully", "status": True, "data": serializer.data})
        return Response({"message": "Update failed", "status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)