# 🎓 EduMonitor — College Monitoring System

A modern, full-featured College Monitoring System built with **Django 4.2 LTS** and powered by **Firebase Realtime Database**. Features real-time teacher tracking, lab equipment defect reporting, student schedule lookups, and complete institutional oversight through a sleek dark glassmorphism dashboard.

Designed for seamless deployment to **GitHub** and **PythonAnywhere**.

---

## ✨ Features

### 👨‍💼 1. Admin Portal
- **Overview Dashboard**: High-level statistics on teachers, labs, students, active issues, and equipment counts.
- **Teacher Management**: Register new faculty, generate short codes, assign credentials, and view or remove staff.
- **Real-Time Teacher Status**: Live monitoring showing whether teachers are Available, Busy in Lecture (with room & subject), or On Leave.
- **Lab Management**: Register computer labs, track system counts, view defect logs, and inspect detailed lab statistics via modal dialogs.
- **Lab Reports History**: Detailed chronological defect logs categorized by month and date.

### 👨‍🏫 2. Teacher Portal
- **Status Dashboard**: Quickly update current availability (`AVAILABLE`, `NOT AVAILABLE`, `ON LEAVE`) with room and return date specifications.
- **Live Lecture Detection**: Automatically detects ongoing lectures based on the current day and time slot.
- **Schedule Management**: Full weekly timetable builder — add or remove lecture slots per day with room and subject details.

### 🖥️ 3. Lab Technician Portal
- **Equipment Defect Reporting**: Submit structured fault reports covering monitors, CPUs, mice, keyboards, switches, and custom issues.
- **Historical Report Archive**: Browse past submissions organized by month and date.
- **Live Report Deletion**: Remove resolved defect tickets asynchronously with instant UI feedback.

### 🎓 4. Student Portal
- **Faculty Directory**: Searchable list of teachers with real-time availability badges.
- **Live Lecture Tracker**: View who is currently teaching, in which classroom, and which subject.
- **Daily Timetable**: Check today's schedule for any faculty member.

---

## 🎨 UI / Design System
- **Theme**: Premium Dark Glassmorphism (`backdrop-filter: blur(16px)`).
- **Typography**: Google Fonts (*Outfit* headings & *Inter* body).
- **Color Palette**: Violet / Indigo (`#6c63ff`), Cyan (`#00d4ff`), Emerald (`#00e5a0`), Coral (`#ff6b6b`).
- **Responsiveness**: Fully responsive desktop sidebar and mobile slide-out navigation.
- **Micro-Interactions**: Smooth card hover lifts, floating badges, auto-dismissing toast notifications.

---

## 🏗️ Architecture & Technology Stack

| Component | Technology |
|---|---|
| **Framework** | Django 4.2 LTS |
| **Database** | Firebase Realtime Database (`pyrebase4`) |
| **Frontend** | Semantic HTML5 + Custom Vanilla CSS (Design System) |
| **Sessions** | Django Database-backed Sessions (`SQLite3`) |
| **Authentication** | Role-based authentication (Admin, Teacher, Lab, Student) with SHA-256 password hashing |
| **Deployment Target** | GitHub & PythonAnywhere |

---

## 📂 Project Structure

```text
Monitoring System/
├── .env                       # Local environment variables (do NOT commit)
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore rules for Django & Python
├── manage.py                  # Django CLI entrypoint
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── monitoring_system/         # Project configuration
│   ├── __init__.py
│   ├── asgi.py                # ASGI entrypoint
│   ├── settings.py            # Django settings (Firebase config, sessions, static)
│   ├── urls.py                # Root URL router
│   └── wsgi.py                # WSGI entrypoint (for PythonAnywhere)
└── core/                      # Main application
    ├── apps.py                # App configuration & default admin bootstrap
    ├── urls.py                # Route definitions
    ├── static/
    │   └── css/
    │       └── style.css      # Glassmorphism design system (~480 lines)
    ├── templates/
    │   ├── base.html          # Base layout with toast alerts & sidebar logic
    │   ├── login.html         # Unified multi-role login
    │   ├── forgot_password.html # Teacher password reset
    │   ├── admin/
    │   │   ├── dashboard.html
    │   │   ├── teacher_manage.html
    │   │   ├── teacher_status.html
    │   │   ├── lab_manage.html
    │   │   └── lab_reports.html
    │   ├── teacher/
    │   │   ├── dashboard.html
    │   │   └── schedule.html
    │   ├── lab/
    │   │   └── dashboard.html
    │   └── student/
    │       └── dashboard.html
    ├── utils/
    │   ├── __init__.py
    │   ├── firebase.py        # Pyrebase initialization & db client
    │   ├── helpers.py         # Passwords, time-slot calculations, bootstrapping
    │   └── reports.py         # Report flattening, counting, & sanitization
    └── views/
        ├── __init__.py
        ├── auth_views.py      # Login, logout, forgot password
        ├── admin_views.py     # Admin dashboard, faculty & lab management
        ├── teacher_views.py   # Teacher status & schedule management
        ├── lab_views.py       # Lab report submission & management
        └── student_views.py   # Student directory & real-time tracker
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed
- Git installed
- A Firebase project with Realtime Database enabled

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd "Monitoring System"
```

### 3. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your Firebase credentials:
```env
DJANGO_SECRET_KEY=your-secure-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
```

> **Firebase Setup Note**: In your Firebase Console, ensure your Realtime Database rules allow read/write access for your application.

### 6. Initialize Database (for Django Sessions)
```bash
python manage.py migrate
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.

---

## 🔑 Default Credentials

On initial startup, a default super admin is automatically verified / seeded into Firebase:

| Role | User ID | Password |
|---|---|---|
| **Admin** | `admin1` | `admin123` |

> ⚠️ **Security Tip**: Log into the admin portal and update this password or add a dedicated administrator for production use.

---

## 🌐 Deploying to PythonAnywhere

1. **Upload / Clone Code**:
   Open a Bash console in PythonAnywhere:
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd "Monitoring System"
   ```

2. **Create Virtualenv & Install Requirements**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create your `.env` file in the project directory with your production credentials.

4. **Collect Static Files & Run Migrations**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

5. **Configure PythonAnywhere Web Tab**:
   - **Source code**: `/home/<username>/Monitoring System`
   - **Working directory**: `/home/<username>/Monitoring System`
   - **Virtualenv**: `/home/<username>/.virtualenvs/myenv`
   - **Static Files**:
     - URL: `/static/`
     - Directory: `/home/<username>/Monitoring System/staticfiles`
   - **WSGI configuration file** (edit from Web tab):
     ```python
     import os
     import sys
     from dotenv import load_dotenv

     path = '/home/<username>/Monitoring System'
     if path not in sys.path:
         sys.path.append(path)

     # Load environment variables
     load_dotenv(os.path.join(path, '.env'))

     os.environ['DJANGO_SETTINGS_MODULE'] = 'monitoring_system.settings'

     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```

6. Click **Reload <username>.pythonanywhere.com** to go live!

---

## 🔒 Security Best Practices
- Keep `.env` out of version control (`.gitignore` already blocks `.env` and `*.env.local`).
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` to your actual domain in production.
- Use strong passwords matching the complexity policy (letters, numbers, and symbols required).

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
