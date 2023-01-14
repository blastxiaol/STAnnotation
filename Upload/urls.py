from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.upload, name='upload'),
    path(r'batch_upload', views.batch_upload, name='batch_upload')
]