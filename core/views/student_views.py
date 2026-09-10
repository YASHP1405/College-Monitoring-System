"""
Student views: Dashboard showing all teachers with their real-time status.
"""

import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse

from core.utils.firebase import db

logger = logging.getLogger(__name__)


def dashboard(request):
    if request.session.get("role") != "student":
        return redirect(reverse("login"))

    teachers = db.child("teachers").get().val() or {}
    current_day = datetime.now().strftime("%A")
    current_time_24 = datetime.now().strftime("%H:%M")

    for code, teacher in teachers.items():
        teacher_schedule = teacher.get("schedule", {})
        today_schedule = teacher_schedule.get(current_day, {})

        # Normalise list → dict if Firebase returned a list
        if isinstance(today_schedule, list):
            today_schedule = {str(i): v for i, v in enumerate(today_schedule)}

        teacher["current_lecture"] = None
        if today_schedule:
            for time_slot, lecture in today_schedule.items():
                if isinstance(lecture, dict) and "-" in time_slot:
                    parts = time_slot.split("-")
                    start = parts[0].strip()
                    end = parts[1].strip()
                    if start <= current_time_24 <= end:
                        teacher["current_lecture"] = {
                            "room": lecture.get("room", "Unknown"),
                            "subject": lecture.get("subject", ""),
                        }
                        break

    return render(request, "student/dashboard.html", {
        "teachers": teachers,
        "current_day": current_day,
        "current_time": datetime.now().strftime("%I:%M %p"),
    })
