from django.urls import path
from . import views

 
urlpatterns = [
    path('', views.index, name='index'),
    path('monitor/<str:rover_id>/', views.monitor, name='monitor')
]