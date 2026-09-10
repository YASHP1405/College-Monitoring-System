"""
Lab views: Dashboard (submit / view reports) and Remove Report (JSON API).
"""

import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

from core.utils.firebase import db
from core.utils.reports import sanitize_and_group_reports

logger = logging.getLogger(__name__)


def _require_lab(request):
    if request.session.get("role") != "lab":
        return redirect(reverse("login"))
    return None


def dashboard(request):
    guard = _require_lab(request)
    if guard:
        return guard

    lab_id = request.session["user_id"]
    lab_data = db.child("labs").child(lab_id).get().val() or {}

    if request.method == "POST":
        report = {}
        for key in ["Monitors", "CPU", "Mouse", "Keyboard", "Switches"]:
            try:
                report[key] = int(request.POST.get(key, 0))
            except (ValueError, TypeError):
                report[key] = 0

        other_issues = request.POST.get("OtherIssues", "").strip()
        if other_issues:
            report["OtherIssues"] = other_issues

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.child("labs").child(lab_id).child("reports").child(timestamp).set(report)
        messages.success(request, "✅ Report saved!")

        # Reload lab data to include new report
        lab_data = db.child("labs").child(lab_id).get().val() or {}

    reports_obj = lab_data.get("reports", {})
    if not isinstance(reports_obj, dict):
        reports_obj = {}

    grouped_reports = sanitize_and_group_reports(reports_obj)

    lab = {
        "id": lab_id,
        "name": lab_data.get("name", "Unknown"),
        "systems": lab_data.get("systems", 0),
        "issues": lab_data.get("issues", 0),
    }

    return render(request, "lab/dashboard.html", {
        "lab_id": lab_id,
        "lab": lab,
        "reports": grouped_reports,
    })


def remove_report(request):
    """JSON endpoint to delete a specific lab report by timestamp."""
    if request.session.get("role") != "lab":
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    lab_id = request.session["user_id"]
    timestamp = request.POST.get("timestamp")

    if not timestamp:
        return JsonResponse({"success": False, "error": "No timestamp provided"}, status=400)

    try:
        db.child("labs").child(lab_id).child("reports").child(timestamp).remove()
        return JsonResponse({"success": True})
    except Exception as e:
        logger.exception("Error removing lab report: %s", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
