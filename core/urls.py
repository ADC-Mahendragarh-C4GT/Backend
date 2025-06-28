from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('roads', RoadViewSet)
router.register('contractors', ContractorViewSet)
router.register('infra-works', InfraWorkViewSet)
router.register('updates', UpdateViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
