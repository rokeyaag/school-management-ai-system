from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'target_role', 'attachment',
                  'is_active', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']