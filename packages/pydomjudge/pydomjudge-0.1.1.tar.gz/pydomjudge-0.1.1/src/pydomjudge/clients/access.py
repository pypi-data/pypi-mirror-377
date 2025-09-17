from typing import Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.response import AccessInformation


class AccessClient(_Client):
    """
    Client for retrieving access information for contests.
    """
    def get_access_information(self, contest_id: Union[str, int], strict: bool = False) -> AccessInformation:
        """
        Retrieves access information for a specific contest.

        Args:
            contest_id (Union[str, int]): The contest ID (path parameter).
            Example: "1"
            strict (bool, optional): Whether to only include CCS compliant properties in the response (query parameter).
            Default: False

        Returns:
            AccessInformation: Access information for the given contest.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails with status codes 400, 401, 403, or 404.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/access"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return AccessInformation.model_validate(response.json())