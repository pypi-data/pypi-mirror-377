from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import TeamCategory


class GroupsClient(_Client):
    """
    Client for retrieving team group information for contests.
    """
    def get_all_groups(self, contest_id: Union[str, int], idlist: List[str] = None, public: bool = None,
                       strict: bool = False) -> List[TeamCategory]:
        """
        Retrieve all team groups for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to fetch groups for.
            idlist (List[str], optional): A list of group IDs to filter the results. Defaults to None.
            public (bool, optional): If set, filters groups by their public status. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[TeamCategory]: A list of TeamCategory objects representing the groups.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/groups"
        params = {
            "ids[]": idlist,
            "public": public,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [TeamCategory.model_validate(group) for group in response.json()]

    def add_group(self, contest_id: Union[str, int], group_data: dict, strict: bool = False) -> TeamCategory:
        """
        Adds a new group to a specified contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to which the group will be added.
            group_data (dict): A dictionary containing the group's data to be created.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            TeamCategory: An instance of TeamCategory representing the newly created group.

        Raises:
            requests.HTTPError: If the HTTP request to the server fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/groups"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=group_data)
        response.raise_for_status()
        return TeamCategory.model_validate(response.json())

    def get_group(self, contest_id: Union[str, int], group_id: str, strict: bool = False) -> TeamCategory:
        """
        Retrieve a specific group (team category) for a given contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            group_id (str): The ID of the group (team category) to retrieve.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            TeamCategory: The retrieved team category object.

        Raises:
            requests.HTTPError: If the HTTP request fails.
            pydantic.ValidationError: If the response cannot be validated as a TeamCategory.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/groups/{group_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return TeamCategory.model_validate(response.json())