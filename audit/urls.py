from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('report/', AuditReportView.as_view(), name='audit_report'),

]
