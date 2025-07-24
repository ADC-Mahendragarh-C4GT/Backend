from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'roads', RoadViewSet)
router.register('contractors', ContractorViewSet)
router.register(r'infra-works', InfraWorkViewSet)
router.register('updates', UpdateViewSet)
router.register(r'comments', CommentsViewSet, basename='comment')
router.register(r'other-department-requests', OtherDepartmentRequestViewSet, basename= 'otherDepartmentForm')



urlpatterns = [
    path('api/updatesPage/', UpdateListView.as_view(), name='update-list'),
    path('upload-csv/', UploadCSVView.as_view(), name='upload-csv'),
    path('api/', include(router.urls)),
]
