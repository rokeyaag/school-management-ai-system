from .groq_client import chat
from apps.students.models import Student
from apps.exams.models import Marks
from apps.attendance.models import Attendance


def analyze_student_performance(student_id, school, lang='en'):
    student = Student.objects.filter(id=student_id, school=school).first()
    if not student:
        return {'error': 'Student not found'}

    # Attendance data
    total_att = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status='present').count()
    att_pct = round((present / total_att * 100), 1) if total_att > 0 else 0

    # Marks data
    marks_qs = Marks.objects.filter(student=student).select_related('subject', 'exam')
    subject_data = {}
    for m in marks_qs:
        name = m.subject.name
        if name not in subject_data:
            subject_data[name] = []
        pct = round(float(m.marks_obtained) / float(m.total_marks) * 100, 1)
        subject_data[name].append(pct)

    subject_avg = {s: round(sum(v)/len(v), 1) for s, v in subject_data.items()}
    weak_subjects = [s for s, avg in subject_avg.items() if avg < 50]
    strong_subjects = [s for s, avg in subject_avg.items() if avg >= 75]

    if lang == 'bn':
        prompt = f"""
তুমি একজন শিক্ষা বিশেষজ্ঞ AI। নিচের তথ্যের উপর ভিত্তি করে বাংলায় একটি সংক্ষিপ্ত performance analysis দাও:

ছাত্র: {student.user.full_name}
উপস্থিতি: {att_pct}%
বিষয়ভিত্তিক গড়: {subject_avg}
দুর্বল বিষয়: {weak_subjects}
শক্তিশালী বিষয়: {strong_subjects}

৩-৪ বাক্যে বিশ্লেষণ ও পরামর্শ দাও।
"""
    else:
        prompt = f"""
You are an educational AI expert. Based on the following data, provide a brief performance analysis:

Student: {student.user.full_name}
Attendance: {att_pct}%
Subject averages: {subject_avg}
Weak subjects: {weak_subjects}
Strong subjects: {strong_subjects}

Provide analysis and advice in 3-4 sentences.
"""

    messages = [{'role': 'user', 'content': prompt}]
    analysis = chat(messages)

    return {
        'student_name': student.user.full_name,
        'attendance_percentage': att_pct,
        'subject_averages': subject_avg,
        'weak_subjects': weak_subjects,
        'strong_subjects': strong_subjects,
        'ai_analysis': analysis,
    }