from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Clarification
from pydomjudge.models.request import ClarificationPost


class ClarificationsClient(_Client):
    """
    Client for retrieving clarification information for contests.
    """
    def get_all_clarifications(self, contest_id: Union[str, int], idlist: List[Union[str, int]] = None, problem: Union[str, int] = None, strict: bool = False) -> List[Clarification]:
        """
        Retrieve all clarifications for a specific contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to fetch clarifications for.
            idlist (List[Union[str, int]], optional): A list of clarification IDs to filter the results. Defaults to None.
            problem (Union[str, int], optional): The problem ID to filter clarifications by a specific problem. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Clarification]: A list of Clarification objects retrieved from the contest.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/clarifications"
        params = {
            "ids[]": idlist,
            "problem": problem,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Clarification.model_validate(clarification) for clarification in response.json()]

    def get_clarification(self, contest_id: Union[str, int], clarification_id: Union[str, int], strict: bool = False) -> Clarification:
        """
        Retrieve a specific clarification for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            clarification_id (Union[str, int]): The ID of the clarification to retrieve.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Clarification: The clarification object corresponding to the provided IDs.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            pydantic.ValidationError: If the response data cannot be validated as a Clarification.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/clarifications/{clarification_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Clarification.model_validate(response.json())

    def add_clarification(self, contest_id: Union[str, int], clarification: ClarificationPost) -> Clarification:
        """
        Adds a new clarification to the specified contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to which the clarification will be added.
            clarification (ClarificationPost): The clarification data to be posted.

        Returns:
            Clarification: The created clarification object as returned by the API.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/clarifications"
        response = self.session.post(url, json=clarification)
        response.raise_for_status()
        return Clarification.model_validate(response.json())