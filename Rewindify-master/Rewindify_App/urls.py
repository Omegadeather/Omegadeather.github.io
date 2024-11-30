from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("authorize/", include("authorize.urls")),
    path("authorize/", include("django.contrib.auth.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]
