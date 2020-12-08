from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
	path('files/', views.upload_file),
	path('files/<int:file_id>/', views.update_file),

	path('users/<int:user_id>/files/', views.get_files),
	path('users/<int:user_id>/files/<int:file_id>/', views.get_file),

	path('data/recover/<int:bserver_id>/', views.recover_data),
	path('data/', views.get_data),
]
