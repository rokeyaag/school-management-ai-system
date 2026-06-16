# 🏫 School Management AI - Slack Bot

## 🎯 Problem Statement
স্কুল পরিচালনায় প্রতিদিন অনেক তথ্য manage করতে হয় — attendance, notices, reports। এই bot Slack এর মাধ্যমে সব তথ্য এক জায়গায় এনে AI দিয়ে স্বয়ংক্রিয় করে।

## 💡 Solution
**School Management Bot** — একটি AI-powered Slack Bot যা Django backend এর সাথে connected এবং Groq AI (LLaMA 4) ব্যবহার করে।

## ✨ Features

### Slack Commands
| Command | Description |
|---------|-------------|
| `/school stats` | স্কুলের সামগ্রিক তথ্য |
| `/school attendance` | উপস্থিতি রিপোর্ট |
| `/school notice` | সর্বশেষ notices |
| `/school notice create [বিষয়]` | AI দিয়ে notice তৈরি |
| `/school report` | AI school health report |
| `/school ask [প্রশ্ন]` | AI কে যেকোনো প্রশ্ন |
| `/school help` | সব commands |

### Web Application Features
- 📊 Dashboard with real-time charts
- 👨‍🎓 Student & Teacher Management
- 📋 Attendance Tracking
- 📝 Exam & Marks Management
- 💰 Fee & Accounting Management
- 📢 AI Notice Generator
- 🖼️ Photo Gallery
- 🤖 5 AI Features (Lesson Plan, Study Recommendation, School Health, Report Card, Question Generator)
- 🔐 Multi-tenant with Role-based Access (Super Admin, School Admin, Teacher, Student)

## 🛠️ Tech Stack
- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React + Vite + TailwindCSS
- **Database:** PostgreSQL
- **AI:** Groq API (meta-llama/llama-4-scout-17b-16e-instruct)
- **Storage:** Cloudinary
- **Slack:** Slack Bolt API
- **Deployment:** Railway

## 🚀 How It Works
1. User types `/school [command]` in Slack
2. Slack sends request to Django backend
3. Backend fetches data from PostgreSQL
4. AI generates intelligent response using Groq/LLaMA 4
5. Response sent back to Slack channel

## 📦 Installation

```bash
git clone https://github.com/rokeyaag/school-management-ai-system
cd school-management-ai-system
pip install -r requirements.txt
```

### Environment Variables (.env)
```
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
SLACK_BOT_TOKEN=your_slack_bot_token
```

```bash
python manage.py migrate
python manage.py runserver
```

## 🎥 Demo
- **Slack Workspace:** School Management AI
- **Bot:** School Management Bot
- **Commands:** `/school help` to get started

## 👨‍💻 Developer
**Mohammad Lutfor Rahman**
- Full-Stack AI Developer
- Generative AI Engineering Course — ICTBD Bangladesh

## 📄 License
MIT License