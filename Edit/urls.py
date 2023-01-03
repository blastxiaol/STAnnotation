from django.urls import path
from . import views

urlpatterns = [
    path(r'get_list/user_id=<int:user_id>', views.get_list, name='get_list'),
    path(r'get_instance', views.get_instance, name='get_instance'),
    path(r'submit_data', views.submit_data, name='submit_data'),
]