from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Balloon


class BalloonsClient(_Client):
    """
    Client for retrieving balloon information for contests.
    """
    def get_all_balloons(self, contest_id: Union[str, int], todo: bool = None) -> List[Balloon]:
        """
        Retrieve all balloons for a specified contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve balloons for.
            todo (bool, optional): If specified, filters balloons based on their 'todo' status.

        Returns:
            List[Balloon]: A list of Balloon objects for the given contest.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/balloons"
        params = {
            "todo": todo
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Balloon.model_validate(balloon) for balloon in response.json()]

    def mark_balloon_done(self, contest_id: Union[str, int], balloon_id: int) -> None:
        """
        Marks a balloon as delivered (done) for a specific contest.

        Sends a POST request to the API to update the status of the specified balloon.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            balloon_id (int): The ID of the balloon to mark as done.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/balloons/{balloon_id}/done"
        response = self.session.post(url)
        response.raise_for_status()