from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tracks', views.TrackViewSet)
router.register(r'karts', views.KartViewSet)
router.register(r'drivers', views.DriverViewSet)
router.register(r'heats', views.HeatViewSet)
router.register(r'results', views.HeatParticipationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ai/generate/', views.ai_generate, name='ai-generate'),
]
