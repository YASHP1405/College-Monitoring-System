"""
Authentication views: Login, Logout, Forgot Password, Student Signup, Google Auth.
"""

import json
import re
import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

from core.utils.firebase import db
from core.utils.helpers import hash_password, validate_password

logger = logging.getLogger(__name__)


def login_view(request):
    """Handle login for Admin, Teacher, Lab, and Student roles via ID or Email."""
    if request.session.get("role"):
        return _redirect_by_role(request.session["role"])

    if request.method == "POST":
        login_input = request.POST.get("user_id", "").strip()
        password = request.POST.get("password", "")

        if not login_input or not password:
            messages.error(request, "❌ User ID / Email and Password are required!")
            return redirect(reverse("login"))

        try:
            hashed = hash_password(password)

            # 1. Check if login_input is an email address
            resolved_id = login_input
            resolved_role = None

            if "@" in login_input:
                email_lower = login_input.lower()

                # Check students by email
                students = db.child("students").get().val() or {}
                for sid, sdata in students.items():
                    if isinstance(sdata, dict) and sdata.get("email", "").lower() == email_lower:
                        resolved_id = sid
                        resolved_role = "student"
                        break

                # Check teachers by email if not found
                if not resolved_role:
                    teachers = db.child("teachers").get().val() or {}
                    for tid, tdata in teachers.items():
                        if isinstance(tdata, dict) and tdata.get("email", "").lower() == email_lower:
                            resolved_id = tid
                            resolved_role = "teacher"
                            break

            # 2. Check Admin
            admin = db.child("admins").child(resolved_id).get().val()
            if admin and admin.get("password") == hashed:
                request.session["role"] = "admin"
                request.session["user_id"] = resolved_id
                request.session["user_name"] = admin.get("name", "Admin")
                return redirect(reverse("admin_dashboard"))

            # 3. Check Teacher
            teacher = db.child("teachers").child(resolved_id).get().val()
            if teacher and teacher.get("password") == hashed:
                request.session["role"] = "teacher"
                request.session["user_id"] = resolved_id
                request.session["user_name"] = teacher.get("name", "Teacher")
                return redirect(reverse("teacher_dashboard"))

            # 4. Check Lab
            lab = db.child("labs").child(resolved_id).get().val()
            if lab and lab.get("password") == hashed:
                request.session["role"] = "lab"
                request.session["user_id"] = resolved_id
                request.session["user_name"] = lab.get("name", "Lab")
                return redirect(reverse("lab_dashboard"))

            # 5. Check Student
            student = db.child("students").child(resolved_id).get().val()
            if student and student.get("password") == hashed:
                request.session["role"] = "student"
                request.session["user_id"] = resolved_id
                request.session["user_name"] = student.get("name", "Student")
                return redirect(reverse("student_dashboard"))

            messages.error(request, "❌ Invalid credentials! Check your ID/Email and password.")

        except Exception as e:
            logger.exception("Login error: %s", e)
            messages.error(request, "❌ Error authenticating. Please try again.")

    return render(request, "login.html")


def signup_view(request):
    """Handle Student self-registration."""
    if request.session.get("role"):
        return _redirect_by_role(request.session["role"])

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        user_id = request.POST.get("user_id", "").strip().lower()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not name or not user_id or not password:
            messages.error(request, "❌ Full Name, Student ID, and Password are required!")
            return render(request, "signup.html")

        if not re.match(r'^[a-zA-Z0-9_.-]+$', user_id):
            messages.error(request, "❌ Student ID can only contain letters, numbers, dots, and underscores.")
            return render(request, "signup.html")

        if password != confirm_password:
            messages.error(request, "❌ Passwords do not match!")
            return render(request, "signup.html")

        if not validate_password(password):
            messages.error(request, "❌ Password must contain letters, numbers, and symbols.")
            return render(request, "signup.html")

        try:
            # Check if student ID exists
            existing_student = db.child("students").child(user_id).get().val()
            if existing_student:
                messages.error(request, f"❌ Student ID '{user_id}' is already registered!")
                return render(request, "signup.html")

            # Check if email is registered
            if email:
                all_students = db.child("students").get().val() or {}
                for sid, sdata in all_students.items():
                    if isinstance(sdata, dict) and sdata.get("email", "").lower() == email:
                        messages.error(request, f"❌ Email '{email}' is already registered!")
                        return render(request, "signup.html")

            # Register student in Firebase
            db.child("students").child(user_id).set({
                "name": name,
                "email": email,
                "password": hash_password(password),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Auto login
            request.session["role"] = "student"
            request.session["user_id"] = user_id
            request.session["user_name"] = name
            messages.success(request, f"🎉 Account created! Welcome, {name}!")
            return redirect(reverse("student_dashboard"))

        except Exception as e:
            logger.exception("Signup error: %s", e)
            messages.error(request, "❌ Registration failed. Please try again.")

    return render(request, "signup.html")


def google_login_view(request):
    """Handle Firebase Google Sign-In callback and establish Django student session."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        display_name = data.get("displayName", "").strip() or "Google User"
        uid = data.get("uid", "").strip()

        if not email or not uid:
            return JsonResponse({"success": False, "error": "Missing Google user info"}, status=400)

        # Derive username candidate
        clean_prefix = re.sub(r'[^a-zA-Z0-9_]', '_', email.split('@')[0])
        student_id = clean_prefix or f"user_{uid[:8]}"

        students = db.child("students").get().val() or {}
        existing_key = None
        for sid, sdata in students.items():
            if isinstance(sdata, dict) and sdata.get("email", "").lower() == email:
                existing_key = sid
                break

        if not existing_key:
            # Register new student from Google profile
            target_id = student_id
            if target_id in students:
                target_id = f"{target_id}_{uid[:4]}"

            db.child("students").child(target_id).set({
                "name": display_name,
                "email": email,
                "google_uid": uid,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            logged_in_id = target_id
        else:
            logged_in_id = existing_key

        request.session["role"] = "student"
        request.session["user_id"] = logged_in_id
        request.session["user_name"] = display_name
        messages.success(request, f"✅ Signed in with Google as {display_name}!")
        return JsonResponse({"success": True, "redirect_url": reverse("student_dashboard")})

    except Exception as e:
        logger.exception("Google auth error: %s", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


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
