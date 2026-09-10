"""
Admin views: Dashboard, Teacher Management, Lab Management, Teacher Status.
"""

import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

from core.utils.firebase import db
from core.utils.helpers import hash_password, validate_password, calculate_status
from core.utils.reports import count_reports_and_issues, sanitize_and_group_reports

logger = logging.getLogger(__name__)


def _require_admin(request):
    """Return redirect if not admin, else None."""
    if request.session.get("role") != "admin":
        return redirect(reverse("login"))
    return None


# ─── Dashboard ────────────────────────────────────────────────────────────────

def dashboard(request):
    guard = _require_admin(request)
    if guard:
        return guard

    teachers = db.child("teachers").get().val() or {}
    labs = db.child("labs").get().val() or {}
    students = db.child("students").get().val() or {}

    return render(request, "admin/dashboard.html", {
        "teachers": teachers,
        "labs": labs,
        "students": students,
    })


# ─── Teacher Management ───────────────────────────────────────────────────────

def teacher_manage(request):
    guard = _require_admin(request)
    if guard:
        return guard

    teachers = db.child("teachers").get().val() or {}
    return render(request, "admin/teacher_manage.html", {"teachers": teachers})


def add_teacher(request):
    guard = _require_admin(request)
    if guard:
        return guard

    if request.method != "POST":
        return redirect(reverse("admin_teacher_manage"))

    code = request.POST.get("short_code", "").upper().strip()
    name = request.POST.get("name", "").strip()
    password = request.POST.get("password", "").strip()

    if not code or not name or not password:
        messages.error(request, "❌ All fields are required!")
        return redirect(reverse("admin_teacher_manage"))

    if not validate_password(password):
        messages.error(request, "❌ Weak password! Must include letters, numbers, and symbols.")
        return redirect(reverse("admin_teacher_manage"))

    db.child("teachers").child(code).set({
        "name": name,
        "password": hash_password(password),
        "status": "No status yet",
        "last_updated": "Never",
        "schedule": {}
    })
    messages.success(request, f"✅ Teacher {name} added!")
    return redirect(reverse("admin_teacher_manage"))


def remove_teacher(request, code):
    guard = _require_admin(request)
    if guard:
        return guard

    db.child("teachers").child(code).remove()
    messages.warning(request, f"❌ Teacher {code} removed!")
    return redirect(reverse("admin_teacher_manage"))


# ─── Lab Management ───────────────────────────────────────────────────────────

def lab_manage(request):
    guard = _require_admin(request)
    if guard:
        return guard

    labs_dict = db.child("labs").get().val() or {}
    labs = []

    for lab_id, lab_data in labs_dict.items():
        reports_obj = lab_data.get("reports", {}) or {}
        total_reports, total_issues, _flat = count_reports_and_issues(reports_obj)
        systems = lab_data.get("systems", 0)
        systems = systems if isinstance(systems, int) else 0
        issues = lab_data.get("issues", 0)
        issues = issues if isinstance(issues, int) else total_issues

        labs.append({
            "id": lab_id,
            "name": lab_data.get("name", ""),
            "password": lab_data.get("password", ""),
            "reports": total_reports,
            "systems": systems,
            "issues": issues,
        })

    return render(request, "admin/lab_manage.html", {"labs": labs})


def add_lab(request):
    guard = _require_admin(request)
    if guard:
        return guard

    if request.method != "POST":
        return redirect(reverse("admin_lab_manage"))

    lab_id = request.POST.get("lab_id", "").strip()
    name = request.POST.get("name", "").strip()
    password = request.POST.get("password", "").strip()

    if not lab_id or not name or not password:
        messages.error(request, "❌ All fields are required!")
        return redirect(reverse("admin_lab_manage"))

    if not validate_password(password):
        messages.error(request, "❌ Weak password! Must include letters, numbers, and symbols.")
        return redirect(reverse("admin_lab_manage"))

    db.child("labs").child(lab_id).set({
        "name": name,
        "password": hash_password(password),
        "reports": {},
        "systems": 0,
        "issues": 0,
    })
    messages.success(request, f"✅ Lab {name} added!")
    return redirect(reverse("admin_lab_manage"))


def remove_lab(request, lab_id):
    guard = _require_admin(request)
    if guard:
        return guard

    db.child("labs").child(lab_id).remove()
    messages.warning(request, f"❌ Lab {lab_id} removed!")
    return redirect(reverse("admin_lab_manage"))


def get_lab_json(request, lab_id):
    """Return lab details as JSON (used by admin modal)."""
    if request.session.get("role") != "admin":
        return JsonResponse({"error": "not authorized"}, status=403)

    lab_data = db.child("labs").child(lab_id).get().val()
    if not lab_data:
        return JsonResponse({"error": "Lab not found"}, status=404)

    reports_obj = lab_data.get("reports", {}) or {}
    total_reports, total_issues, flat = count_reports_and_issues(reports_obj)

    return JsonResponse({
        "lab_id": lab_id,
        "lab_name": lab_data.get("name", ""),
        "reports": flat,
        "reports_count": total_reports,
        "systems": lab_data.get("systems", 0),
        "issues": total_issues,
    })


def lab_reports(request, lab_id):
    guard = _require_admin(request)
    if guard:
        return guard

    lab_data = db.child("labs").child(lab_id).get().val()
    if not lab_data:
        messages.error(request, "❌ Lab not found!")
        return redirect(reverse("admin_lab_manage"))

    lab = {
        "id": lab_id,
        "name": lab_data.get("name", "Unknown"),
        "systems": lab_data.get("systems", 0),
        "issues": lab_data.get("issues", 0),
    }

    reports_obj = lab_data.get("reports", {})
    grouped_reports = sanitize_and_group_reports(reports_obj)

    return render(request, "admin/lab_reports.html", {
        "lab": lab,
        "reports": grouped_reports,
    })


# ─── Teacher Status ───────────────────────────────────────────────────────────

def teacher_status(request):
    guard = _require_admin(request)
    if guard:
        return guard

    teachers = db.child("teachers").get().val() or {}
    updated_teachers = {}

    for code, teacher in teachers.items():
        calculated_status, current_day, current_time = calculate_status(teacher)
        updated_teachers[code] = {
            "name": teacher.get("name", "Unknown"),
            "status": calculated_status,
            "last_updated": teacher.get("last_updated", "Never"),
            "schedule": teacher.get("schedule", {}),
        }

    now = datetime.now()
    return render(request, "admin/teacher_status.html", {
        "teachers": updated_teachers,
        "current_day": now.strftime("%A"),
        "current_time": now.strftime("%H:%M"),
    })
