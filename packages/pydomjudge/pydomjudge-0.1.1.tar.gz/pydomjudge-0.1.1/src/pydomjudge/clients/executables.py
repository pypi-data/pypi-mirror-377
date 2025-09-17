from typing import Dict

from pydomjudge.clients.client import _Client


class ExecutablesClient(_Client):
    """
    Client for retrieving executable information from the API.
    """
    def get_executable(self, executable_id: str, strict: bool = False) -> Dict:
        """
        Retrieve information about a specific executable by its ID.

        Args:
            executable_id (str): The unique identifier of the executable to retrieve.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: A dictionary containing the executable's details as validated by the model.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
        """
        url = f"{self.base_url}/api/v4/executables/{executable_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return self.model_validate(response.json())