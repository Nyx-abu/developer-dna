"""
Root URL configuration for Developer DNA.

All telemetry API routes live under /api/v1/.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request) -> JsonResponse:
    """Minimal health endpoint for Docker health checks."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health_check, name="health-check"),
    path("api/v1/", include("telemetry.urls")),
]
