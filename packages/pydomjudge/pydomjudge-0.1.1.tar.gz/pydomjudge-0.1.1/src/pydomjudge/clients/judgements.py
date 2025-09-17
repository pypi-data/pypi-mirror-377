from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Judging


class JudgementsClient(_Client):
    """
    Client for retrieving judgement information for contests.
    """
    def get_all_judgements(self, contest_id: Union[str, int], idlist: List[str] = None, result: str = None,
                           submission_id: str = None, strict: bool = False) -> List[Judging]:
        """
        Retrieve all judgements for a specific contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve judgements from.
            idlist (List[str], optional): A list of judgement IDs to filter the results. Defaults to None.
            result (str, optional): Filter judgements by result (e.g., 'accepted', 'rejected'). Defaults to None.
            submission_id (str, optional): Filter judgements by submission ID. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Judging]: A list of Judging objects representing the retrieved judgements.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgements"
        params = {
            "ids[]": idlist,
            "result": result,
            "submission_id": submission_id,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Judging.model_validate(judgement) for judgement in response.json()]

    def get_judgement(self, contest_id: Union[str, int], judgement_id: str, strict: bool = False) -> Judging:
        """
        Retrieve a specific judgement for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            judgement_id (str): The ID of the judgement to retrieve.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Judging: The validated Judging object corresponding to the requested judgement.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
            pydantic.ValidationError: If the response data cannot be validated as a Judging object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgements/{judgement_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Judging.model_validate(response.json())