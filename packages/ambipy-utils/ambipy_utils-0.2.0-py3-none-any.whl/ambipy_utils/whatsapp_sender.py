import requests


class WhatsAppSender:
    """
    WhatsAppSender class to send messages via Evolution WhatsApp API.
    Attributes:
        api_base_url (str): Base URL for the API.
        api_key (str): API key for authentication.
        instance_name (str): Instance name for the API.
    """

    api_base_url = str
    api_key = str
    instance_name = str

    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        instance_name: str,
    ):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.instance_name = instance_name

    def send_message(self, message: str, to: str):
        """
        Sends a message to a specified number via WhatsApp API.
        Args:
            message (str): The message to be sent.
            to (str): The recipient's phone number.
        Returns:
            dict: The response from the API:
            {
                "ok": bool,
                "status_code": int,
                "to": str,
            }
        """
        url = f"{self.api_base_url}/message/sendText/{self.instance_name}"
        body = {
            "number": to,
            "text": message,
        }
        headers = {
            "apikey": self.api_key,
        }

        try:
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as http_err:
            raise RuntimeError(
                f"HTTP error occurred: {http_err}"
            ) from http_err

        except Exception as err:
            raise RuntimeError(f"An error occurred: {err}") from err
