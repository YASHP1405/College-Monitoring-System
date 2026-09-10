"""
Report processing utilities for lab equipment issue reports.
Ported from the original Flask app.py.
"""

from datetime import datetime


# ─── Flatten Reports ──────────────────────────────────────────────────────────

def flatten_reports(reports_obj: dict) -> dict:
    """
    Convert various possible Firebase shapes into a flat dictionary:
      { "timestamp_str": {Monitors:.., CPU:.., ...}, ... }

    Handles:
      - flat mapping timestamp -> report (common case)
      - nested mapping like month->{day->{timestamp->report}}
      - other nested combinations
    """
    flat = {}

    def _walk(key_prefix, obj):
        if isinstance(obj, dict):
            # If dict contains any equipment keys, treat as a report entry
            expected_keys = {"Monitors", "CPU", "Mouse", "Keyboard", "Switches"}
            if expected_keys & set(obj.keys()):
                timestamp_key = key_prefix or "unknown"
                flat[timestamp_key] = obj
                return
            # Otherwise descend deeper
            for k, v in obj.items():
                next_prefix = k if not key_prefix else f"{key_prefix} {k}"
                _walk(next_prefix, v)
        # Ignore non-dict leaves

    _walk("", reports_obj)
    return flat


def count_reports_and_issues(reports_obj: dict) -> tuple[int, int, dict]:
    """
    Return (total_reports, total_issues, flat_reports_dict).
    """
    flat = flatten_reports(reports_obj)
    total_reports = 0
    total_issues = 0
    for ts, rep in flat.items():
        if isinstance(rep, dict):
            total_reports += 1
            total_issues += sum(v for v in rep.values() if isinstance(v, int))
    return total_reports, total_issues, flat


# ─── Sanitize Reports ─────────────────────────────────────────────────────────

def sanitize_report(report) -> dict:
    """Ensure report dict has all required equipment keys with integer values."""
    keys = ["Monitors", "CPU", "Mouse", "Keyboard", "Switches"]
    if not isinstance(report, dict):
        return {key: 0 for key in keys}
    for key in keys:
        if key not in report or not isinstance(report[key], int):
            report[key] = 0
    return report


def sanitize_and_group_reports(reports_obj: dict) -> dict:
    """
    Convert flat or nested reports into a grouped structure:
      { "Month Year": { "DD-MM-YYYY": { "timestamp": report, ... }, ... }, ... }

    Sorted newest-first.
    """
    grouped_reports = {}
    if not isinstance(reports_obj, dict):
        return grouped_reports

    for tstamp, report in sorted(reports_obj.items(), reverse=True):
        report = sanitize_report(report)
        try:
            dt = datetime.strptime(tstamp, "%Y-%m-%d %H:%M:%S")
            month = dt.strftime("%B %Y")
            day = dt.strftime("%d-%m-%Y")
        except Exception:
            month = "Unknown"
            day = "Unknown"

        grouped_reports.setdefault(month, {}).setdefault(day, {})[tstamp] = report

    return grouped_reports
