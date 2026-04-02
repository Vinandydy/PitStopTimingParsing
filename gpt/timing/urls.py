from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tracks', views.TrackViewSet, basename='track')
router.register(r'drivers', views.DriverViewSet, basename='driver')
router.register(r'karts', views.KartViewSet, basename='kart')
router.register(r'heats', views.HeatViewSet, basename='heat')

urlpatterns = [
    path('', include(router.urls)),
]
