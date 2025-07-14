from rest_framework import serializers
from .models import Road, Contractor, InfraWork, Update

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
