from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
	path('files/backup/', views.backup_data),
	path('files/', views.get_data),
]
