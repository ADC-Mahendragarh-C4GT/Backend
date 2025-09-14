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
from audit.models import *
from django.core.serializers.json import DjangoJSONEncoder


all_characters = (
            string.ascii_uppercase +
            string.digits
        )


class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        instance = Road(**validated_data)  

        flag = True
        while flag:
            specialCharactor = random.choice(all_characters)
            prefix = (
                instance.state[0].upper() +
                instance.district[0].upper() +
                instance.area_name[0].upper() +
                str(instance.length_km).split('.')[0]
            )

            # Count existing roads with same prefix
            count = Road.objects.filter(unique_code__startswith=prefix).count() + 1

            # Format sequential suffix with leading zeros (001, 002…)
            unique_code = f"{prefix}-{count:03d}"
            
            if not Road.objects.filter(unique_code=unique_code).exists():
                flag = False

        instance.unique_code = unique_code
        instance.save()
       

        login_user_id = self.request.data.get("login_user")
        performed_by_user = None
        print("---login_user_id-------------------",login_user_id)
        if login_user_id:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_id)
            except CustomUser.DoesNotExist:
                performed_by_user = None

        old_details_snapshot = {"id": instance.id}

        new_details_snapshot = {
                    "id": instance.id,
                    "unique_code": instance.unique_code,
                    "road_name": instance.road_name,
                    "ward_number": instance.ward_number,
                    "location": instance.location,
                    "length_km": instance.length_km,
                    "width_m": instance.width_m,
                    "road_type": instance.road_type,
                    "material_type": instance.material_type,
                    "road_category": instance.road_category,
                    "area_name": instance.area_name,
                    "state": instance.state,
                    "district": instance.district,
        }


        RoadAuditLog.objects.create(
                    action="CREATE",
                    performed_by=performed_by_user,
                    old_details_of_affected_road=json.dumps(str(old_details_snapshot)),  # no old details on CREATE
                    new_details_of_affected_road=json.dumps(str(new_details_snapshot)),
        )
        return instance


    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        old_data = {
            "state": instance.state,
            "district": instance.district,
            "area_name": instance.area_name,
            "length_km": instance.length_km,
            "unique_code": instance.unique_code
        }

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        has_changed = (
            old_data["state"] != updated_instance.state or
            old_data["district"] != updated_instance.district or
            old_data["area_name"] != updated_instance.area_name or
            old_data["length_km"] != updated_instance.length_km
        )

        if has_changed:
            flag = True
            while flag:
                prefix = (
                    updated_instance.state[0].upper() +
                    updated_instance.district[0].upper() +
                    updated_instance.area_name[0].upper() +
                    str(updated_instance.length_km).split('.')[0]
                )

                count = Road.objects.filter(unique_code__startswith=prefix).exclude(pk=updated_instance.pk).count() + 1
                
            updated_instance.unique_code = f"{prefix}-{count:03d}"
            updated_instance.save()

        new_data = {
            "state": updated_instance.state,
            "district": updated_instance.district,
            "area_name": updated_instance.area_name,
            "length_km": updated_instance.length_km,
            "unique_code": updated_instance.unique_code
        }

        login_user_data = request.data.get("login_user", None)
        performed_by_user = None
        if login_user_data and isinstance(login_user_data, dict) and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        changed_old_details = {}
        changed_new_details = {}
        for field in new_data.keys():
            old_value = old_data.get(field)
            new_value = new_data.get(field)
            if new_value:
                changed_old_details[field] = old_value
                changed_new_details[field] = new_value

        if changed_old_details or changed_new_details:
            RoadAuditLog.objects.create(
                action="UPDATE",
                performed_by=performed_by_user,
                old_details_of_affected_road=json.dumps(changed_old_details, default=str),
                new_details_of_affected_road=json.dumps(changed_new_details, default=str)
            )

        return Response(self.get_serializer(updated_instance).data)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        print("------------instance -------------", instance)

        login_user_data = request.data.get("login_user", None)
        performed_by_user = None
        if login_user_data and isinstance(login_user_data, dict) and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        
        print('----------------instanceID', instance.unique_code)
        
        changed_old_details = {}
        changed_new_details = {}
        changed_old_details["id"] = instance.id
        changed_old_details["unique_code"] = instance.unique_code
        changed_old_details["road_name"] = instance.road_name
        changed_old_details["ward_number"] = instance.ward_number
        changed_old_details["location"] = instance.location
        changed_old_details["length_km"] = instance.length_km
        changed_old_details["width_m"] = instance.width_m
        changed_old_details["road_type"] = instance.road_type
        changed_old_details["material_type"] = instance.material_type
        changed_old_details["road_category"] = instance.road_category
        changed_old_details["area_name"] = instance.area_name
        changed_old_details["state"] = instance.state
        changed_old_details["district"] = instance.district

        changed_new_details["id"] = instance.id
        
        RoadAuditLog.objects.create(
            action="DELETE",
            performed_by=performed_by_user,
            old_details_of_affected_road=json.dumps(str(changed_old_details)),
            new_details_of_affected_road=json.dumps(str(changed_new_details))
        )


        instance.isActive = False
        instance.save()

        return Response(
            {"detail": f"Road '{instance.road_name}' deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


    

    

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        instance = Contractor(**validated_data) 
        
        instance.save()
        
        login_user = self.request.data.get("login_user")
        if login_user:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None
        
        old_details_snapshot = {"id": instance.id}
        new_details_snapshot = {
            "id": instance.id,
            "contractor_name": instance.contractor_name,
            "contact_person": instance.contact_person,
            "contact_number": instance.contact_number,
            "email": instance.email,
            "address": instance.address,
        }

        ContracterAuditLog.objects.create(
            action="CREATE",
            performed_by=performed_by_user,
            old_details_of_affected_contracter=json.dumps(str(old_details_snapshot)),
            new_details_of_affected_contracter=json.dumps(str(new_details_snapshot)),
        )
      

        return instance
    
    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        old_data = {
            "contractor_name": instance.contractor_name,
            "contact_person": instance.contact_person,
            "contact_number": instance.contact_number,
            "email": instance.email,
            "address": instance.address,
        }

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        new_data = {
            "contractor_name": updated_instance.contractor_name,
            "contact_person": updated_instance.contact_person,
            "contact_number": updated_instance.contact_number,
            "email": updated_instance.email,
            "address": updated_instance.address,
        }

        login_user_data = request.data.get("login_user", None)
        performed_by_user = None
        if login_user_data and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        changed_old_details = {}
        changed_new_details = {}
        for field in new_data.keys():
            old_value = old_data.get(field)
            new_value = new_data.get(field)
            if new_value:
                changed_old_details[field] = old_value
                changed_new_details[field] = new_value

        if changed_old_details or changed_new_details:
            ContracterAuditLog.objects.create(
                action="UPDATE",
                performed_by=performed_by_user,
                old_details_of_affected_contracter=json.dumps(changed_old_details, default=str),
                new_details_of_affected_contracter=json.dumps(changed_new_details, default=str)
            )

        return Response(self.get_serializer(updated_instance).data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        login_user_data = request.data.get("login_user", None)
        performed_by_user = None
        if login_user_data and "id" in login_user_data:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user_data["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        changed_old_details = {}
        changed_new_details = {}
        changed_old_details["id"] = instance.id
        changed_old_details["contractor_name"] = instance.contractor_name
        changed_old_details["contact_person"] = instance.contact_person
        changed_old_details["contact_number"] = instance.contact_number
        changed_old_details["email"] = instance.email
        changed_old_details["address"] = instance.address

        changed_new_details["id"] = instance.id

        ContracterAuditLog.objects.create(
            action="DELETE",
            performed_by=performed_by_user,
            old_details_of_affected_contracter=json.dumps(str(changed_old_details)),
            new_details_of_affected_contracter=json.dumps(str(changed_new_details))
        )

        instance.isActive = False
        instance.save()

        return Response(
            {"detail": f"Contractor '{instance.contractor_name}' deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class InfraWorkViewSet(viewsets.ModelViewSet):
    queryset = InfraWork.objects.all()
    serializer_class = InfraWorkSerializer

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        work = self.get_object()
        updates = Update.objects.filter(work=work).order_by('-update_date', '-progress_percent')
        serializer = UpdateSerializer(updates, many=True)
        return Response(serializer.data)
    
from django.utils.timezone import now  # Ensure timezone-aware datetime

class UpdateViewSet(viewsets.ModelViewSet):
    queryset = Update.objects.all().order_by('-update_date')
    serializer_class = UpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        work_id = self.request.data.get('work')
        progress = self.request.data.get('progress_percent')

        if not work_id:
            raise serializers.ValidationError({"work": "This field is required."})

        try:
            work_instance = InfraWork.objects.filter(id=work_id).first()
            if not work_instance:
                raise serializers.ValidationError({"work": f"No InfraWork found with id {work_id}"})
        except InfraWork.DoesNotExist:
            raise serializers.ValidationError({"work": f"No InfraWork found with id {work_id}"})

        update_instance = serializer.save(work=work_instance)

        if str(progress) == "100":
            work_instance.completedOrpending = 'Completed'
            work_instance.progress_percent = 100
            work_instance.end_date = update_instance.update_date or now()
            work_instance.save()




from rest_framework import generics

class UpdateListView(generics.ListAPIView):
    queryset = InfraWork.objects.all().order_by('-start_date', '-id')
    serializer_class = InfraWorkSerializer

    

class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    

    def get_queryset(self):
        queryset = Comments.objects.all().order_by('-comment_date')
        work_id = self.request.query_params.get('work_id')
        if work_id:
            queryset = queryset.filter(infra_work__id=work_id)

        print("queryset:------------------------------", queryset)

        instance = {
            "queryset": queryset
        }
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        login_user = request.data.get("login_user")
        performed_by_user = None

        if login_user:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        old_details_snapshot = {
            "id": instance.id,
            "infra_work": instance.infra_work.id if instance.infra_work else None,
            "update": instance.update.id if instance.update else None,
            "comment_text": instance.comment_text,
            "commenter": instance.commenter.id if instance.commenter else None,
            "deletedBy": performed_by_user.id if performed_by_user else None,
            "update": instance.update.id if instance.update else None

        }

        instance.isActive = False
        instance.deletedBy = performed_by_user
        instance.save()

        CommentAuditLog.objects.create(
            action="DELETE",
            performed_by=performed_by_user,
            old_details_of_affected_comment=json.dumps(old_details_snapshot),
            new_details_of_affected_comment=json.dumps(old_details_snapshot),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class OtherDepartmentRequestViewSet(viewsets.ModelViewSet):
    queryset = OtherDepartmentRequest.objects.all()
    serializer_class = OtherDepartmentRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        instance = serializer.save()

        
        old_details_snapshot = {"id": instance.id}
        new_details_snapshot = {
           "id": instance.id,
           "contact_info": instance.contact_info,
           "department_name": instance.department_name,
           "requested_by": instance.requested_by,
           "work_description": instance.work_description,
           "pdfDescription": instance.pdfDescription.url if instance.pdfDescription else None,
           "road": instance.road.id if instance.road else None,
           "status": instance.status,
           "submitted_at":  instance.submitted_at.isoformat() if instance.submitted_at else None,
        }
        OtherDepartmentRequestAuditLog.objects.create(
            action="CREATE",
            performed_by=None,
            old_details_of_affected_request=json.dumps(old_details_snapshot),
            new_details_of_affected_request=json.dumps(new_details_snapshot),
        )

        return instance

    def perform_update(self, serializer):
        instance = serializer.instance

        if not serializer.validated_data.get('response_by'):

            serializer.save(
                response_date=timezone.now(),
                
            )

        else:
            serializer.save()
        
        login_user = self.request.data.get("login_user")
        if login_user:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None
        
        old_details_snapshot = {
           "id": instance.id,
           "contact_info": instance.contact_info,
           "department_name": instance.department_name,
           "requested_by": instance.requested_by,
           "work_description": instance.work_description,
           "pdfDescription": instance.pdfDescription.url if instance.pdfDescription else None,
           "road": instance.road.id if instance.road else None,
           "status": instance.status,
           "submitted_at": instance.submitted_at,
        }

        new_details_snapshot = {
            "id": instance.id,
           "contact_info": instance.contact_info,
           "department_name": instance.department_name,
           "requested_by": instance.requested_by,
           "work_description": instance.work_description,
           "pdfDescription": instance.pdfDescription.url if instance.pdfDescription else None,
           "road": instance.road.id if instance.road else None,
           "status": instance.status,
           "submitted_at": instance.submitted_at,
        }

        OtherDepartmentRequestAuditLog.objects.create(
            action="UPDATE",
            performed_by=performed_by_user,
            old_details_of_affected_request=json.dumps(old_details_snapshot, cls=DjangoJSONEncoder),
            new_details_of_affected_request=json.dumps(new_details_snapshot, cls=DjangoJSONEncoder),
        )


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
                    prefix = (
                        row['state'][0].upper() +
                        row['district'][0].upper() +
                        row['area_name'][0].upper() +
                        str(row['length_km']).split('.')[0]
                    )
                    count = Road.objects.filter(unique_code__startswith=prefix).count() + 1
                    unique_code = f"{prefix}-{count:03d}"


                    # Check if this code already exists
                    if not Road.objects.filter(unique_code=unique_code).exists():
                        flag = False
                       
                instance = Road.objects.create(
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

                login_user_id = request.data.get("login_user")
                performed_by_user = None
                print("---login_user_id-------------------",login_user_id)
                print("---instance road-------------------",instance.road_name)
                if login_user_id:
                    try:
                        performed_by_user = CustomUser.objects.get(id=login_user_id)
                    except CustomUser.DoesNotExist:
                        performed_by_user = None

                old_details_snapshot = {"id": instance.id}

                new_details_snapshot = {
                    "id": instance.id,
                    "unique_code": instance.unique_code,
                    "road_name": instance.road_name,
                    "ward_number": instance.ward_number,
                    "location": instance.location,
                    "length_km": instance.length_km,
                    "width_m": instance.width_m,
                    "road_type": instance.road_type,
                    "material_type": instance.material_type,
                    "road_category": instance.road_category,
                    "area_name": instance.area_name,
                    "state": instance.state,
                    "district": instance.district,
                }


                RoadAuditLog.objects.create(
                    action="CREATE",
                    performed_by=performed_by_user,
                    old_details_of_affected_road=json.dumps(str(old_details_snapshot)),  # no old details on CREATE
                    new_details_of_affected_road=json.dumps(str(new_details_snapshot)),
                )



            return Response({"message": "CSV uploaded & saved successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InfraWorksByRoadViewSet(viewsets.ModelViewSet):
    serializer_class = InfraWorksByRoadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        road_id = self.request.query_params.get('road_id')
        print("Road ID:-----------------", road_id)
        if road_id:
            return InfraWork.objects.filter(road__id=road_id).order_by('-start_date')
        return InfraWork.objects.all().order_by('-start_date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

from django.core.mail import send_mail  
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
SENDERS_EMAIL = settings.SENDERS_EMAIL

@api_view(["POST"])
@permission_classes([AllowAny])
def send_xen_email(request):

    serializer = OtherDepartmentRequestEmailSerializer(data=request.data)
    if serializer.is_valid():
        formData = serializer.validated_data['formData']
        emails = serializer.validated_data['emails']
        road_data = formData.get("road")
        
        subject = f"New Department Request: {formData.get('departmentName')}"
        body = f"""
A new request has been submitted from {formData.get('departmentName')} for your review in Suvidha Manch Platform.

Department Name: {formData.get('departmentName')}
Requested By: {formData.get('requestedBy')}
Road Id and Name : {road_data.get("unique_code")}, {road_data.get("road_name")}
Contact Info: {formData.get('contactInfo')}
Proposed Work: {formData.get('workDescription')}
District = {road_data.get("district")}
State = {road_data.get("state")}

Please review and take necessary action.
"""
        for e in emails:
            send_mail(
                subject,
                body,
                SENDERS_EMAIL,
                [e],
                fail_silently=False
            )
        return Response({"message": "Email sent to XEN successfully"})
        
    return Response(serializer.errors, status=400)