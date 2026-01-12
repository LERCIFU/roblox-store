from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='task'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('complete/<int:pk>/', views.complete_task, name='complete_task'),
]