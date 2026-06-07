from rest_framework import serializers
from .models import Student, Guardian
from apps.authentication.serializers import UserSerializer


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['id', 'name', 'phone', 'email', 'relation', 'occupation', 'is_primary']


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    section_display = serializers.CharField(source='section.name', read_only=True)
    guardians = GuardianSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'full_name', 'email', 'avatar',
            'class_name', 'class_name_display', 'section', 'section_display',
            'dob', 'gender', 'blood_group', 'address', 'religion',
            'is_active', 'created_at', 'guardians'
        ]
        read_only_fields = ['id', 'created_at']


class StudentCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=6)
    student_id = serializers.CharField()
    class_name = serializers.IntegerField(required=False, allow_null=True)
    section = serializers.IntegerField(required=False, allow_null=True)
    dob = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'], required=False, allow_blank=True)
    blood_group = serializers.CharField(required=False, allow_blank=True)
    address = serializers.TextField(required=False, allow_blank=True) if False else serializers.CharField(required=False, allow_blank=True)
    religion = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        from apps.authentication.models import CustomUser
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def validate_student_id(self, value):
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError('Student ID already exists')
        return value