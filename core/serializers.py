from rest_framework import serializers
from .models import Road, Vendor, InfraWork, Update

class RoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = '__all__'

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class InfraWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfraWork
        fields = '__all__'

class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = '__all__'
