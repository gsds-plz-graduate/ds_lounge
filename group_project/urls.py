"""group_project URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import check.views
import common.views
import excelupload.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', common.views.home),
    path('google-login/', include('allauth.urls')),
    path('excel/', excelupload.views.excel_upload),
    path('check/', include('check.urls')),
    path('mypage/', check.views.mypage, name = "mypage"),
    path('common/', include('common.urls')),
    path('recommendation/', include('recommendation.urls'))
]
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
