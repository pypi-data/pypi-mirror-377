from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Award


class AwardsClient(_Client):
    """
    Client for retrieving award information for contests.
    """
    def get_all_awards(self, contest_id: Union[str, int], strict: bool = False) -> List[Award]:
        """
        Get all the awards standings for a contest.

        Parameters:
            contest_id (Union[str, int]): The contest ID.
            strict (bool): Whether to only include CCS compliant properties.

        Returns:
            List[Award]: List of Award objects.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/awards"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Award.model_validate(award) for award in response.json()]

    def get_award(self, contest_id: Union[str, int], award_id: str, strict: bool = False) -> Award:
        """
        Retrieve a specific award for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            award_id (str): The ID of the award to retrieve.
            strict (bool, optional): Whether to enforce strict validation. Defaults to False.

        Returns:
            Award: The Award object corresponding to the specified contest and award.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
            pydantic.ValidationError: If the response data cannot be validated as an Award.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/awards/{award_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Award.model_validate(response.json())