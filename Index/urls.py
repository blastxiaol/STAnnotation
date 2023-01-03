from django.urls import path
from . import views

app_name = 'Index'

urlpatterns = [
    path(r'', views.index, name='index')
]