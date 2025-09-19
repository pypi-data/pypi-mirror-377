from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from ambipy_utils.email_sender import EmailSender


class TestEmailSender:
    @staticmethod
    @patch("boto3.client")
    def test_send_email_success(mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.send_email.return_value = {
            "MessageId": "12345",
            "ResponseMetadata": {
                "RequestId": "req-123",
                "HTTPStatusCode": HTTPStatus.OK,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
        }

        email_sender = EmailSender(
            aws_access_key_id="fake_id",
            aws_secret_access_key="fake_secret",
            aws_region="us-east-1",
        )

        receivers = ["test@example.com"]
        subject = "Test Subject"
        content = "<p>Test Content</p>"
        from_email = "sender@example.com"
        from_name = "Sender Name"

        response = email_sender.send(
            receivers, subject, content, from_email, from_name
        )

        assert response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        mock_client.send_email.assert_called_once()
        called_args = mock_client.send_email.call_args[1]
        assert "Destination" in called_args
        assert "Message" in called_args
        assert "Source" in called_args

    @staticmethod
    @patch("boto3.client")
    def test_send_email_failure(mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.send_email.side_effect = Exception("SES error")

        email_sender = EmailSender(
            aws_access_key_id="fake_id",
            aws_secret_access_key="fake_secret",
            aws_region="us-east-1",
        )

        receivers = ["test@example.com"]
        subject = "Test Subject"
        content = "<p>Test Content</p>"
        from_email = "sender@example.com"
        from_name = "Sender Name"

        with pytest.raises(Exception, match="SES error"):
            email_sender.send(
                receivers, subject, content, from_email, from_name
            )
