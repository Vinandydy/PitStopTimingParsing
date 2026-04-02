import os

import requests
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Track, Kart, Driver, Heat
from .serializers import (
    TrackSerializer, KartSerializer, DriverSerializer,
    HeatListSerializer, HeatDetailSerializer
)


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для треков"""
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['slug', 'name']


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для гонщиков"""
    queryset = Driver.objects.select_related('track').all()
    serializer_class = DriverSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['track']
    search_fields = ['name', 'team']


class KartViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для картов"""
    queryset = Kart.objects.select_related('track').all()
    serializer_class = KartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['track', 'is_active']
    search_fields = ['number']


class HeatViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для заездов"""
    queryset = Heat.objects.select_related('track').prefetch_related(
        'results__driver', 'results__kart'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['track', 'session_type', 'championship']
    ordering_fields = ['scheduled_at']
    ordering = ['-scheduled_at']
    search_fields = ['name', 'external_id']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HeatDetailSerializer
        return HeatListSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def ai_generate(request):
    """Проксирует AI-запрос в Ollama и возвращает инсайт."""
    prompt = request.data.get("prompt", "").strip()
    context = request.data.get("context", {})
    model = request.data.get("model", "qwen2.5:7b")
    temperature = float(request.data.get("temperature", 0.2))
    max_tokens = int(request.data.get("max_tokens", 512))

    if not prompt:
        return Response({"error": "Поле 'prompt' обязательно"}, status=400)

    full_prompt = (
        "Ты аналитик картинговых заездов. Отвечай кратко, на русском, по цифрам.\n\n"
        f"КОНТЕКСТ:\n{context}\n\n"
        f"ЗАПРОС:\n{prompt}\n"
    )

    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        return Response(
            {
                "insight": data.get("response", ""),
                "model": model,
                "tokens_used": data.get("eval_count", 0),
                "duration_ms": data.get("eval_duration", 0) // 1_000_000 if data.get("eval_duration") else 0,
            }
        )
    except requests.exceptions.ConnectionError:
        return Response({"error": "Не удалось подключиться к Ollama"}, status=503)
    except requests.exceptions.Timeout:
        return Response({"error": "Таймаут AI-запроса"}, status=504)
    except Exception as exc:
        return Response({"error": f"Ошибка AI: {exc}"}, status=500)
