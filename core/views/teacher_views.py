"""
Teacher views: Dashboard (status update) and Schedule management.
"""

import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from core.utils.firebase import db
from core.utils.helpers import get_current_lecture

logger = logging.getLogger(__name__)


def _require_teacher(request):
    if request.session.get("role") != "teacher":
        return redirect(reverse("login"))
    return None


def dashboard(request):
    guard = _require_teacher(request)
    if guard:
        return guard

    code = request.session["user_id"]
    teacher = db.child("teachers").child(code).get().val() or {}
    schedule = teacher.get("schedule", {})

    if request.method == "POST":
        status_type = request.POST.get("status_type", "")
        room = request.POST.get("room", "")
        leave_date = request.POST.get("leave_date", "")

        if status_type == "AVAILABLE":
            status_text = f"AVAILABLE in Room {room}" if room else "AVAILABLE"
        elif status_type == "NOT AVAILABLE":
            status_text = "NOT AVAILABLE"
        elif status_type == "ON LEAVE":
            status_text = f"ON LEAVE until {leave_date}" if leave_date else "ON LEAVE"
        else:
            status_text = teacher.get("status", "No status")

        db.child("teachers").child(code).update({
            "status": status_text,
            "last_updated": datetime.now().strftime("%d/%m/%Y %I:%M %p"),
        })
        messages.success(request, "✅ Status updated!")

    # Refresh teacher data after possible update
    teacher = db.child("teachers").child(code).get().val() or {}
    schedule = teacher.get("schedule", {})
    current_lecture = get_current_lecture(schedule)

    if current_lecture:
        display_status = f"IN LECTURE at {current_lecture['room']} / {current_lecture['subject']}"
    else:
        display_status = teacher.get("status", "No status")

    # Today's schedule — normalise string entries to dicts
    today_schedule = schedule.get(datetime.now().strftime("%A"), {})
    for k, v in list(today_schedule.items()):
        if isinstance(v, str):
            parts = v.split(" / ")
            today_schedule[k] = {
                "room": parts[0],
                "subject": parts[1] if len(parts) > 1 else "",
            }

    now = datetime.now()
    return render(request, "teacher/dashboard.html", {
        "teacher": teacher,
        "display_status": display_status,
        "schedule": today_schedule,
        "current_day": now.strftime("%A"),
        "current_time": now.strftime("%I:%M %p"),
    })


def schedule_view(request):
    guard = _require_teacher(request)
    if guard:
        return guard

    code = request.session["user_id"]
    teacher = db.child("teachers").child(code).get().val() or {}
    schedule = teacher.get("schedule", {})

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            day = request.POST.get("day")
            time_slot = request.POST.get("time_slot")
            room = request.POST.get("room")
            subject = request.POST.get("subject")

            if day and time_slot and room and subject:
                db.child("teachers").child(code).child("schedule").child(day).child(time_slot).set({
                    "room": room,
                    "subject": subject,
                })
                messages.success(request, f"✅ Schedule updated: {day} {time_slot} → {room} / {subject}")
            else:
                messages.error(request, "❌ All fields are required!")

        elif action == "delete":
            day = request.POST.get("day")
            time_slot = request.POST.get("time_slot")

            if day and time_slot:
                db.child("teachers").child(code).child("schedule").child(day).child(time_slot).remove()
                messages.info(request, f"🗑 Deleted schedule: {day} {time_slot}")
            else:
                messages.error(request, "❌ Day & Time Slot required to delete!")

        return redirect(reverse("teacher_schedule"))

    # Refresh schedule after changes
    teacher = db.child("teachers").child(code).get().val() or {}
    schedule = teacher.get("schedule", {})

    return render(request, "teacher/schedule.html", {
        "teacher": teacher,
        "schedule": schedule,
    })
