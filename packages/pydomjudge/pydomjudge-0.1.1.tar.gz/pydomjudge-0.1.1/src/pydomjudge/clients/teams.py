from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Team


class TeamsClient(_Client):
    """
    Client for retrieving and managing team information for contests.
    """
    def get_all_teams(self, contest_id: Union[str, int], idlist: List[str] = None, category: str = None,
                      affiliation: str = None, public: bool = None, strict: bool = False) -> List[Team]:
        """
        Retrieve all teams for a specified contest, with optional filters.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            idlist (List[str], optional): List of team IDs to filter.
            category (str, optional): Category to filter teams.
            affiliation (str, optional): Affiliation to filter teams.
            public (bool, optional): Filter by public teams.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Team]: List of Team objects.

        Raises:
            requests.HTTPError: If the request to the server fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams"
        params = {
            "ids[]": idlist,
            "category": category,
            "affiliation": affiliation,
            "public": public,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Team.model_validate(team) for team in response.json()]

    def get_team(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> Team:
        """
        Retrieve a team's information.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            team_id (str): The team identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Team: The requested team object.

        Raises:
            requests.HTTPError: If the request to the server fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Team.model_validate(response.json())

    def add_team(self, contest_id: Union[str, int], team_data: dict, strict: bool = False) -> Team:
        """
        Adds a new team to a specified contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to add the team to.
            team_data (dict): A dictionary containing the team's data.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Team: The created Team object.

        Raises:
            requests.HTTPError: If the request to the server fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=team_data)
        response.raise_for_status()
        return Team.model_validate(response.json())

    def update_team(self, contest_id: Union[str, int], team_id: str, team_data: dict, strict: bool = False) -> Team:
        """
        Update a team's information.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            team_id (str): The team identifier.
            team_data (dict): The updated team data.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Team: The updated team object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=team_data)
        response.raise_for_status()
        return Team.model_validate(response.json())

    def delete_team(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> None:
        """
        Delete a team from a specified contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            team_id (str): The team identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()

    def get_team_photo(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> bytes:
        """
        Get a team's photo.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            team_id (str): The team identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The photo file content.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}/photo"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def set_team_photo(self, contest_id: Union[str, int], team_id: str, photo: bytes, strict: bool = False) -> None:
        """
        Set or update a team's photo.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            team_id (str): The team identifier.
            photo (bytes): The photo file content.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}/photo"
        params = {
            "strict": strict
        }
        files = {
            "photo": photo
        }
        response = self.session.put(url, params=params, files=files)
        response.raise_for_status()

    def delete_team_photo(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> None:
        """
        Delete a team's photo.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            team_id (str): The team identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}/photo"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()