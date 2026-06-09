from rest_framework import serializers
from .models import Student, Guardian
from apps.authentication.models import CustomUser


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['id', 'name', 'phone', 'email', 'relation', 'occupation', 'is_primary']


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    section_display = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'roll', 'full_name', 'name_bangla',
            'email', 'phone', 'avatar', 'photo',
            'class_name', 'class_name_display', 'section', 'section_display',
            'dob', 'birth_reg_no', 'gender', 'blood_group', 'religion',
            'present_address', 'permanent_address',
            'father_name', 'father_nid', 'father_mobile',
            'mother_name', 'mother_nid', 'mother_mobile',
            'guardian_name', 'guardian_mobile', 'guardian_relation',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StudentCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=6)
    student_id = serializers.CharField(required=False, allow_blank=True)
    roll = serializers.CharField(required=False, allow_blank=True)
    name_bangla = serializers.CharField(required=False, allow_blank=True)
    dob = serializers.DateField(required=False, allow_null=True)
    birth_reg_no = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'], required=False, allow_blank=True)
    blood_group = serializers.CharField(required=False, allow_blank=True)
    religion = serializers.CharField(required=False, allow_blank=True)
    photo = serializers.URLField(required=False, allow_blank=True)
    class_name = serializers.IntegerField(required=False, allow_null=True)
    section = serializers.IntegerField(required=False, allow_null=True)
    present_address = serializers.CharField(required=False, allow_blank=True)
    permanent_address = serializers.CharField(required=False, allow_blank=True)
    father_name = serializers.CharField(required=False, allow_blank=True)
    father_nid = serializers.CharField(required=False, allow_blank=True)
    father_mobile = serializers.CharField(required=False, allow_blank=True)
    mother_name = serializers.CharField(required=False, allow_blank=True)
    mother_nid = serializers.CharField(required=False, allow_blank=True)
    mother_mobile = serializers.CharField(required=False, allow_blank=True)
    guardian_name = serializers.CharField(required=False, allow_blank=True)
    guardian_mobile = serializers.CharField(required=False, allow_blank=True)
    guardian_relation = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value