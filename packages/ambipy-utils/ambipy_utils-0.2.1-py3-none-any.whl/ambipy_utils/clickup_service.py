import requests

from ambipy_utils.helpers.enums import Lists, Priority, Users


class ClickupService:
    """
    A class that provides methods to interact with the ClickUp API.
    """

    API_BASE_URL = "https://api.clickup.com/api/v2"
    API_TOKEN: str

    def __init__(self, api_token: str):
        self.API_TOKEN = api_token

    def create_task(
        self,
        name: str,
        description: str,
        assignees: list[int] = [Users.FABIO_SOUZA],
        priority: Priority = Priority.HIGHT,
        list_id: Lists = Lists.GEOPROCESSAMENTO_GERAL,
    ):
        """
        Create a task in ClickUp.
        Args:
            name (str): The name of the task.
            description (str): The description of the task.
            assignees (list[int]): List of user IDs to assign the task to.
            priority (Priority): Priority level of the task.
            list_id (Lists): ID of the list where the task will be created.
        """
        body = {
            "name": name,
            "markdown_description": description,
            "assignees": assignees,
            "priority": priority,
        }
        headers = {
            "Authorization": self.API_TOKEN,
        }

        try:
            response = requests.post(
                f"{self.API_BASE_URL}/list/{list_id}/task",
                json=body,
                headers=headers,
            )
            response.raise_for_status()

            return response.json()

        except requests.HTTPError as http_err:
            raise RuntimeError(
                f"HTTP error occurred: {http_err}"
            ) from http_err

        except Exception:
            raise Exception(
                f"Erro ao criar task no Clickup. Erro: {response.text}"
            )
