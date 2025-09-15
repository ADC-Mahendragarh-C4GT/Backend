from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializes import *
from .models import *

class AuditReportView(APIView):
    def get(self, request):
        serializer = AuditLogReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        logs_by_model = {
            "User": UserAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
            "Road": RoadAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
            "Contractor": ContracterAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
            "InfraWork": InfraWorkAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
            "Update": UpdateAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
            "Comment": CommentAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
            "OtherDepartment": OtherDepartmentRequestAuditLog.objects.filter(timestamp__range=(start_date, end_date)),
        }

        data = {
            model: AuditLogSerializer(qs, many=True).data
            for model, qs in logs_by_model.items()
        }

        return Response({
            "status": True,
            "message": "Audit Report fetched",
            "data": data,
        })  