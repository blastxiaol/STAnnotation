from django.urls import path
from . import views

urlpatterns = [
    path(r'add', views.add, name='add'),
    path(r'ishard', views.ishard, name='ishard')
]