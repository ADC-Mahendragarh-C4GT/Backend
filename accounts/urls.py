from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-types/', UserTypeListView.as_view(), name='user-types'),
    path("updateUser/<int:user_id>/", UpdateUserView.as_view(), name="updateUser"),
    path('Users/', UsersView.as_view(), name='Users'),
]
