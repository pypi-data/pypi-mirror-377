import traceback
from unittest.mock import MagicMock, patch

from ambipy_utils.logger import Logger


class TestLogger:
    @staticmethod
    def test_log_info(caplog):
        with caplog.at_level("INFO"):
            Logger.log_info("Testing info log")

        assert "Testing info log" in caplog.text

    @staticmethod
    def test_log_error_without_email(caplog):
        logger = Logger()

        with caplog.at_level("ERROR"):
            try:
                raise ValueError("Test error")
            except Exception:
                logger.log_error("An error occurred")

        assert "An error occurred" in caplog.text
        assert "ValueError" in caplog.text

    @staticmethod
    @patch("ambipy_utils.logger.SMTPHelper")
    def test_log_error_with_email(mock_smtp_helper):
        mock_instance = MagicMock()
        mock_smtp_helper.return_value = mock_instance

        APP_NAME = "TestApp"
        ERR_MSG = "An error occurred"
        TRACEBACK_MSG = ""

        sender = {"email": "example@email.com", "password": "senha"}
        receivers = ["admin@email.com"]
        logger = Logger(
            error_email_sender=sender,
            error_email_receivers=receivers,
            app_name=APP_NAME,
        )

        try:
            raise RuntimeError("Test error")
        except Exception:
            TRACEBACK_MSG = traceback.format_exc()
            logger.log_error(ERR_MSG)

        mock_instance.send_email.assert_called_once()
        _, kwargs = mock_instance.send_email.call_args

        assert kwargs["receivers"] == receivers
        assert kwargs["subject"] == f"Erro na aplicação {APP_NAME}"
        assert kwargs["body"] == f"{ERR_MSG}: {TRACEBACK_MSG}"
