from django.urls import path
from . import views

urlpatterns = [
    # เครื่องหมาย '' แปลว่า หน้าแรกสุดของแอปนี้
    path('', views.home, name='home'),

]