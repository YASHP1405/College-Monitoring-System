from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin-panel/", admin.site.urls),   # Django admin (renamed to avoid clash with /admin view)
    path("", include("core.urls")),
]
