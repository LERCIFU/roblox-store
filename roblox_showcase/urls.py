# roblox_showcase/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='roblox_home'), # ตั้งชื่อว่า roblox_home
]