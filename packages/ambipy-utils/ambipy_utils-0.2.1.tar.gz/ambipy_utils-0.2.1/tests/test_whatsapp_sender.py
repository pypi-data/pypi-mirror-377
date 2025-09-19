from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests

from ambipy_utils.whatsapp_sender import WhatsAppSender


class TestWhatsAppSender:
    API_BASE_URL = "https://api.example.com"
    API_KEY = "fake_api_key"
    INSTANCE_NAME = "test_instance"

    @patch("ambipy_utils.whatsapp_sender.requests.post")
    def test_send_message(self, mock_post):
        PHONE_NUMBER = "1234567890"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "status_code": HTTPStatus.CREATED,
            "to": PHONE_NUMBER,
        }
        mock_response.status_code = HTTPStatus.CREATED
        mock_post.return_value = mock_response

        whatsapp_sender = WhatsAppSender(
            api_base_url=self.API_BASE_URL,
            api_key=self.API_KEY,
            instance_name=self.INSTANCE_NAME,
        )

        response = whatsapp_sender.send_message("Hello", PHONE_NUMBER)

        assert response["ok"] is True
        assert response["status_code"] == HTTPStatus.CREATED
        assert response["to"] == PHONE_NUMBER
        assert mock_post.called
        assert mock_post.call_count == 1

    @patch("ambipy_utils.whatsapp_sender.requests.post")
    def test_send_message_http_error(self, mock_post):
        mock_response = MagicMock()
        error_msg = (
            f"400 Client Error: Bad Request for url: "
            f"{self.API_BASE_URL}/message/sendText/{self.INSTANCE_NAME}"
        )
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            error_msg
        )
        mock_response.json.return_value = {
            "ok": False,
            "status_code": HTTPStatus.BAD_REQUEST,
            "reason": "Bad Request",
        }
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_post.return_value = mock_response

        whatsapp_sender = WhatsAppSender(
            api_base_url=self.API_BASE_URL,
            api_key=self.API_KEY,
            instance_name=self.INSTANCE_NAME,
        )

        with pytest.raises(RuntimeError) as excinfo:
            whatsapp_sender.send_message("Hello", None)
        assert str(excinfo.value) == f"HTTP error occurred: {error_msg}"
