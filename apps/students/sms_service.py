import requests
from django.conf import settings


def send_sms(mobile, message):
    """
    Send SMS via SSL Wireless
    Set in settings.py:
    SMS_API_URL = "https://smpp.sslwireless.com/api/v3/send-sms"
    SMS_API_TOKEN = "your-api-token"
    SMS_SID = "your-sid"
    SMS_ENABLED = True
    """
    if not getattr(settings, 'SMS_ENABLED', False):
        print(f"[SMS MOCK] To: {mobile} | Message: {message}")
        return True

    try:
        response = requests.post(
            getattr(settings, 'SMS_API_URL', ''),
            json={
                "api_token": getattr(settings, 'SMS_API_TOKEN', ''),
                "sid": getattr(settings, 'SMS_SID', ''),
                "msisdn": mobile.replace('-', '').replace('+88', '').replace(' ', ''),
                "sms": message,
                "csms_id": f"MSG_{mobile}_{message[:10]}"
            },
            timeout=10
        )
        data = response.json()
        return data.get('status_code') == 200
    except Exception as e:
        print(f"SMS Error: {e}")
        return False


def send_absence_sms(student):
    """Send absence notification to parents"""
    name = student.user.full_name
    class_name = student.class_name.name if student.class_name else ''
    roll = student.roll or ''
    message = f"Dear Parent, {name} (Class: {class_name}, Roll: {roll}) was ABSENT today. Please contact school for details."

    sent = False
    if student.father_mobile:
        send_sms(student.father_mobile, message)
        sent = True
    if student.mother_mobile:
        send_sms(student.mother_mobile, message)
        sent = True
    if student.guardian_mobile:
        send_sms(student.guardian_mobile, message)
        sent = True
    return sent


def send_fee_reminder_sms(student, amount):
    """Send fee reminder to parents"""
    name = student.user.full_name
    message = f"Dear Parent, Fee payment of BDT {amount} is due for {name}. Please pay at school or contact us."

    if student.father_mobile:
        send_sms(student.father_mobile, message)
    elif student.mother_mobile:
        send_sms(student.mother_mobile, message)


def send_result_sms(student, exam_name, gpa):
    """Send exam result to parents"""
    name = student.user.full_name
    message = f"Dear Parent, {name}'s result for {exam_name} is out. GPA: {gpa}. Login to parent portal for details."

    if student.father_mobile:
        send_sms(student.father_mobile, message)
    elif student.mother_mobile:
        send_sms(student.mother_mobile, message)