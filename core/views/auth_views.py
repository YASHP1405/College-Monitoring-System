"""
Authentication views: Login, Logout, Forgot Password.
"""

import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from core.utils.firebase import db
from core.utils.helpers import hash_password, validate_password

logger = logging.getLogger(__name__)


def login_view(request):
    """Handle login for Admin, Teacher, Lab, and Student roles."""
    if request.session.get("role"):
        return _redirect_by_role(request.session["role"])

    if request.method == "POST":
        user_id = request.POST.get("user_id", "").strip()
        password = request.POST.get("password", "")

        if not user_id or not password:
            messages.error(request, "❌ User ID and Password are required!")
            return redirect(reverse("login"))

        try:
            hashed = hash_password(password)

            # Admin check
            admin = db.child("admins").child(user_id).get().val()
            if admin and admin.get("password") == hashed:
                request.session["role"] = "admin"
                request.session["user_id"] = user_id
                return redirect(reverse("admin_dashboard"))

            # Teacher check
            teacher = db.child("teachers").child(user_id).get().val()
            if teacher and teacher.get("password") == hashed:
                request.session["role"] = "teacher"
                request.session["user_id"] = user_id
                return redirect(reverse("teacher_dashboard"))

            # Lab check
            lab = db.child("labs").child(user_id).get().val()
            if lab and lab.get("password") == hashed:
                request.session["role"] = "lab"
                request.session["user_id"] = user_id
                return redirect(reverse("lab_dashboard"))

            # Student check
            student = db.child("students").child(user_id).get().val()
            if student and student.get("password") == hashed:
                request.session["role"] = "student"
                request.session["user_id"] = user_id
                return redirect(reverse("student_dashboard"))

            messages.error(request, "❌ Invalid credentials!")

        except Exception as e:
            logger.exception("Login error: %s", e)
            messages.error(request, "❌ Error authenticating. Please try again.")

    return render(request, "login.html")


def logout_view(request):
    """Clear session and redirect to login."""
    request.session.flush()
    messages.success(request, "✅ Logged out successfully!")
    return redirect(reverse("login"))


def forgot_password_view(request):
    """Allow teachers to reset their password using their short code."""
    if request.method == "POST":
        code = request.POST.get("short_code", "").upper().strip()
        new_password = request.POST.get("new_password", "")

        teacher = db.child("teachers").child(code).get().val()
        if not teacher:
            messages.error(request, "❌ Invalid short code!")
            return redirect(reverse("forgot_password"))

        if not validate_password(new_password):
            messages.error(request, "❌ Password must contain letters, numbers, and symbols.")
            return redirect(reverse("forgot_password"))

        db.child("teachers").child(code).update({"password": hash_password(new_password)})
        messages.success(request, "✅ Password reset successfully!")
        return redirect(reverse("login"))

    return render(request, "forgot_password.html")


# ─── Internal Helper ──────────────────────────────────────────────────────────

def _redirect_by_role(role: str):
    """Redirect to the correct dashboard based on role."""
    role_map = {
        "admin": "admin_dashboard",
        "teacher": "teacher_dashboard",
        "lab": "lab_dashboard",
        "student": "student_dashboard",
    }
    return redirect(reverse(role_map.get(role, "login")))
