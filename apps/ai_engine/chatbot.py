from .groq_client import chat
from apps.students.models import Student
from apps.attendance.models import Attendance
from apps.exams.models import Marks
from apps.fees.models import FeePayment

def get_school_context(school, user):
    try:
        role = user.role
        context = f"School: {school.name}\nUser Role: {role}\n"

        if role in ['super_admin', 'school_admin']:
            students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
            student_list = '\n'.join([f"- {s.user.full_name} (ID: {s.student_id}, Class: {s.class_name.name if s.class_name else 'N/A'}, Roll: {s.roll or 'N/A'})" for s in students])
            total_att = Attendance.objects.filter(school=school).count()
            present = Attendance.objects.filter(school=school, status='present').count()
            att_rate = round((present / total_att * 100), 1) if total_att > 0 else 0
            due_fees = FeePayment.objects.filter(school=school, status='due').count()
            paid_fees = FeePayment.objects.filter(school=school, status='paid').count()
            context += f"""
Total Students: {students.count()}
Attendance Rate: {att_rate}%
Due Payments: {due_fees}
Paid Payments: {paid_fees}

Student List:
{student_list}
"""
        elif role == 'student':
            try:
                student = Student.objects.get(user=user, school=school)
                marks = Marks.objects.filter(student=student).select_related('subject', 'exam')
                marks_info = '\n'.join([f"- {m.subject.name}: {m.marks_obtained}/{m.total_marks} (Grade: {m.grade})" for m in marks])
                att = Attendance.objects.filter(student=student)
                present = att.filter(status='present').count()
                att_rate = round((present / att.count() * 100), 1) if att.count() > 0 else 0
                fees = FeePayment.objects.filter(student=student)
                due = fees.filter(status='due').count()
                context += f"""
Student: {student.user.full_name}
Class: {student.class_name.name if student.class_name else 'N/A'}
Roll: {student.roll or 'N/A'}
Attendance: {att_rate}%
Due Fees: {due}

Exam Results:
{marks_info if marks_info else 'No results yet'}
"""
            except Student.DoesNotExist:
                context += "Student profile not found."

        elif role == 'teacher':
            context += f"Teacher: {user.full_name}\n"

        return context
    except Exception as e:
        return f"School: {school.name}"

def school_chatbot(message, history=None, lang='en', school=None, user=None):
    if history is None:
        history = []

    context = get_school_context(school, user) if school and user else ""

    if lang == 'bn':
        system_prompt = f"""তুমি {school.name if school else 'এই স্কুলের'} একটি AI assistant।
বাংলায় উত্তর দাও। শুধুমাত্র নিচের real data ব্যবহার করো, কোনো fake data দেবে না।
যদি তথ্য না থাকে সৎভাবে বলো।

{context}"""
    else:
        system_prompt = f"""You are the AI assistant for {school.name if school else 'this school'}.
Answer based ONLY on the real data below. Never make up fake information.
If information is not available, say so honestly.

{context}"""

    messages = [{'role': 'system', 'content': system_prompt}]
    for h in history:
        messages.append({'role': h['role'], 'content': h['content']})
    messages.append({'role': 'user', 'content': message})
    response = chat(messages)
    return {'response': response, 'lang': lang}