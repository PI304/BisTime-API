"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

api_info = openapi.Info(
    title="BisTime - API Doc",
    default_version="v1",
    description="BisTime Application을 위한 API 문서",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="earthlyz9.dev@gmail.com"),
)

SchemaView = get_schema_view(
    api_info,
    public=True,
    permission_classes=([permissions.AllowAny]),
    validators=["flex"],
)


def health_check_view(request):
    return HttpResponse(status=200)


urlpatterns = [
    path("health-check", health_check_view, name="health-check"),
    re_path(r"^api", include("config.urls_v1")),
]
