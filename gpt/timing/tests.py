from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from timing.views import ai_generate


class AIEndpointTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("timing.views.requests.post")
    def test_ai_generate_uses_chat_response(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "chat insight"},
            "eval_count": 10,
            "eval_duration": 1_000_000,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        request = self.factory.post("/api/ai/generate/", {"prompt": "test", "context": {}}, format="json")
        response = ai_generate(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["insight"], "chat insight")

    @patch("timing.views.requests.post")
    def test_ai_generate_falls_back_to_generate(self, mock_post):
        chat_response = Mock()
        chat_response.status_code = 404
        chat_response.text = "not found"

        generate_response = Mock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "response": "generate insight",
            "eval_count": 12,
            "eval_duration": 2_000_000,
        }
        generate_response.raise_for_status = Mock()

        mock_post.side_effect = [chat_response, generate_response]

        request = self.factory.post("/api/ai/generate/", {"prompt": "test", "context": {}}, format="json")
        response = ai_generate(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["insight"], "generate insight")
