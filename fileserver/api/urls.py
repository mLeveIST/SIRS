from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
	path('files/', views.upload_file),
	path('files/<int:file_id>/', views.update_file),

	path('users/<int:user_id>/files/', views.list_files),
	path('users/<int:user_id>/files/<int:file_id>/', views.download_file),

	path('data/recover/<int:bserver_id>/', views.recover_data),
	path('data/<int:file_id>/', views.get_file_data),
	path('data/', views.get_data),
]
