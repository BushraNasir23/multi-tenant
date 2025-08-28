from rest_framework import serializers
from .models import Task
from accounts.serializers import UserSerializer

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assigned_to', 
                 'assigned_to_detail', 'created_by', 'created_by_detail', 
                 'company', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'company', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assigned_to']

    def validate_assigned_to(self, value):
        request_user = self.context['request'].user
        if request_user.company and value.company != request_user.company:
            raise serializers.ValidationError(
                "Cannot assign task to user from different company"
            )
        return value

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
