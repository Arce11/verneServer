from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('monitor/<str:rover_id>/', views.monitor, name='monitor'),
    path('monitor_old/<str:rover_id>/', views.monitor_old, name='monitor_old'),
    path('api/rover/', views.RoverAPI.as_view(), name='api_rovers'),
    path('api/session/', views.SessionAPI.as_view(), name='api_sessions'),
    path('api/rover/<str:pk>/', views.SpecificRoverAPI.as_view(), name='api_rover'),
    path('api/session/<str:pk>/', views.SpecificSessionAPI.as_view(), name='api_session'),
]