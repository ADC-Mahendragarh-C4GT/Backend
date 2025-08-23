from rest_framework import serializers
from .models import *
from accounts.serializers import UserSerializer
import json
from audit.models import *

class RoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = '__all__'
        

class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = '__all__'


class InfraWorkSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Update
        fields = '__all__'

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
    update = UpdateSerializer()
    infra_work = InfraWorkSerializer()
    commenter = UserSerializer()
    class Meta:
        model = Comments
        fields = '__all__'

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['infra_work', 'update', 'comment_text']

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required to comment.")
        validated_data['commenter'] = user
        return super().create(validated_data)


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