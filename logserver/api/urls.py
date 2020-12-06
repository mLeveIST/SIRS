from django.urls import path
from . import views

urlpatterns = [
    path('users/register/', views.register),
    path('users/login/', views.LoginClass.as_view()),

    path('files/', views.file_list),
    path('files/<int:file_id>/', views.file_details),

    path('users/<str:username>/pubkey/', views.get_pubkey),
]
