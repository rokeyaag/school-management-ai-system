from rest_framework import serializers
from .models import CustomUser
from apps.tenants.models import School


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    school_slug = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'phone', 'role', 'password', 'school_slug']

    def create(self, validated_data):
        school_slug = validated_data.pop('school_slug', None)
        password = validated_data.pop('password')
        school = None
        if school_slug:
            try:
                school = School.objects.get(slug=school_slug, is_active=True)
            except School.DoesNotExist:
                raise serializers.ValidationError({'school_slug': 'School not found'})
        user = CustomUser.objects.create_user(
            password=password,
            school=school,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'avatar', 'school', 'school_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value