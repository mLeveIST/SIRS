from django.urls import path
from . import views

urlpatterns = [
    path('user/register/', views.register),
    path('user/login/', views.LoginClass.as_view()),

    path('file/', views.file_list),
    path('file/<int:file_id>/', views.file_details),

    path('user/<str:username>/pubkey/', views.get_pubkey),
]
