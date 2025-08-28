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
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():

            user = serializer.save()
            

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
                'id':user.id,
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
        isActiveUserOnly = request.user.isActive
        if not isActiveUserOnly:
            return Response({"detail": "User is not existed or deleted."}, status=status.HTTP_403_FORBIDDEN)
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
        current_user = request.user
        if current_user.id == user_id:
            return Response({
                "message": "You can't change your own details. Please contact another JE to update your profile.",
                "status": False
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found or deleted", "status": False}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "message": "Update failed",
                "status": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        login_user_data = request.data.get("login_user", None)
        performed_by_user = None
        if login_user_data and isinstance(login_user_data, dict) and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        old_details_snapshot = CustomUser.objects.filter(pk=user.pk).values().first()

        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()

        new_details_snapshot = request.data 

        changed_old_details = {}
        changed_new_details = {}
        for field, new_value in new_details_snapshot.items():
            if field == "login_user":  # skip login_user field
                continue
            old_value = old_details_snapshot.get(field)
            if old_value != new_value:
                changed_old_details[field] = old_value
                changed_new_details[field] = new_value

        UserAuditLog.objects.create(
            action="UPDATE",
            performed_by=performed_by_user,
            old_details_of_affected_user=json.dumps(changed_old_details),
            new_details_of_affected_user=json.dumps(changed_new_details)
        )

        return Response({
            "message": "User updated successfully",
            "status": True,
            "data": UserUpdateSerializer(user).data
        })



class UsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all().filter(isActive=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    

class GetLoginUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get("id") 
        if not user_id:
            return Response({"error": "id is required"}, status=400)

        login_user = CustomUser.objects.filter(id=user_id, isActive=True).first()
        if not login_user:
            return Response({"error": "User not found or deleted"}, status=404)

        serializer = UserSerializer(login_user)
        return Response(serializer.data)


class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "User not found", "status": False},
                status=status.HTTP_404_NOT_FOUND
            )
        
        login_user_data = request.data.get("login_user", None)
        performed_by_user = None
        if login_user_data and isinstance(login_user_data, dict) and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        
        changed_old_details = {}
        changed_new_details = {}
        changed_old_details["id"] = user.id
        changed_new_details["id"] = user.id
        
        UserAuditLog.objects.create(
            action="DELETE",
            performed_by=performed_by_user,
            old_details_of_affected_user=json.dumps(changed_old_details),
            new_details_of_affected_user=json.dumps(changed_new_details)
        )

        user.isActive = False
        user.save()
        return Response(
            {"message": "User deleted successfully", "status": True},
            status=status.HTTP_200_OK
        )