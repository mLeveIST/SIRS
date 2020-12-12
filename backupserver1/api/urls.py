from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
	path('data/backup/', views.backup_data),
	path('data/', views.get_data),
]
