# School Management AI SaaS Platform

A multi-tenant school management system with 10+ AI-powered features, built for Bangladeshi educational institutions. The platform combines traditional school administration tools with AI-driven analytics, a Textbook Knowledge Base with RAG (Retrieval-Augmented Generation), and a Slack bot integration.

## Features

### Core Management

- **Multi-Tenant Architecture** — Each school operates in an isolated tenant with its own data, users, and settings. Super admins approve and manage schools.
- **Authentication & Roles** — JWT-based auth with five roles: Super Admin, School Admin, Teacher, Student, and Parent. Custom email backend.
- **Student Management** — Full student profiles with personal, family, and guardian info. Bulk CSV import, auto-generated IDs, PDF student lists, and photo ID card generation.
- **Teacher Management** — Teacher profiles with qualifications, specializations, salary tracking, and auto-generated employee IDs.
- **Academics** — Classes, sections, subjects, and timetable management with teacher assignments.
- **Attendance** — Bulk attendance marking, per-student and per-date reports. Automatic SMS notifications to parents on absence.
- **Exams & Results** — Exam scheduling, marks entry with auto-calculated grades and GPA (Bangladesh grading scale). PDF report cards.
- **Fee Management** — Fee categories, payment tracking (cash, bKash, Nagad, bank), due/paid/partial status, and per-student fee reports.
- **Notices** — School-wide announcements with role-based targeting (all, students, teachers, parents). Read/unread tracking.
- **Gallery** — Photo albums with Cloudinary-hosted images. Admin-only upload and management.
- **Parent Portal** — Parents view their children's attendance, exam results, fee status, and school notices via phone number linking.
- **SMS Notifications** — Absence alerts, fee reminders, and result notifications via SSL Wireless SMS gateway.

### AI-Powered Features (Groq + Llama 4 Scout)

1. **AI Chatbot** — Context-aware school assistant that answers questions using real school data (students, attendance, exams, fees, notices). Role-aware responses for admins, teachers, and students.
2. **Student Performance Analysis** — AI-generated analysis of individual student performance across subjects with improvement recommendations.
3. **Study Recommendations** — Personalized study plans based on exam results, attendance patterns, and fee status.
4. **AI Notice Generator** — Auto-generates professional school notices in English or Bengali from a topic prompt.
5. **Lesson Plan Generator** — Creates detailed lesson plans with objectives, activities, assessments, and homework.
6. **Exam Question Generator** — Generates MCQ and short questions with answers for any subject, class, and difficulty level.
7. **Attendance Predictor** — Identifies at-risk students based on attendance patterns and provides intervention recommendations.
8. **Fee Defaulter Analysis** — Analyzes fee payment patterns, identifies defaulters, and suggests recovery actions.
9. **AI Report Cards** — Generates personalized teacher comments for student report cards based on exam performance.
10. **Parent Progress Report** — Comprehensive AI-generated progress reports for parents covering academics, attendance, and fees.
11. **AI Financial Report** — Monthly financial health analysis with income/expense breakdown and savings recommendations.
12. **AI Financial Health Check** — Overall financial health scoring with risk warnings.
13. **AI Expense Optimization** — Category-wise expense analysis with cost-saving recommendations.
14. **AI Salary Report** — Payroll health analysis with pending salary risk assessment.

### Textbook Knowledge Base (RAG with ChromaDB)

- Upload textbook content as plain text, PDF, scanned PDF, or images
- Scanned PDFs and images processed via Groq Vision OCR (Llama 4 Scout multimodal)
- Text chunked and embedded using `paraphrase-multilingual-MiniLM-L12-v2` (supports Bengali + English)
- Stored in ChromaDB persistent vector database for semantic search
- Students ask questions and get answers grounded in uploaded textbook content (RAG)
- Per-school, per-subject isolation of knowledge base data

### Slack Bot Integration

- `/school stats` — School overview (students, teachers, attendance)
- `/school notice` — Recent notices
- `/school notice create [topic]` — AI-generated notice
- `/school ask [question]` — Ask the AI assistant
- `/school report` — AI school health report

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Django REST Framework |
| Database | PostgreSQL |
| Vector DB | ChromaDB (persistent, local) |
| AI/LLM | Groq API, Llama 4 Scout 17B (text + vision) |
| Embeddings | Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) |
| Auth | JWT via SimpleJWT (with token blacklist) |
| File Storage | Cloudinary |
| PDF Generation | ReportLab |
| PDF Parsing | pdfplumber, pypdfium2 |
| SMS | SSL Wireless API |
| Frontend | React, Vite, Tailwind CSS |
| Deployment | Gunicorn, WhiteNoise |

## Project Structure

```
school-management-backend/
├── core/                    # Django project config
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Dev overrides
│   │   └── production.py    # Production overrides
│   └── urls.py              # Root URL routing
├── apps/
│   ├── authentication/      # Users, JWT, login, registration, parent portal
│   ├── tenants/             # Multi-tenant school management
│   ├── students/            # Student CRUD, bulk import, PDF, ID cards, SMS
│   ├── teachers/            # Teacher CRUD, employee IDs
│   ├── academics/           # Classes, sections, subjects, timetable
│   ├── attendance/          # Attendance marking and reports
│   ├── exams/               # Exams, marks, grading, report cards
│   ├── fees/                # Fee categories, payments, due tracking
│   ├── notices/             # Announcements with role targeting
│   ├── accounting/          # Expenses, income, salary payments, AI reports
│   ├── gallery/             # Photo albums via Cloudinary
│   ├── knowledge_base/      # Textbook RAG with ChromaDB + Groq Vision
│   ├── ai_engine/           # AI chatbot, performance, recommendations
│   └── slack_bot/           # Slack slash command integration
├── chroma_data/             # ChromaDB persistent storage (auto-created)
├── requirements.txt
├── manage.py
└── .env                     # Environment variables (not committed)
```

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ (for the frontend)

### Backend Setup

1. **Clone and install dependencies**

```bash
git clone https://github.com/rokeyaag/school-management-ai-system.git
cd school-management-ai-system
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

2. **Install additional packages** (not in requirements.txt but used by features)

```bash
pip install chromadb sentence-transformers pdfplumber pypdfium2 reportlab
```

3. **Create the `.env` file** in the project root

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*

DB_NAME=school_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

GROQ_API_KEY=your-groq-api-key

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

SLACK_BOT_TOKEN=your-slack-bot-token
```

4. **Create the database and run migrations**

```bash
createdb school_db              # or create via pgAdmin
python manage.py migrate
```

5. **Create a superuser**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | Debug mode (default: `True`) |
| `ALLOWED_HOSTS` | No | Comma-separated hosts (default: `*`) |
| `DB_NAME` | Yes | PostgreSQL database name |
| `DB_USER` | Yes | PostgreSQL username |
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `DB_HOST` | No | Database host (default: `localhost`) |
| `DB_PORT` | No | Database port (default: `5432`) |
| `CLOUDINARY_CLOUD_NAME` | Yes | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Yes | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Yes | Cloudinary API secret |
| `GROQ_API_KEY` | Yes | Groq API key for AI features |
| `CORS_ALLOWED_ORIGINS` | No | Comma-separated frontend origins |
| `SLACK_BOT_TOKEN` | No | Slack bot OAuth token |
| `SMS_API_TOKEN` | No | SSL Wireless SMS API token |
| `SMS_SID` | No | SSL Wireless sender ID |

## API Endpoints

| Prefix | Module | Key Endpoints |
|--------|--------|---------------|
| `/api/auth/` | Authentication | Register, login, logout, profile, password reset |
| `/api/tenants/` | Schools | Register school, list, approve |
| `/api/students/` | Students | CRUD, bulk upload, PDF export, ID cards, report cards |
| `/api/teachers/` | Teachers | CRUD, generate employee ID |
| `/api/academics/` | Academics | Classes, sections, subjects, timetable |
| `/api/attendance/` | Attendance | List, bulk mark, reports |
| `/api/exams/` | Exams | CRUD, results, publish, AI report cards |
| `/api/fees/` | Fees | Categories, payments, due list, reports |
| `/api/notices/` | Notices | CRUD, AI generate, unread count |
| `/api/accounting/` | Accounting | Expenses, income, salaries, AI financial reports |
| `/api/gallery/` | Gallery | Albums, photo upload/delete |
| `/api/knowledge-base/` | Knowledge Base | Subjects, documents, PDF/image upload, RAG Q&A |
| `/api/ai/` | AI Engine | Chatbot, performance, recommendations, predictions |
| `/api/slack/` | Slack Bot | Slash command handler |

## License

This project was built for the ICTBD Hackathon 2025.
