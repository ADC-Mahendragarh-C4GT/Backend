from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

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