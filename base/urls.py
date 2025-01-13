from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home, 'home'),
    path('room', views.room, name='room'),
    ]