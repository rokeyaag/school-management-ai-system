from rest_framework import serializers
from .models import Teacher
from apps.authentication.models import CustomUser


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone', 'avatar',
            'specialization', 'qualification', 'join_date', 'salary',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class TeacherCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=6)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    qualification = serializers.CharField(required=False, allow_blank=True)
    join_date = serializers.DateField(required=False, allow_null=True)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    avatar = serializers.URLField(required=False, allow_blank=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value