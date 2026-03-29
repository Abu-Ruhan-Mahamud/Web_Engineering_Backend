from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# Health check endpoint for Azure App Service
def health_check(request):
    return JsonResponse({"status": "ok", "service": "Curova API"})

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/admin/", include("users.admin_urls")),
    path("api/", include("appointments.urls")),
    path("api/", include("medical.urls")),
    path("api/", include("medications.urls")),
    path("api/", include("documents.urls")),
    path("api/", include("messaging.urls")),
    path("api/", include("lab_tests.urls")),
    path("api/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
