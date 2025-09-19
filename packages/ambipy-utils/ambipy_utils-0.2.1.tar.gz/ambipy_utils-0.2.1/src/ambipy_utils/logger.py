import logging
import traceback
from typing import Optional, TypedDict

from ambipy_utils.helpers.smtp_helper import SMTPHelper


class ErrorEmailSenderType(TypedDict):
    email: str
    password: str


class Logger:
    error_email_sender: Optional[ErrorEmailSenderType]
    email_helper: SMTPHelper = None
    app_name = str
    error_email_receivers = Optional[list[str]]

    def __init__(
        self,
        error_email_sender: Optional[ErrorEmailSenderType] = None,
        error_email_receivers: list[str] = [],
        app_name: str = "",
    ):
        if error_email_sender:
            self.email_helper = SMTPHelper(
                sender_email=error_email_sender["email"],
                sender_password=error_email_sender["password"],
            )

        self.error_email_sender = error_email_sender
        self.error_email_receivers = error_email_receivers
        self.app_name = app_name

        logging.basicConfig(
            filename=".log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    @staticmethod
    def log_info(message: str):
        logging.info(message)

    def log_error(self, message: str):
        err_msg = f"{message}: {traceback.format_exc()}"
        logging.error(err_msg)

        if self.error_email_sender and self.error_email_receivers:
            self.email_helper.send_email(
                receivers=self.error_email_receivers,
                subject=f"Erro na aplicação {self.app_name}",
                body=err_msg,
            )
