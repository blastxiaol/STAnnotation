from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.download, name='download')
]