import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from groq import Groq
import requests
from apps.tenants.models import School
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.attendance.models import Attendance
from apps.notices.models import Notice
from datetime import date

SLACK_BOT_TOKEN = "xoxb-11355788501991-11365329464595-d7mIlsBy0LWMGXfMlQ3LrjDX"
GROQ_API_KEY = "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"

def ai_generate(prompt):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful school management assistant. Reply in Bengali when asked in Bengali. Keep responses concise."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

def get_school_stats():
    school = School.objects.first()
    if not school:
        return "কোনো স্কুল পাওয়া যায়নি।"
    students = Student.objects.filter(school=school).count()
    teachers = Teacher.objects.filter(school=school).count()
    today_attendance = Attendance.objects.filter(school=school, date=date.today()).count()
    notices = Notice.objects.filter(school=school).count()
    return f"🏫 *{school.name}*\n👨‍🎓 Students: {students}\n👨‍🏫 Teachers: {teachers}\n📋 আজকের Attendance: {today_attendance}\n📢 মোট Notice: {notices}"

def get_recent_notices():
    school = School.objects.first()
    if not school:
        return "কোনো স্কুল পাওয়া যায়নি।"
    notices = Notice.objects.filter(school=school).order_by('-created_at')[:3]
    if not notices:
        return "কোনো notice নেই।"
    msg = "📢 *সর্বশেষ Notices:*\n"
    for n in notices:
        msg += f"• *{n.title}*\n"
    return msg

@csrf_exempt
@require_http_methods(["POST"])
def slack_commands(request):
    text = request.POST.get("text", "").strip().lower()
    user_name = request.POST.get("user_name", "")

    if text in ["stats", "তথ্য", "attendance", "উপস্থিতি"]:
        msg = get_school_stats()
        return JsonResponse({"response_type": "in_channel", "text": msg})

    elif text in ["notice", "নোটিশ"]:
        msg = get_recent_notices()
        return JsonResponse({"response_type": "in_channel", "text": msg})

    elif text.startswith("notice create "):
        topic = text[14:]
        notice_text = ai_generate(f"Write a short school notice in Bengali about: {topic}")
        msg = f"📢 *AI Generated Notice:*\n{notice_text}"
        return JsonResponse({"response_type": "in_channel", "text": msg})

    elif text.startswith("ask "):
        question = text[4:]
        answer = ai_generate(question)
        msg = f"🤖 *AI উত্তর:*\n{answer}"
        return JsonResponse({"response_type": "in_channel", "text": msg})

    elif text in ["report", "রিপোর্ট"]:
        school = School.objects.first()
        students = Student.objects.filter(school=school).count() if school else 0
        teachers = Teacher.objects.filter(school=school).count() if school else 0
        prompt = f"Generate a brief school health report in Bengali. School has {students} students and {teachers} teachers."
        report = ai_generate(prompt)
        msg = f"📊 *AI School Report:*\n{report}"
        return JsonResponse({"response_type": "in_channel", "text": msg})

    elif text in ["help", "সাহায্য"]:
        msg = """*🏫 School Management Bot Commands:*
- `/school stats` - স্কুলের সামগ্রিক তথ্য
- `/school attendance` - উপস্থিতি রিপোর্ট
- `/school notice` - সর্বশেষ notices
- `/school notice create [বিষয়]` - AI দিয়ে notice তৈরি
- `/school report` - AI school report
- `/school ask [প্রশ্ন]` - AI কে প্রশ্ন করুন
- `/school help` - সাহায্য"""
        return JsonResponse({"response_type": "in_channel", "text": msg})

    else:
        msg = "❓ `/school help` লিখুন সাহায্যের জন্য।"
        return JsonResponse({"response_type": "ephemeral", "text": msg})