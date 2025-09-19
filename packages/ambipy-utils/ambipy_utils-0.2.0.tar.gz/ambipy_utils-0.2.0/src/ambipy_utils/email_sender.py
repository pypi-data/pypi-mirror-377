import boto3


class EmailSender:
    """
    A class to send emails using AWS SES.
    Attributes:
        aws_access_key_id (str): AWS access key ID.
        aws_secret_access_key (str): AWS secret access key.
        aws_region (str): AWS region.
    Methods:
        send(
            receivers: list[str],
            subject: str,
            content: str,
            from_email: str,
            from_name: str,
        ):
            Sends an email to the specified receivers with
            the given subject and content.
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
    ):
        self.client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
        )

    def send(
        self,
        receivers: list[str],
        subject: str,
        content: str,
        from_email: str,
        from_name: str,
    ):
        """
        Sends an email to the specified receivers with the given subject
        and content.
        Args:
            receivers (list[str]): List of email addresses to send
            the email to.
            subject (str): Subject of the email.
            content (str): HTML content of the email.
            from_email (str): Sender's email address.
            from_name (str): Sender's name.
        Returns:
            {
                "MessageId": str,
                "ResponseMetadata": {
                    "RequestId": str,
                    "HTTPStatusCode": int,
                    "HTTPHeaders": dict,
                    "RetryAttempts": int,
                },
            }
        """
        response = self.client.send_email(
            Destination={
                "ToAddresses": receivers,
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": content,
                    },
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": subject,
                },
            },
            Source=f"{from_name} <{from_email}>",
        )

        return response
