from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('files/users/<int:user_id>/', views.file_list),
    path('files/<int:file_id>/users/<int:user_id>/', views.file_detail),
    path('files/recover/<int:server_id>/', views.recover_data),
    path('files/', views.get_data),
]
