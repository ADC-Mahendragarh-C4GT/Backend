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

    