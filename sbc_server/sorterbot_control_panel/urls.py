from django.urls import path
from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('arms', views.ArmViewSet)
router.register('sessions', views.SessionViewSet)
router.register('ui', views.UIViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('get_cloud_ip/', views.get_cloud_ip, name='get_cloud_ip'),
    path('send_connection_status/', views.send_connection_status, name='send_connection_status'),
    path('log/', views.log, name='log'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
