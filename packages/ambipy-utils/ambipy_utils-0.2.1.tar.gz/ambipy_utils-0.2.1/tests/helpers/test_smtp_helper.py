from unittest.mock import MagicMock, patch

import pytest

from ambipy_utils.helpers.smtp_helper import SMTPHelper


class TestSMTPHelper:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch(
            "ambipy_utils.helpers.smtp_helper.smtplib.SMTP"
        ) as mock_smtp:
            self.mock_smtp_instance = MagicMock()
            mock_smtp.return_value = self.mock_smtp_instance

            self.helper = SMTPHelper(
                sender_email="test@example.com",
                sender_password="password",
                smtp_host="smtp.example.com",
                smtp_port=587,
            )

            yield

    def test_setup_server(self):
        self.mock_smtp_instance.starttls.assert_called_once()
        self.mock_smtp_instance.login.assert_called_once_with(
            "test@example.com", "password"
        )

    def test_send_email(self):
        with patch(
            "ambipy_utils.helpers.smtp_helper.email.message.Message"
        ) as mock_msg:
            mock_email_instance = MagicMock()
            mock_msg.return_value = mock_email_instance

            self.helper.send_email(
                receivers=["receiver@example.com"],
                subject="Test Subject",
                body="<h1>Hello</h1>",
            )

            self.mock_smtp_instance.sendmail.assert_called_once()
            self.mock_smtp_instance.sendmail.assert_called_with(
                "test@example.com",
                ["receiver@example.com"],
                mock_email_instance.as_string().encode("utf-8"),
            )
