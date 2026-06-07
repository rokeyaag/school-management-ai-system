from .groq_client import chat


def school_chatbot(message, history=None, lang='en'):
    if history is None:
        history = []

    if lang == 'bn':
        system_prompt = """তুমি একটি স্কুল ম্যানেজমেন্ট AI assistant। 
তুমি বাংলায় উত্তর দেবে। শুধুমাত্র স্কুল সম্পর্কিত প্রশ্নের উত্তর দাও যেমন:
- ছাত্র-ছাত্রীদের পারফরম্যান্স
- উপস্থিতি
- পরীক্ষার ফলাফল
- ফি সম্পর্কিত তথ্য
- নোটিশ ও ঘোষণা"""
    else:
        system_prompt = """You are a school management AI assistant.
Answer only school-related questions such as:
- Student performance
- Attendance
- Exam results
- Fee information
- Notices and announcements"""

    messages = [{'role': 'system', 'content': system_prompt}]
    for h in history:
        messages.append({'role': h['role'], 'content': h['content']})
    messages.append({'role': 'user', 'content': message})

    response = chat(messages)
    return {
        'response': response,
        'lang': lang,
    }