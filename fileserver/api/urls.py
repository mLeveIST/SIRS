from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('file/user/<int:user_id>/', views.file_list),
    path('file/<int:file_id>/user/<int:user_id>/', views.file_detail),
	path('files/recover/<int:server_id>/', views.recover_data),
	path('files/', views.get_data),
]