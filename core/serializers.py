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
    road = RoadSerializer()
    contractor = ContractorSerializer()

    class Meta:
        model = InfraWork
        fields = '__all__'

class UpdateSerializer(serializers.ModelSerializer):
    work = InfraWorkSerializer()

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
