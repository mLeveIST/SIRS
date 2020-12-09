from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

urlpatterns = [
	path('users/register/', views.register_user),
	path('users/login/', obtain_auth_token),

	path('files/', views.files_detail),
	path('files/<int:file_id>/', views.file_detail),

	path('files/<int:file_id>/users/', views.get_file_contributors),
	path('users/<str:username>/', views.get_user_pubkey),

	path('files/<int:file_id>/report/', views.report_file),
	path('files/backup/', views.backup_data),
]
