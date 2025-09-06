from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import request_password_reset, validate_reset_token, reset_password


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-types/', UserTypeListView.as_view(), name='user-types'),
    path("updateUser/<int:user_id>/", UpdateUserView.as_view(), name="updateUser"),
    path('Users/', UsersView.as_view(), name='Users'),
    path('get-login-user/', GetLoginUserView.as_view(), name='get_login_user'),
    path('deleteUser/<int:user_id>/', DeleteUserView.as_view(), name='delete-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("request-password-reset/", request_password_reset, name="request-password-reset"),
    path("validate-reset-token/<uidb64>/<token>/", validate_reset_token, name="validate-reset-token"),
    path("reset-password/<uidb64>/<token>/", reset_password, name="reset-password"),

]
