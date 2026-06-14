from .groq_client import chat
from apps.students.models import Student
from apps.attendance.models import Attendance
from apps.exams.models import Marks, Exam
from apps.fees.models import FeePayment
from apps.notices.models import Notice
from apps.teachers.models import Teacher
from apps.academics.models import Class
from django.utils import timezone

def get_school_context(school, user):
    try:
        role = user.role
        context = f"School: {school.name}\nUser Role: {role}\n"

        if role in ['super_admin', 'school_admin']:
            students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
            student_list = '\n'.join([f"- {s.user.full_name} (Class: {s.class_name.name if s.class_name else 'N/A'}, Roll: {s.roll or 'N/A'})" for s in students])

            total_att = Attendance.objects.filter(school=school).count()
            present_att = Attendance.objects.filter(school=school, status='present').count()
            att_rate = round((present_att / total_att * 100), 1) if total_att > 0 else 0
            today = timezone.now().date()
            today_att = Attendance.objects.filter(school=school, date=today)
            today_present = today_att.filter(status='present').count()
            today_total = today_att.count()

            due_fees = FeePayment.objects.filter(school=school, status='due').count()
            paid_fees = FeePayment.objects.filter(school=school, status='paid').count()

            teachers = Teacher.objects.filter(school=school, is_active=True).select_related('user')
            teacher_list = '\n'.join([f"- {t.user.full_name} (Specialization: {t.specialization or 'N/A'})" for t in teachers])

            exams = Exam.objects.filter(school=school).order_by('-start_date')[:10]
            exam_list = '\n'.join([f"- {e.name} | Class: {e.class_name.name if e.class_name else 'N/A'} | Start: {e.start_date} | Published: {e.is_published}" for e in exams])

            notices = Notice.objects.filter(school=school, is_active=True).order_by('-created_at')[:5]
            notice_list = '\n'.join([f"- {n.title} ({n.created_at.strftime('%d %b %Y')})" for n in notices])

            marks = Marks.objects.filter(exam__school=school)
            avg = 0
            if marks.exists():
                avg = round(sum(m.marks_obtained for m in marks if m.marks_obtained) / marks.count(), 1)

            classes = Class.objects.filter(school=school)
            class_stats = []
            for c in classes:
                c_marks = Marks.objects.filter(exam__school=school, student__class_name=c)
                if c_marks.exists():
                    c_avg = round(sum(m.marks_obtained for m in c_marks if m.marks_obtained) / c_marks.count(), 1)
                    class_stats.append(f"- {c.name}: Avg {c_avg}")
            class_stats_str = '\n'.join(class_stats) if class_stats else 'No data'

            context += f"""
=== STUDENTS ({students.count()} total) ===
{student_list}

=== TEACHERS ({teachers.count()} total) ===
{teacher_list}

=== ATTENDANCE ===
Overall Rate: {att_rate}%
Today ({today}): {today_present}/{today_total} present

=== EXAMS ===
{exam_list if exam_list else 'No exams yet'}

=== FEES ===
Paid: {paid_fees}, Due: {due_fees}

=== NOTICES ===
{notice_list if notice_list else 'No notices'}

=== EXAM PERFORMANCE ===
Overall Avg Score: {avg}
Class-wise Avg:
{class_stats_str}
"""

        elif role == 'student':
            try:
                student = Student.objects.get(user=user, school=school)
                marks = Marks.objects.filter(student=student).select_related('subject', 'exam')
                marks_info = '\n'.join([f"- {m.subject.name}: {m.marks_obtained}/{m.total_marks} (Grade: {m.grade})" for m in marks])
                att = Attendance.objects.filter(student=student)
                present = att.filter(status='present').count()
                absent = att.filter(status='absent').count()
                att_rate = round((present / att.count() * 100), 1) if att.count() > 0 else 0
                fees = FeePayment.objects.filter(student=student)
                due = fees.filter(status='due').count()
                paid = fees.filter(status='paid').count()
                notices = Notice.objects.filter(school=school, is_active=True).order_by('-created_at')[:5]
                notice_list = '\n'.join([f"- {n.title}" for n in notices])
                exams = Exam.objects.filter(school=school, class_name=student.class_name).order_by('-start_date')[:5]
                exam_list = '\n'.join([f"- {e.name} | Date: {e.start_date} | Published: {e.is_published}" for e in exams])
                context += f"""
Student: {student.user.full_name}
Class: {student.class_name.name if student.class_name else 'N/A'}
Roll: {student.roll or 'N/A'}

=== ATTENDANCE ===
Rate: {att_rate}% | Present: {present} | Absent: {absent}

=== EXAM RESULTS ===
{marks_info if marks_info else 'No results yet'}

=== MY EXAMS ===
{exam_list if exam_list else 'No exams'}

=== FEES ===
Paid: {paid} | Due: {due}

=== RECENT NOTICES ===
{notice_list if notice_list else 'No notices'}
"""
            except Student.DoesNotExist:
                context += "Student profile not found."

        elif role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user, school=school)
                students = Student.objects.filter(school=school, is_active=True)
                today = timezone.now().date()
                today_att = Attendance.objects.filter(school=school, date=today)
                today_present = today_att.filter(status='present').count()
                exams = Exam.objects.filter(school=school).order_by('-start_date')[:5]
                exam_list = '\n'.join([f"- {e.name} | Class: {e.class_name.name if e.class_name else 'N/A'} | Date: {e.start_date}" for e in exams])
                notices = Notice.objects.filter(school=school, is_active=True).order_by('-created_at')[:5]
                notice_list = '\n'.join([f"- {n.title}" for n in notices])
                context += f"""
Teacher: {teacher.user.full_name}
Specialization: {teacher.specialization or 'N/A'}

=== SCHOOL INFO ===
Total Students: {students.count()}
Today Attendance: {today_present}/{today_att.count()} present

=== RECENT EXAMS ===
{exam_list if exam_list else 'No exams'}

=== NOTICES ===
{notice_list if notice_list else 'No notices'}
"""
            except Teacher.DoesNotExist:
                context += f"Teacher: {user.full_name}\n"

        return context
    except Exception as e:
        return f"School: {school.name} | Error: {str(e)}"

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