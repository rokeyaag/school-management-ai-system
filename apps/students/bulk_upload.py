import csv
import io
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .models import Student
from .views import generate_student_id
from apps.authentication.models import CustomUser
from apps.academics.models import Class


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bulk_upload_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_template.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'full_name', 'email', 'password', 'class_name', 'roll',
        'father_name', 'father_mobile', 'mother_name', 'mother_mobile',
        'gender', 'religion', 'student_id'
    ])
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_upload_students(request):
    file = request.FILES.get('file')
    school = request.user.school

    if not file:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    if not file.name.endswith('.csv'):
        return Response({'error': 'Only CSV files allowed'}, status=status.HTTP_400_BAD_REQUEST)

    decoded = file.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))

    required = ['full_name', 'email', 'password', 'class_name']
    headers = reader.fieldnames or []
    missing = [f for f in required if f not in headers]
    if missing:
        return Response({'error': f'Missing columns: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)

    created = []
    errors = []

    for i, row in enumerate(reader, start=2):
        full_name = row.get('full_name', '').strip()
        email = row.get('email', '').strip()
        password = row.get('password', '').strip()
        class_name = row.get('class_name', '').strip()

        row_errors = []
        if not full_name:
            row_errors.append('full_name required')
        if not email:
            row_errors.append('email required')
        if not password:
            row_errors.append('password required')
        if not class_name:
            row_errors.append('class_name required')

        if row_errors:
            errors.append({'row': i, 'name': full_name, 'errors': row_errors})
            continue

        if CustomUser.objects.filter(email=email).exists():
            errors.append({'row': i, 'name': full_name, 'errors': [f'Email {email} already exists']})
            continue

        class_obj = Class.objects.filter(name__iexact=class_name, school=school).first()
        if not class_obj:
            errors.append({'row': i, 'name': full_name, 'errors': [f'Class "{class_name}" not found']})
            continue

        try:
            user = CustomUser.objects.create_user(
                email=email,
                full_name=full_name,
                phone=row.get('father_mobile', '').strip(),
                password=password,
                role='student',
                school=school
            )
            student_id = row.get('student_id', '').strip() or generate_student_id(school)
            Student.objects.create(
                user=user,
                school=school,
                student_id=student_id,
                class_name=class_obj,
                roll=row.get('roll', '').strip(),
                father_name=row.get('father_name', '').strip(),
                father_mobile=row.get('father_mobile', '').strip(),
                mother_name=row.get('mother_name', '').strip(),
                mother_mobile=row.get('mother_mobile', '').strip(),
                gender=row.get('gender', '').strip(),
                religion=row.get('religion', '').strip(),
            )
            created.append({'name': full_name, 'email': email, 'class': class_name})
        except Exception as e:
            errors.append({'row': i, 'name': full_name, 'errors': [str(e)]})

    return Response({
        'success': True,
        'created_count': len(created),
        'error_count': len(errors),
        'created': created,
        'errors': errors,
    }, status=status.HTTP_201_CREATED)