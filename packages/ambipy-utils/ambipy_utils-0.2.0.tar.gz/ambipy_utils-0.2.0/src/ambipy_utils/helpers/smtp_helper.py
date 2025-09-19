import email.message
import smtplib


class SMTPHelper:
    """
    A class to send emails using SMTP.
    Attributes:
        sender_email (str): The email address of the sender.
        sender_password (str): The password for the sender's email account.
        smtp_host (str): The SMTP server host. Default is "smtp.gmail.com".
        smtp_port (int): The SMTP server port. Default is 587.
    """

    def __init__(
        self,
        sender_email: str,
        sender_password: str,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

        self.__setup_server()

    def __setup_server(self):
        """
        Sets up the SMTP server connection.
        """
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        self.smtp_server = server

    def send_email(self, receivers: list[str], subject: str, body: str):
        """
        Sends an email to the specified receivers.
        Args:
            receivers (list[str]): List of email addresses to send the email.
            subject (str): Subject of the email.
            body (str): HTML content of the email.
        """
        msg = email.message.Message()
        msg["Subject"] = subject
        msg.add_header("Content-Type", "text/html")
        msg.set_payload(body)

        self.smtp_server.sendmail(
            self.sender_email, receivers, msg.as_string().encode("utf-8")
        )
