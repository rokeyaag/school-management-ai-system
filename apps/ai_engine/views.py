from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .groq_client import chat
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .performance import analyze_student_performance
from .chatbot import school_chatbot


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_performance(request, student_id):
    lang = request.query_params.get('lang', 'en')
    result = analyze_student_performance(student_id, request.user.school, lang)
    if 'error' in result:
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot(request):
    message = request.data.get('message', '')
    history = request.data.get('history', [])
    lang = request.data.get('lang', 'en')
    if not message:
        return Response({'error': 'message required'}, status=status.HTTP_400_BAD_REQUEST)
    result = school_chatbot(message, history, lang, school=request.user.school, user=request.user)
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lesson_plan(request):
    subject = request.data.get('subject', '')
    topic = request.data.get('topic', '')
    class_name = request.data.get('class_name', '')
    duration = request.data.get('duration', '45')
    lang = request.data.get('lang', 'en')
    school = request.user.school
    if lang == 'bn':
        prompt = f'You are a teacher at {school.name}. Create a detailed lesson plan in Bengali for teaching "{topic}" in {subject} for {class_name} students. Duration: {duration} minutes. Include: objectives, materials, introduction, main activities, assessment, and homework.'
    else:
        prompt = f'You are a teacher at {school.name}. Create a detailed lesson plan for teaching "{topic}" in {subject} for {class_name} students. Duration: {duration} minutes. Include: learning objectives, materials needed, introduction (5 min), main activities, assessment, and homework assignment.'
    messages = [{'role': 'user', 'content': prompt}]
    result = chat(messages)
    return Response({'plan': result})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def study_recommendation(request):
    lang = request.data.get('lang', 'en')
    student_id = request.data.get('student_id')
    school = request.user.school
    from apps.exams.models import Marks
    from apps.students.models import Student
    from apps.attendance.models import Attendance
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user)
            student_id = student.id
            student_name = student.user.full_name or str(student)
        except:
            student_name = 'Student'
    elif student_id:
        try:
            student = Student.objects.get(id=student_id)
            student_name = student.user.full_name or str(student)
        except:
            student_name = 'Student'
    else:
        student_name = 'the student'
    marks = Marks.objects.filter(student_id=student_id, exam__school=school) if student_id else Marks.objects.filter(exam__school=school)
    attendance = Attendance.objects.filter(student_id=student_id, school=school) if student_id else []
    marks_summary = []
    for m in marks[:20]:
        marks_summary.append(f"{m.subject.name}: {m.marks_obtained}/{m.total_marks} ({m.grade})")
    total_days = len(attendance)
    present_days = len([a for a in attendance if a.status == 'present'])
    absent_days = len([a for a in attendance if a.status == 'absent'])
    attendance_pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0
    fee_data = 'No fee data.'
    try:
        from apps.fees.models import FeePayment as Payment
        fees = Payment.objects.filter(student_id=student_id, school=school) if student_id else []
        if fees:
            paid = len([f for f in fees if f.status == 'paid'])
            due = len([f for f in fees if f.status == 'due'])
            fee_data = f'Paid: {paid}, Due: {due}'
    except:
        pass
    marks_data = "\n".join(marks_summary) if marks_summary else "No exam data yet."
    fee_info = fee_data
    attendance_data = f"Total: {total_days} days, Present: {present_days}, Absent: {absent_days}, Rate: {attendance_pct}%"
    if lang == 'bn':
        prompt = f'You are an educational advisor at {school.name}. Create a detailed personalized study recommendation in Bengali for {student_name}.\n\nExam Results:\n{marks_data}\n\nAttendance:\n{attendance_data}\n\nFee Status:\n{fee_info}\n\nProvide: 1) Subject-wise improvement tips 2) Study schedule 3) Attendance advice if needed 4) Overall motivation.'
    else:
        prompt = f'You are an educational advisor at {school.name}. Create a detailed personalized study recommendation for {student_name}.\n\nExam Results:\n{marks_data}\n\nAttendance:\n{attendance_data}\n\nFee Status:\n{fee_info}\n\nProvide: 1) Subject-wise improvement tips for weak subjects 2) Recommended daily study schedule 3) Attendance advice if needed 4) Overall encouragement. Note fee issues sensitively if any.'
    messages = [{'role': 'user', 'content': prompt}]
    result = chat(messages)
    return Response({'recommendation': result})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def school_health(request):
    lang = request.data.get('lang', 'en')
    school = request.user.school
    from apps.students.models import Student
    from apps.teachers.models import Teacher
    from apps.attendance.models import Attendance
    from apps.fees.models import FeePayment as Payment
    from apps.notices.models import Notice
    from apps.exams.models import Marks
    students = Student.objects.filter(school=school).count()
    teachers = Teacher.objects.filter(school=school).count()
    att = Attendance.objects.filter(school=school)
    total_att = att.count()
    present = att.filter(status='present').count()
    att_rate = round(present / total_att * 100, 1) if total_att > 0 else 0
    payments = Payment.objects.filter(school=school)
    paid = payments.filter(status='paid').count()
    due = payments.filter(status='due').count()
    notices = Notice.objects.filter(school=school, is_active=True).count()
    marks = Marks.objects.filter(exam__school=school)
    avg_marks = 0
    if marks.exists():
        total = sum(m.marks_obtained for m in marks if m.marks_obtained)
        avg_marks = round(total / marks.count(), 1)
    summary = f"School: {school.name}\nStudents: {students}, Teachers: {teachers}\nAttendance Rate: {att_rate}%\nFees Paid: {paid}, Due: {due}\nNotices: {notices}\nAvg Exam Score: {avg_marks}"
    if lang == 'bn':
        prompt = f'You are a school health analyst. Analyze this school data and provide a comprehensive health report in Bengali with recommendations.\n\n{summary}'
    else:
        prompt = f'You are a school health analyst. Analyze this school data and provide a comprehensive health report with key insights, concerns, and recommendations for improvement.\n\n{summary}'
    messages = [{'role': 'user', 'content': prompt}]
    result = chat(messages)
    return Response({'report': result})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def question_generator(request):
    subject = request.data.get('subject', '')
    class_name = request.data.get('class_name', '')
    topic = request.data.get('topic', '')
    difficulty = request.data.get('difficulty', 'medium')
    num_mcq = request.data.get('num_mcq', 5)
    num_short = request.data.get('num_short', 3)
    lang = request.data.get('lang', 'en')
    school = request.user.school

    if lang == 'bn':
        prompt = f'You are an experienced teacher at {school.name}. Generate exam questions in Bengali for:\nSubject: {subject}\nClass: {class_name}\nTopic: {topic}\nDifficulty: {difficulty}\n\nGenerate exactly:\n{num_mcq} MCQ questions (with 4 options A/B/C/D and correct answer)\n{num_short} Short questions (with model answers)\n\nFormat clearly with sections: MCQ Questions, Short Questions.'
    else:
        prompt = f'You are an experienced teacher at {school.name}. Generate exam questions for:\nSubject: {subject}\nClass: {class_name}\nTopic: {topic}\nDifficulty: {difficulty}\n\nGenerate exactly:\n{num_mcq} MCQ questions (with 4 options A/B/C/D and correct answer marked)\n{num_short} Short questions (with model answers)\n\nFormat clearly with sections: MCQ Questions, Short Questions.'

    messages = [{'role': 'user', 'content': prompt}]
    result = chat(messages)
    return Response({'questions': result})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_predictor(request):
    lang = request.data.get('lang', request.query_params.get('lang', 'en'))
    school = request.user.school
    from apps.students.models import Student
    from apps.attendance.models import Attendance

    students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
    at_risk = []
    good = []

    for student in students:
        att = Attendance.objects.filter(student=student, school=school)
        total = att.count()
        present = att.filter(status='present').count()
        absent = att.filter(status='absent').count()
        rate = round((present / total * 100), 1) if total > 0 else 0
        data = {
            'name': student.user.full_name,
            'class': student.class_name.name if student.class_name else 'N/A',
            'total': total,
            'present': present,
            'absent': absent,
            'rate': rate
        }
        if rate < 75 or absent >= 5:
            at_risk.append(data)
        else:
            good.append(data)

    at_risk_summary = '\n'.join([f"- {s['name']} (Class: {s['class']}, Rate: {s['rate']}%, Absent: {s['absent']} days)" for s in at_risk]) or 'None'
    good_summary = '\n'.join([f"- {s['name']} (Rate: {s['rate']}%)" for s in good]) or 'None'

    if lang == 'bn':
        prompt = f'তুমি {school.name} এর attendance analyst। নিচের data বিশ্লেষণ করে বাংলায় report দাও।\n\nAt-Risk Students (75% এর নিচে বা 5+ absent):\n{at_risk_summary}\n\nGood Attendance:\n{good_summary}\n\nপ্রতিটি at-risk student এর জন্য কারণ ও সমাধান দাও।'
    else:
        prompt = f'You are an attendance analyst for {school.name}. Analyze the data below and provide insights.\n\nAt-Risk Students (below 75% or 5+ absences):\n{at_risk_summary}\n\nGood Attendance Students:\n{good_summary}\n\nProvide: 1) Summary 2) Risk analysis for each at-risk student 3) Recommendations for improvement.'

    messages = [{'role': 'user', 'content': prompt}]
    from .groq_client import chat
    result = chat(messages)
    return Response({
        'at_risk': at_risk,
        'good': good,
        'analysis': result,
        'summary': {
            'total_students': len(at_risk) + len(good),
            'at_risk_count': len(at_risk),
            'good_count': len(good)
        }
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fee_defaulter(request):
    lang = request.query_params.get('lang', 'en')
    school = request.user.school
    from apps.students.models import Student
    from apps.fees.models import FeePayment

    students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
    defaulters = []
    good = []

    for student in students:
        fees = FeePayment.objects.filter(student=student, school=school)
        total = fees.count()
        paid = fees.filter(status='paid').count()
        due = fees.filter(status='due').count()
        due_amount = sum(f.amount for f in fees.filter(status='due'))
        paid_amount = sum(f.paid_amount or 0 for f in fees.filter(status='paid'))
        data = {
            'name': student.user.full_name,
            'class': student.class_name.name if student.class_name else 'N/A',
            'total': total,
            'paid': paid,
            'due': due,
            'due_amount': float(due_amount),
            'paid_amount': float(paid_amount),
        }
        if due > 0:
            defaulters.append(data)
        else:
            good.append(data)

    defaulter_summary = '\n'.join([f"- {s['name']} (Class: {s['class']}, Due: {s['due']} months, Amount: {s['due_amount']} BDT)" for s in defaulters]) or 'None'
    good_summary = '\n'.join([f"- {s['name']} (Paid: {s['paid']} months)" for s in good]) or 'None'

    if lang == 'bn':
        prompt = f'তুমি {school.name} এর fee analyst। নিচের data বিশ্লেষণ করে বাংলায় report দাও।\n\nFee Defaulters:\n{defaulter_summary}\n\nRegular Payers:\n{good_summary}\n\nপ্রতিটি defaulter এর জন্য সমাধান ও action plan দাও।'
    else:
        prompt = f'You are a fee analyst for {school.name}. Analyze the fee data below.\n\nFee Defaulters:\n{defaulter_summary}\n\nRegular Payers:\n{good_summary}\n\nProvide: 1) Summary 2) Risk level for each defaulter 3) Recommended actions for fee recovery.'

    messages = [{'role': 'user', 'content': prompt}]
    from .groq_client import chat
    result = chat(messages)
    return Response({
        'defaulters': defaulters,
        'good': good,
        'analysis': result,
        'summary': {
            'total_students': len(defaulters) + len(good),
            'defaulter_count': len(defaulters),
            'good_count': len(good),
            'total_due_amount': sum(s['due_amount'] for s in defaulters),
        }
    })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def parent_progress_report(request):
    lang = request.data.get('lang', 'en')
    student_id = request.data.get('student_id')
    school = request.user.school
    from apps.students.models import Student
    from apps.attendance.models import Attendance
    from apps.exams.models import Marks
    from apps.fees.models import FeePayment

    try:
        student = Student.objects.get(id=student_id, school=school)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

    marks = Marks.objects.filter(student=student).select_related('subject', 'exam')
    marks_info = '\n'.join([f"- {m.subject.name}: {m.marks_obtained}/{m.total_marks} (Grade: {m.grade})" for m in marks])

    att = Attendance.objects.filter(student=student, school=school)
    total = att.count()
    present = att.filter(status='present').count()
    absent = att.filter(status='absent').count()
    att_rate = round((present / total * 100), 1) if total > 0 else 0

    fees = FeePayment.objects.filter(student=student, school=school)
    paid = fees.filter(status='paid').count()
    due = fees.filter(status='due').count()
    due_amount = float(sum(f.amount for f in fees.filter(status='due')))

    student_name = student.user.full_name
    class_name = student.class_name.name if student.class_name else 'N/A'
    roll = student.roll or 'N/A'

    if lang == 'bn':
        prompt = f'''তুমি {school.name} এর একজন শিক্ষক। {student_name} এর অভিভাবকের জন্য বাংলায় একটি সম্পূর্ণ progress report লিখো।

ছাত্র/ছাত্রীর তথ্য:
নাম: {student_name}
শ্রেণী: {class_name}
রোল: {roll}

পরীক্ষার ফলাফল:
{marks_info if marks_info else 'কোনো ফলাফল নেই'}

উপস্থিতি:
মোট: {total} দিন | উপস্থিত: {present} | অনুপস্থিত: {absent} | হার: {att_rate}%

ফি অবস্থা:
পরিশোধিত: {paid} | বাকি: {due} | বাকি পরিমাণ: ৳{due_amount}

একটি professional ও সহানুভূতিশীল report লিখো যেখানে থাকবে:
১) সামগ্রিক মূল্যায়ন
২) বিষয়ভিত্তিক মন্তব্য
৩) উপস্থিতি মন্তব্য
৪) অভিভাবকের জন্য পরামর্শ
৫) উৎসাহমূলক বার্তা'''
    else:
        prompt = f'''You are a teacher at {school.name}. Write a complete parent progress report for {student_name}.

Student Information:
Name: {student_name}
Class: {class_name}
Roll: {roll}

Exam Results:
{marks_info if marks_info else 'No exam results yet'}

Attendance:
Total: {total} days | Present: {present} | Absent: {absent} | Rate: {att_rate}%

Fee Status:
Paid: {paid} | Due: {due} | Due Amount: ৳{due_amount}

Write a professional and caring report including:
1) Overall Assessment
2) Subject-wise comments
3) Attendance remarks
4) Recommendations for parents
5) Encouraging closing message'''

    messages = [{'role': 'user', 'content': prompt}]
    from .groq_client import chat
    result = chat(messages)
    return Response({
        'report': result,
        'student': {
            'name': student_name,
            'class': class_name,
            'roll': roll,
            'attendance_rate': att_rate,
            'fees_due': due,
            'due_amount': due_amount,
        }
    })