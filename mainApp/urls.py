from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('monitor/<str:rover_id>/', views.monitor, name='monitor'),
    path('api/rover', views.monitor, name='api_rover'),
    path('api/data', views.monitor, name='api_data'),

]