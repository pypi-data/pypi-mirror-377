from unittest.mock import MagicMock, patch

import pytest
import requests

from ambipy_utils.clickup_service import ClickupService


class TestClickupService:
    @staticmethod
    @patch("ambipy_utils.clickup_service.requests.post")
    def test_create_task_success(mock_post):
        ID = "12345"
        NAME = "Test Task"
        DESCRIPTION = "This is a test task"
        ASSIGNEES = [1, 2]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": ID,
            "name": NAME,
            "description": DESCRIPTION,
            "assignees": ASSIGNEES,
        }
        mock_post.return_value = mock_response

        clickup_service = ClickupService(api_token="fake_api_token")
        response = clickup_service.create_task(
            name=NAME,
            description=DESCRIPTION,
            assignees=ASSIGNEES,
            priority=1,
            list_id=1234567890,
        )

        assert response["id"] == ID
        assert response["name"] == NAME
        assert response["description"] == DESCRIPTION
        assert response["assignees"] == ASSIGNEES
        assert mock_post.called
        assert mock_post.call_count == 1
        assert mock_post.call_args[1]["json"] == {
            "name": NAME,
            "markdown_description": DESCRIPTION,
            "assignees": ASSIGNEES,
            "priority": 1,
        }

    @staticmethod
    @patch("ambipy_utils.clickup_service.requests.post")
    def test_create_task_failure(mock_post):
        LIST_ID = 1234567890
        err_msg = (
            f"HTTP error occurred: 401 Client Error: "
            f"Unauthorized for url: https://api.clickup.com/api/v2/list/{LIST_ID}/task"
        )
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            err_msg
        )
        mock_response.json.return_value = {
            "err": err_msg,
        }
        mock_post.return_value = mock_response

        clickup_service = ClickupService(api_token="wrong_token")

        with pytest.raises(RuntimeError) as excinfo:
            clickup_service.create_task(
                name="Test Task",
                description="This is a test task",
                assignees=[1, 2],
                priority=1,
                list_id=LIST_ID,
            )
        assert str(excinfo.value) == (f"HTTP error occurred: {err_msg}")
