from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import include, path

def health_check(request):
    return JsonResponse({"status": "ok"})

def admin_portal(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff")
    return redirect("login")

def admin_login_redirect(request):
    return redirect("login")

urlpatterns = [
    path("healthz/", health_check, name="health_check"),
    path("admin/login/", admin_login_redirect),
    path("admin/", admin_portal),
    path("django-admin/", admin.site.urls),
    path("staff/", include("quizzes.staff_urls")),
    path("", include("quizzes.urls")),
]
