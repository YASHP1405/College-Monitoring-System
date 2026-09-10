from django.urls import path
from core.views import auth_views, admin_views, teacher_views, lab_views, student_views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path("", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("forgot-password/", auth_views.forgot_password_view, name="forgot_password"),

    # ── Admin ─────────────────────────────────────────────────────────────────
    path("admin/", admin_views.dashboard, name="admin_dashboard"),
    path("admin/teacher-manage/", admin_views.teacher_manage, name="admin_teacher_manage"),
    path("admin/add-teacher/", admin_views.add_teacher, name="add_teacher"),
    path("admin/remove-teacher/<str:code>/", admin_views.remove_teacher, name="remove_teacher"),
    path("admin/teacher-status/", admin_views.teacher_status, name="admin_teacher_status"),
    path("admin/lab-manage/", admin_views.lab_manage, name="admin_lab_manage"),
    path("admin/add-lab/", admin_views.add_lab, name="add_lab"),
    path("admin/remove-lab/<str:lab_id>/", admin_views.remove_lab, name="remove_lab"),
    path("admin/lab/<str:lab_id>/", admin_views.get_lab_json, name="get_lab"),
    path("admin/lab/<str:lab_id>/reports/", admin_views.lab_reports, name="lab_reports"),

    # ── Teacher ───────────────────────────────────────────────────────────────
    path("teacher/", teacher_views.dashboard, name="teacher_dashboard"),
    path("teacher/schedule/", teacher_views.schedule_view, name="teacher_schedule"),

    # ── Lab ───────────────────────────────────────────────────────────────────
    path("lab/", lab_views.dashboard, name="lab_dashboard"),
    path("lab/remove-report/", lab_views.remove_report, name="remove_lab_report"),

    # ── Student ───────────────────────────────────────────────────────────────
    path("student/", student_views.dashboard, name="student_dashboard"),
]
