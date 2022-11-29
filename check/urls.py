from django.urls import path

from . import views

app_name = "check"

urlpatterns = [
    path('uploaded/', views.uploaded, name = "uploaded")
]
