from django.urls import path

from common import views

app_name = "common"

urlpatterns = [
    path('inclugrd/', views.inclugrd, name = "inclugrd"),
    path('shreyn/', views.shreyn, name = "shreyn"),
    path('share/', views.share, name = "share"),
    path('detail/<int:user_id>/', views.sharedetail, name = "detail")
]
