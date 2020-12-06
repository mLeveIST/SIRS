from django.urls import path
from . import views

urlpatterns = [
    path('file/user/<int:user_id>/', views.file_list),
    path('file/<int:file_id>/user/<int:user_id>/', views.file_detail),
]
