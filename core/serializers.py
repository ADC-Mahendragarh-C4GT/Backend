from rest_framework import serializers
from .models import *
from accounts.serializers import UserSerializer

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
        fields =  '__all__'
        read_only_fields = ['road', 'contractor']
    def create(self, validated_data):
        road_data = self.initial_data['road']
        contractor_data = self.initial_data['contractor']
        print("Road Data:-----------------", road_data)
        print("Contractor Data:-----------------", contractor_data)
        road = Road.objects.get(unique_code=road_data['unique_code'])
        contractor = Contractor.objects.get(contractor_name=contractor_data['contractor_name'])

        return InfraWork.objects.create(
            road=road,
            contractor=contractor,
            **validated_data
        )
    

    # def create(self, validated_data):
    #     road_data = validated_data.pop('road')
    #     contractor_data = validated_data.pop('contractor')
    #     print("Road Data:-----------------", road_data)
    #     print("Contractor Data:-----------------", contractor_data)
    #     try:
    #         road = Road.objects.get(unique_code=road_data['unique_code'])
    #     except Road.DoesNotExist:
    #         raise serializers.ValidationError({'road': 'Road with this ID does not exist'})

    #     try:
    #         contractor = Contractor.objects.get(contractor_name=contractor_data['contractor_name'])
    #     except Contractor.DoesNotExist:
    #         raise serializers.ValidationError({'contractor': 'Contractor with this ID does not exist'})

    #     return InfraWork.objects.create(
    #         road=road,
    #         contractor=contractor,
    #         **validated_data
    #     )


    
class UpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Update
        fields = '__all__'

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