from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.utils import timezone
from rest_framework.views import APIView
import csv
import random
import string

class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        instance = Road(**validated_data)  # construct an unsaved instance

        all_characters = (
            string.ascii_lowercase +
            string.ascii_uppercase +
            string.digits
        )

        flag = True
        while flag:
            specialCharactor = random.choice(all_characters)
            unique_code = (
                instance.state[0] +
                instance.district[0] +
                instance.area_name[0] +
                str(instance.length_km).split('.')[0] +
                specialCharactor
            )
            if not Road.objects.filter(unique_code=unique_code).exists():
                flag = False

        instance.unique_code = unique_code
        instance.save()

    

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer
    permission_classes=[IsAuthenticated]

class InfraWorkViewSet(viewsets.ModelViewSet):
    queryset = InfraWork.objects.all()
    serializer_class = InfraWorkSerializer

    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        # Custom endpoint to return all updates for this work without pagination.
        work = self.get_object()
        updates = Update.objects.filter(work=work).order_by('-update_date', '-progress_percent')
        serializer = UpdateSerializer(updates, many=True)
        return Response(serializer.data)

class UpdateViewSet(viewsets.ModelViewSet):
    queryset = Update.objects.all().order_by('-update_date')
    serializer_class = UpdateSerializer


from rest_framework import generics

class UpdateListView(generics.ListAPIView):
    queryset = InfraWork.objects.all().order_by('-start_date')
    serializer_class = InfraWorkSerializer


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer

    def get_queryset(self):
        queryset = Comments.objects.all().order_by('-comment_date')
        work_id = self.request.query_params.get('work_id')
        if work_id:
            queryset = queryset.filter(infra_work__id=work_id)
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentsSerializer 
    
class OtherDepartmentRequestViewSet(viewsets.ModelViewSet):
    queryset = OtherDepartmentRequest.objects.all()
    serializer_class = OtherDepartmentRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        instance = serializer.instance

        if not serializer.validated_data.get('response_by'):

            serializer.save(
                response_date=timezone.now(),
                
            )

        else:
            serializer.save()


class UploadCSVView(APIView):
    permission_classes = [IsAuthenticated]  # or [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                all_characters = (
                    string.ascii_lowercase +  
                    string.ascii_uppercase +  
                    string.digits  
                )
                flag = True
                while flag:
                    specialCharactor = random.choice(all_characters)
                    unique_code =( row['state'][0] + row['district'][0] + row['area_name'][0] + row['length_km'].split('.')[0] + specialCharactor)
                    # Check if this code already exists
                    if not Road.objects.filter(unique_code=unique_code).exists():
                        flag = False
                       
                Road.objects.create(
                    road_name=row['road_name'],
                    ward_number=row['ward_number'],
                    location=row['location'],
                    length_km=row['length_km'],
                    width_m=row['width_m'],
                    road_type=row['road_type'],
                    material_type=row['material_type'],
                    road_category=row['road_category'],
                    area_name = row['area_name'],
                    district = row['district'],
                    state = row['state'],
                    unique_code = unique_code,
                )

            return Response({"message": "CSV uploaded & saved successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
