from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import JudgementType


class JudgeTypesClient(_Client):
    """
    Client for retrieving judgement type information for contests.
    """
    def get_all_judgement_types(self, contest_id: Union[str, int], idlist: List[str] = None,
                                strict: bool = False) -> List[JudgementType]:
        """
        Retrieve all judgement types for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve judgement types for.
            idlist (List[str], optional): A list of judgement type IDs to filter the results. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[JudgementType]: A list of JudgementType objects representing the judgement types for the contest.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgement-types"
        params = {
            "ids[]": idlist,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [JudgementType.model_validate(judgement_type) for judgement_type in response.json()]

    def get_judgement_type(self, contest_id: Union[str, int], judgement_type_id: str,
                           strict: bool = False) -> JudgementType:
        """
        Retrieve a specific judgement type for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            judgement_type_id (str): The ID of the judgement type to retrieve.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            JudgementType: The retrieved judgement type object.

        Raises:
            requests.HTTPError: If the HTTP request fails.
            pydantic.ValidationError: If the response data is invalid for JudgementType.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgement-types/{judgement_type_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return JudgementType.model_validate(response.json())