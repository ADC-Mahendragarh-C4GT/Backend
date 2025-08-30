from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializes import *
from .models import *

class AuditReportView(APIView):
    def get(self, request):
        serializer = AuditLogReportSerializer(data=request.query_params)

        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            all_logs = list(UserAuditLog.objects.all()) + \
                       list(RoadAuditLog.objects.all()) + \
                       list(ContracterAuditLog.objects.all()) + \
                       list(InfraWorkAuditLog.objects.all()) + \
                       list(UpdateAuditLog.objects.all()) + \
                       list(CommentAuditLog.objects.all()) + \
                       list(OtherDepartmentRequestAuditLog.objects.all())

            filtered_logs = [
                log for log in all_logs
                if start_date <= log.timestamp <= end_date
            ]   

            serialized_logs = AuditLogSerializer(filtered_logs, many=True).data

            return Response({
                "message": "Audit Report fetched successfully",
                "status": True,
                "data": serialized_logs,
                "start_date": start_date,
                "end_date": end_date,
                "count": len(filtered_logs),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
