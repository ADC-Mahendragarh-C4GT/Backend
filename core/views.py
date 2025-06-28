from rest_framework import viewsets
from .models import *
from .serializers import *

class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

class InfraWorkViewSet(viewsets.ModelViewSet):
    queryset = InfraWork.objects.all()
    serializer_class = InfraWorkSerializer

class UpdateViewSet(viewsets.ModelViewSet):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer
