# 🎓 EduMonitor — College Monitoring & Management System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Realtime%20Database-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)](#)

<p align="center">
  <b>A unified, real-time academic administration and monitoring platform.</b><br>
  Track faculty lecture schedules, monitor computer lab hardware health, manage student directories, and streamline institutional communication through a responsive dark-mode glassmorphism interface.
</p>

[Quick Start](#-quick-start-guide) •
[Key Features](#-key-features) •
[Default Credentials](#-default-credentials) •
[System Architecture](#-system-architecture) •
[Deployment](#-deployment-to-pythonanywhere)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features by Role](#-key-features-by-role)
  - [1. Administrator Portal](#1--administrator-portal)
  - [2. Faculty / Teacher Portal](#2--faculty--teacher-portal)
  - [3. Lab Technician Portal](#3--lab-technician-portal)
  - [4. Student Portal](#4--student-portal)
  - [5. Authentication & Security](#5--authentication--security)
- [Zero-Config Fallback Mode](#-zero-config-fallback-mode)
- [System Architecture & Tech Stack](#-system-architecture--tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Quick Start Guide (Local Setup)](#-quick-start-guide)
- [Default Demo Credentials](#-default-credentials)
- [Firebase Integration Guide (Optional)](#-firebase-integration-guide)
- [Deployment to PythonAnywhere](#-deployment-to-pythonanywhere)
- [Security & Pre-Push Checklist](#-security--github-pre-push-checklist)
- [License](#-license)

---

## 📖 Overview

In modern academic campuses, coordination between administrators, faculty, lab technicians, and students often relies on scattered spreadsheets, paper logs, or fragmented apps.

**EduMonitor** consolidates all campus operations into one centralized web application:
- **Administrators** maintain institution-wide oversight of staff, lab workstations, and active issues.
- **Teachers** update real-time availability and manage automated weekly timetables.
- **Lab Technicians** log and track hardware defects (CPUs, monitors, peripherals, networking switches).
- **Students** check real-time faculty availability and lecture rooms without roaming campus corridors.

---

## 🌟 Key Features by Role

### 1. 🛡️ Administrator Portal
- **Executive Analytics**: Live metric cards displaying total registered faculty, operational labs, recorded hardware issues, and active students.
- **Faculty Directory Management**: Register new faculty, generate random secure passwords, assign short codes (e.g. `T01`), or remove records.
- **Live Faculty Radar**: Real-time status tracker indicating whether each teacher is **Available**, **In Lecture** (with room & subject), or **On Leave**.
- **Lab Workstation Control**: Register labs, configure system counts, inspect defect breakdowns via interactive modals, or decommission obsolete labs.
- **Chronological Defect History**: Inspect archived hardware fault reports grouped by month and date.

### 2. 👨‍🏫 Faculty / Teacher Portal
- **Instant Availability Toggle**: Set status to `AVAILABLE`, `NOT AVAILABLE`, or `ON LEAVE` (with return date and optional room notes).
- **Intelligent Lecture Detection**: Automatically calculates and highlights ongoing lectures based on the current day of the week and system clock.
- **Interactive Timetable Builder**: Configure weekly lecture schedules with precise time slots (e.g., `09:00-10:00`), assigned rooms, and course subjects.

### 3. 🖥️ Lab Technician Portal
- **Hardware Fault Ticketing**: Log structured reports for malfunctioning monitors, CPUs, mice, keyboards, switches, and custom defect descriptions.
- **Historical Log Archive**: Browse past repair requests organized chronologically.
- **Real-Time Ticket Closure**: Resolve and remove defects with instant asynchronous UI updates.

### 4. 🎓 Student Portal
- **Searchable Faculty Directory**: Search teachers by name or department code with real-time status badges.
- **Live Classroom Tracker**: Immediately verify whether a professor is currently lecturing, including room number and subject.
- **Daily Schedule Viewer**: Inspect any teacher's full schedule for the current day.

### 5. 🔐 Authentication & Security
- **Unified Multi-Role Login**: Clean single login screen supporting Admin, Teacher, Lab Technician, and Student access by **User ID** or **Email Address**.
- **Student & Teacher Registration**: Dedicated signup flow with strict password complexity validation (letters, numbers, and symbols).
- **Google OAuth Integration**: One-click Google sign-in via Firebase Client SDK.
- **Session Persistence**: Optional "Remember Me" functionality.
- **Password Reset**: Self-service reset option for faculty accounts.
- **Secure Password Storage**: Cryptographically hashed using SHA-256 before storage.

---

## ⚡ Zero-Config Fallback Mode

> [!TIP]
> **No Firebase account? No problem!**  
> EduMonitor includes an automatic local JSON database fallback (`firebase_local.json`).  
> Anyone cloning this repository can run migrations and launch the app immediately for testing and evaluation **without creating a Firebase project or entering any API keys**.  
> When you're ready for production or cloud sync, simply add your Firebase credentials to `.env`.

---

## 🏗️ System Architecture & Tech Stack

```text
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
│  (Modern Dark-Theme Glassmorphism UI, Vanilla CSS, JS)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON API
┌──────────────────────────────▼──────────────────────────────┐
│                    Django 4.2 LTS Core                      │
│   • URL Routing & Context Processors                        │
│   • Multi-Role Auth & Session Management (SQLite3)          │
│   • Helper Utilities, Time-Slot Resolvers, Cryptography     │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
  ┌─────────────────────────┐     ┌─────────────────────────┐
  │ Firebase Realtime DB    │     │ Local JSON Database     │
  │ (Cloud Sync via Pyrebase)│     │ (Zero-Config Fallback)  │
  └─────────────────────────┘     └─────────────────────────┘
```

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Django 4.2 LTS (Python) | Robust URL routing, sessions, views, and templating |
| **Primary Database** | Firebase Realtime Database | Real-time multi-client state synchronization |
| **Fallback Database** | Local JSON Store (`firebase_local.json`) | Seamless offline development and preview |
| **Session Backend** | Django Sessions (`SQLite3`) | Isolated, secure server-side session management |
| **Frontend Styling** | Semantic HTML5 & Vanilla CSS | Custom glassmorphism design system (`style.css`) |
| **Icons & Typography** | Google Fonts (*Outfit* & *Inter*) + Font Awesome | Polished typography and modern iconography |
| **Deployment Target** | PythonAnywhere / Gunicorn / Render | Production-ready WSGI configuration |

---

## 📂 Project Directory Structure

```text
College-Monitoring-System/
├── .env.example               # Environment variables template (safe to commit)
├── .gitignore                 # Excludes secrets, virtual environments, DBs, and caches
├── LICENSE                    # MIT open-source license
├── README.md                  # Comprehensive project documentation
├── manage.py                  # Django administrative CLI
├── requirements.txt           # Python package dependencies
│
├── monitoring_system/         # Project Settings & WSGI Configuration
│   ├── __init__.py
│   ├── asgi.py                # ASGI entrypoint
│   ├── settings.py            # Core Django configuration & context processors
│   ├── urls.py                # Root URL routing table
│   └── wsgi.py                # WSGI entrypoint for production servers
│
└── core/                      # Application Logic & Templates
    ├── apps.py                # App configuration & default admin bootstrapping
    ├── urls.py                # Role-specific route definitions
    ├── context_processors.py  # Supplies client-side Firebase config to templates
    │
    ├── static/
    │   └── css/
    │       └── style.css      # Dark glassmorphism design system
    │
    ├── templates/             # UI Templates
    │   ├── base.html          # Shell layout with toast alerts & navigation
    │   ├── login.html         # Unified multi-role login & Google Sign-In
    │   ├── registration.html  # Responsive student/faculty signup
    │   ├── forgot_password.html # Teacher password reset flow
    │   ├── admin/             # Administrator dashboard & management views
    │   ├── teacher/           # Faculty dashboard & timetable editor
    │   ├── lab/               # Lab technician dashboard & defect logger
    │   └── student/           # Student directory & real-time tracker
    │
    ├── utils/
    │   ├── firebase.py        # Database connector with local fallback emulator
    │   ├── helpers.py         # Password hashing & schedule time calculation
    │   └── reports.py         # Report flattening & statistics sanitization
    │
    └── views/
        ├── auth_views.py      # Login, registration, Google callback, logout
        ├── admin_views.py     # Admin operations (faculty & lab CRUD)
        ├── teacher_views.py   # Availability updates & timetable edits
        ├── lab_views.py       # Defect report submission & resolution
        └── student_views.py   # Student search & timetable lookup
```

---

## 🚀 Quick Start Guide

Follow these steps to run the project locally in under 3 minutes.

### 1. Prerequisites
- **Python 3.10+** installed on your system ([python.org](https://www.python.org/downloads/))
- **Git** installed ([git-scm.com](https://git-scm.com/))

### 2. Clone the Repository
```bash
git clone https://github.com/YASHP1405/College-Monitoring-System.git
cd College-Monitoring-System
```

### 3. Create & Activate a Virtual Environment

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

### 5. Setup Environment File
Copy the example environment file:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

*(Optional)* You can run the app immediately with default local fallback settings, or edit `.env` to connect your live Firebase project.

### 6. Run Migrations (for Django Session Support)
```bash
python manage.py migrate
```

### 7. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
```text
http://127.0.0.1:8000/
```

---

## 🔑 Default Credentials

For local testing and evaluation, the database includes pre-configured demo accounts:

| Role | User ID / Login | Default Password | Notes |
|---|---|---|---|
| 🛡️ **Administrator** | `admin1` | `admin123` | Full system access to all management modules |
| 👨‍🏫 **Teacher / Faculty** | `T01` | `teach123!` | Dr. Alan Turing (preloaded timetable) |
| 👨‍🏫 **Teacher / Faculty** | `T02` | `teach123!` | Prof. Ada Lovelace |
| 🖥️ **Lab Technician** | `lab1` | `lab123!` | Main Computer Science Lab |
| 🖥️ **Lab Technician** | `lab2` | `lab123!` | Hardware & Networking Lab |
| 🎓 **Student** | `student1` | `student123!` | Or register a new account on `/signup/` |

> [!IMPORTANT]
> Change the default administrator password in production environments!

---

## 🔥 Firebase Integration Guide

To connect a live Firebase Realtime Database:

1. Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. In the left sidebar, navigate to **Build > Realtime Database** and click **Create Database**.
3. Under the **Rules** tab, set access rules:
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```
   *(Adjust security rules as needed for production).*
4. Navigate to **Project Settings** (gear icon) > **General** > **Your apps** and add a **Web App** to find your API credentials.
5. In Firebase **Authentication**, enable the **Google** sign-in provider if you wish to use Google login.
6. Open your `.env` file and fill in your keys:
   ```env
   FIREBASE_API_KEY=AIzaSy...
   FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
   FIREBASE_DATABASE_URL=https://your-app-default-rtdb.firebaseio.com
   FIREBASE_STORAGE_BUCKET=your-app.appspot.com
   FIREBASE_PROJECT_ID=your-app
   ```
7. Restart the Django server. EduMonitor will automatically connect to your live Firebase instance!

---

## 🌐 Deployment to PythonAnywhere

EduMonitor is pre-configured for direct hosting on [PythonAnywhere](https://www.pythonanywhere.com/):

1. **Clone the Repo in PythonAnywhere Bash Console**:
   ```bash
   git clone https://github.com/YASHP1405/College-Monitoring-System.git
   cd College-Monitoring-System
   ```

2. **Create Virtual Environment & Install Packages**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 edumonitor-env
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the project folder with your production values (`DEBUG=False`, `ALLOWED_HOSTS=<your-username>.pythonanywhere.com`).

4. **Collect Static Files & Run Migrations**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

5. **Configure PythonAnywhere Web Tab**:
   - **Source code**: `/home/<username>/College-Monitoring-System`
   - **Working directory**: `/home/<username>/College-Monitoring-System`
   - **Virtualenv**: `/home/<username>/.virtualenvs/edumonitor-env`
   - **Static files**:
     - URL: `/static/`
     - Path: `/home/<username>/College-Monitoring-System/staticfiles`

6. **WSGI Configuration File**:
   Click into the WSGI configuration file link and replace the contents with:
   ```python
   import os
   import sys
   from pathlib import Path
   from dotenv import load_dotenv

   path = '/home/<username>/College-Monitoring-System'
   if path not in sys.path:
       sys.path.append(path)

   load_dotenv(os.path.join(path, '.env'))
   os.environ['DJANGO_SETTINGS_MODULE'] = 'monitoring_system.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

7. Click **Reload <your-username>.pythonanywhere.com** to launch!

---

## 🔒 Security & GitHub Pre-Push Checklist

Before pushing commits to GitHub, verify that sensitive files remain private:

- [x] **`.env` is ignored**: Verified in `.gitignore`. Never commit API keys or production database secrets.
- [x] **`db.sqlite3` is ignored**: Local session database remains untracked.
- [x] **`firebase_local.json` is ignored**: Local test state stays on your development machine.
- [x] **`venv/` is ignored**: Virtual environment dependencies are not pushed.
- [x] **`__pycache__/` is ignored**: Compiled bytecode files are excluded.
- [x] **`.env.example` is maintained**: Safe placeholder template provided for collaborators.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details.

---

<div align="center">
  <sub>Built with ❤️ for academic institutions, educators, and students.</sub>
</div>
