# backend/api/views.py

import json

import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import Driver, Heat, HeatParticipation, Kart, Track

from .filters import HeatFilter, HeatParticipationFilter
from .serializers import (
    DriverSerializer,
    HeatDetailSerializer,
    HeatParticipationSerializer,
    HeatSerializer,
    KartSerializer,
    TrackSerializer,
)

# ============================================================================
# ViewSets
# ============================================================================

class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']


class KartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Kart.objects.select_related('track').all()
    serializer_class = KartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['track', 'is_active']
    search_fields = ['number']
    ordering_fields = ['number', 'total_races', 'best_lap_ms']


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Driver.objects.select_related('track').all()
    serializer_class = DriverSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['track', 'team']
    search_fields = ['name']
    ordering_fields = ['name', 'total_races', 'best_lap_ms']


class HeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Heat.objects.select_related('track').prefetch_related(
        'results__driver', 'results__kart'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HeatFilter
    search_fields = ['name', 'championship']
    ordering_fields = ['scheduled_at', 'name']
    ordering = ['-scheduled_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HeatDetailSerializer
        return HeatSerializer


class HeatParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeatParticipation.objects.select_related(
        'heat', 'driver', 'kart', 'heat__track'
    ).all()
    serializer_class = HeatParticipationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HeatParticipationFilter
    search_fields = ['driver__name']
    ordering_fields = ['position', 'best_lap_ms', 'avg_lap_ms', 'heat__scheduled_at']
    ordering = ['position']


# ============================================================================
# AI Endpoint
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_generate(request):
    """Проксирует запрос к локальному QWEN через Ollama."""
    prompt = request.data.get('prompt', '')
    context = request.data.get('context', {})
    model = request.data.get('model', 'qwen2.5:7b')
    temperature = request.data.get('temperature', 0.2)
    max_tokens = request.data.get('max_tokens', 512)

    system_prompt = """Ты — эксперт по картингу и спортивной аналитике.
Анализируй статистику, давай конкретные, измеримые советы.
Отвечай на русском, кратко, с цифрами. Избегай общих фраз."""

    # Форматируем данные заезда (если есть results в context)
    heat_data_formatted = ""
    if context.get('results'):
        results = context['results']
        results_sorted = sorted(results, key=lambda x: x.get('position', 999))

        lines = [
            f"Название: {context.get('name', 'Без названия')}",
            f"Трек: {context.get('track_name', '—')}",
            f"Дата: {context.get('scheduled_at', '')[:10] if context.get('scheduled_at') else '—'}",
            f"Тип: {context.get('session_type', 'Race')}",
            f"Чемпионат: {context.get('championship', '—')}",
            f"План кругов: {context.get('laps_count', '—')}",
            "",
            "РЕЗУЛЬТАТЫ (позиция | гонщик | карт | лучший круг мс | средний круг мс | круги | S1 | S2 | S3):"
        ]

        for r in results_sorted[:15]:
            best_fmt = _format_ms(r.get('best_lap_ms', 0))
            avg_fmt = _format_ms(r.get('avg_lap_ms', 0))
            lines.append(
                f"{r.get('position')}. {r.get('driver_name')} | "
                f"карт #{r.get('kart_number')} | "
                f"лучший: {r.get('best_lap_ms', 0)}мс ({best_fmt}) | "
                f"средний: {r.get('avg_lap_ms', 0)}мс ({avg_fmt}) | "
                f"круги: {r.get('laps_completed', 0)} | "
                f"S1:{r.get('s1_laps', 0)}/S2:{r.get('s2_laps', 0)}/S3:{r.get('s3_laps', 0)}"
            )

        if results_sorted:
            best_overall = min(
                (r for r in results_sorted if r.get('best_lap_ms', 0) > 0),
                key=lambda x: x['best_lap_ms'],
                default=None
            )
            if best_overall:
                lines.append(
                    f"\nАБСОЛЮТНЫЙ ЛУЧШИЙ КРУГ: {best_overall['driver_name']} — "
                    f"{best_overall['best_lap_ms']}мс ({_format_ms(best_overall['best_lap_ms'])})"
                )

        heat_data_formatted = "\n".join(lines)

    # Формируем финальный промпт
    if heat_data_formatted:
        full_prompt = f"""{system_prompt}

<данные_заезда>
{heat_data_formatted}
</данные_заезда>

<запрос>
{prompt}
</запрос>

Ответь НА РУССКОМ, кратко, по структуре:

🏆 ПОДИУМ
• 1 место: {{имя}} (карт #{{номер}}), лучший круг: {{время}}
• 2 место: {{имя}} (карт #{{номер}}), лучший круг: {{время}}
• 3 место: {{имя}} (карт #{{номер}}), лучший круг: {{время}}

⚡ ЛУЧШИЙ КРУГ ЗАЕЗДА
• {{имя}}: {{время}} (абсолютный рекорд)

🔄 СТРАТЕГИЯ ПИТ-СТОПОВ (по S1)
• Раньше всех сменил карт: {{имя}} (S1: {{кол-во}} кругов)
• Позже всех сменил карт: {{имя}} (S1: {{кол-во}} кругов)

📊 СТАБИЛЬНОСТЬ
• Самый стабильный: {{имя}} (разница лучший/средний: {{X}} сек)

💡 КОНКРЕТНЫЕ СОВЕТЫ
• {{имя}}: {{измеримый совет на основе данных}}"""
    else:
        full_prompt = f"""{system_prompt}

<данные>
{json.dumps(context, ensure_ascii=False, indent=2)}
</данные>

<запрос>
{prompt}
</запрос>

Ответ:"""

    ollama_url = "http://ollama:11434"

    try:
        response = requests.post(
            f'{ollama_url}/api/generate',
            json={
                'model': model,
                'prompt': full_prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_p': 0.9,
                }
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        return Response({
            'insight': result.get('response', ''),
            'model': model,
            'tokens_used': result.get('eval_count', 0),
            'duration_ms': result.get('eval_duration', 0) // 1000000 if result.get('eval_duration') else 0,
        })

    except requests.exceptions.ConnectionError:
        return Response({'error': 'Не удалось подключиться к Ollama'}, status=503)
    except requests.exceptions.Timeout:
        return Response({'error': 'Таймаут. Попробуйте уменьшить max_tokens'}, status=504)
    except Exception as e:
        return Response({'error': f'Ошибка AI: {str(e)}'}, status=500)


# ============================================================================
# Helper Functions
# ============================================================================

def _format_ms(ms: int) -> str:
    """Форматирует миллисекунды в MM:SS.mmm или SS.mmm"""
    if not ms or ms <= 0:
        return '—'
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}" if minutes else f"{seconds}.{milliseconds:03d}"
