from urllib import request
from rest_framework import serializers
from .models import *
from accounts.serializers import UserSerializer
import json
from audit.models import *
from drf_extra_fields.fields import Base64ImageField

class RoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = '__all__'
        

class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = '__all__'


class InfraWorkSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    class Meta:
        model = InfraWork
        fields = '__all__'
        read_only_fields = ['road', 'contractor']

    def create(self, validated_data):
        road_data = self.initial_data.get('road')
        contractor_data = self.initial_data.get('contractor')

        try:
            road = Road.objects.get(unique_code=road_data['unique_code'])
        except Road.DoesNotExist:
            raise serializers.ValidationError({'road': 'Road with this unique_code does not exist'})

        try:
            contractor = Contractor.objects.get(contractor_name=contractor_data['contractor_name'])
        except Contractor.DoesNotExist:
            raise serializers.ValidationError({'contractor': 'Contractor with this contractor_name does not exist'})

        instance = InfraWork.objects.create(
            road=road,
            contractor=contractor,
            **validated_data
        )
        Update.objects.create(
            work=instance,
            status_note="InfraWork created.",
            progress_percent=instance.progress_percent,
            image=instance.image,
            latitude=instance.latitude,
            longitude=instance.longitude,
        )


        login_user = self.context['request'].data.get("login_user") if 'request' in self.context else None
        performed_by_user = None
        if login_user:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        old_details_snapshot = {"id": instance.id}
        new_details_snapshot = {
            "id": instance.id,
            "road": instance.road.id if instance.road else None,
            "phase": instance.phase,
            "description": instance.description,
            "cost": str(instance.cost),
            "defect_liability_period": instance.defect_liability_period,
            "image": instance.image.url if instance.image else None,
            "latitude": str(instance.latitude) if instance.latitude else None,
            "longitude": str(instance.longitude) if instance.longitude else None,
            "start_date": str(instance.start_date),
            "end_date": str(instance.end_date) if instance.end_date else None,
            "progress_percent": instance.progress_percent,
            "completedOrpending": instance.completedOrpending,
            "contractor": instance.contractor.id if instance.contractor else None,
        }
        InfraWorkAuditLog.objects.create(
            action="CREATE",
            performed_by=performed_by_user,
            old_details_of_affected_infra_work=json.dumps(old_details_snapshot),
            new_details_of_affected_infra_work=json.dumps(new_details_snapshot),
        )

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Update
        fields = '__all__'
        extra_fields = ['image_url']

    def get_image_url(self, obj):
        if obj.image:
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    
    def create(self, validated_data):
        workId = self.initial_data.get('work')
        roadId = self.initial_data.get('road')

        try:
            road = Road.objects.get(id=roadId)
            work = InfraWork.objects.filter(id=workId, road=road).first()

        except InfraWork.DoesNotExist:
            raise serializers.ValidationError({'work': 'InfraWork with this id does not exist'})
        
        instance = Update.objects.create(
            **validated_data
        )

        login_user = self.context['request'].data.get("login_user") if 'request' in self.context else None
        performed_by_user = None
        if login_user:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        old_details_snapshot = {"id": instance.id}
        new_details_snapshot = {
            "id": instance.id,
            "work": instance.work.id if instance.work else None,
            "update_date": str(instance.update_date),
            "status_note": str(instance.status_note),
            "progress_percent": str(instance.progress_percent),
            "image": instance.image.url if instance.image else None,
            "latitude": str(instance.latitude) if instance.latitude else None,
            "longitude": str(instance.longitude) if instance.longitude else None,
        }

        UpdateAuditLog.objects.create(
            action="CREATE",
            performed_by=performed_by_user,
            old_details_of_affected_update=json.dumps(old_details_snapshot),
            new_details_of_affected_update=json.dumps(new_details_snapshot),
        )

        return instance
    

class CommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comments
        fields = '__all__'

    def create(self, validated_data):
        print("validateddata ---------------", validated_data)
        request = self.context.get('request')
        login_user = request.data.get("login_user") if request else None
        print("request------------------", request.data)
        performed_by_user = None

        if login_user:
            try:
                performed_by_user = CustomUser.objects.get(id=login_user["id"])
            except CustomUser.DoesNotExist:
                performed_by_user = None

        instance = Comments.objects.create(**validated_data)

        update = self.initial_data.get('update')
        infra_work = self.initial_data.get('infra_work')

        old_details_snapshot = {"id": instance.id}
        new_details_snapshot = {
            "id": instance.id,
            "infra_work": infra_work,
            "update": update,
            "comment_text": instance.comment_text,
            "commenter": str(login_user["id"]) if login_user else None,
        }

        CommentAuditLog.objects.create(
            action="CREATE",
            performed_by=performed_by_user,
            old_details_of_affected_comment=json.dumps(old_details_snapshot),
            new_details_of_affected_comment=json.dumps(new_details_snapshot),
        )

        return instance




class OtherDepartmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherDepartmentRequest
        fields = '__all__'

    

class InfraWorksByRoadSerializer(serializers.ModelSerializer):
    road = RoadSerializer()
    contractor = ContractorSerializer()

    class Meta:
        model = InfraWork
        fields = '__all__'
        read_only_fields = ['road', 'contractor']