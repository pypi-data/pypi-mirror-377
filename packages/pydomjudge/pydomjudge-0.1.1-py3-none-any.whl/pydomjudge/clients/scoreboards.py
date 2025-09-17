from typing import Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.response import Scoreboard


class ScoreboardsClient(_Client):
    """
    Client for retrieving scoreboard information for contests.
    """
    def get_scoreboard(self, contest_id: Union[str, int], allteams: bool = None, category: Union[str, int] = None,
                       country: str = None, affiliation: Union[str, int] = None, public: bool = None,
                       sortorder: int = None) -> Scoreboard:
        """
        Retrieve the scoreboard for a specific contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest.
            allteams (bool, optional): If True, include all teams in the scoreboard.
            category (Union[str, int], optional): Filter teams by category ID or name.
            country (str, optional): Filter teams by country code.
            affiliation (Union[str, int], optional): Filter teams by affiliation ID or name.
            public (bool, optional): If True, retrieve the public scoreboard.
            sortorder (int, optional): Specify the sort order for the scoreboard.

        Returns:
            Scoreboard: The validated scoreboard object for the contest.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/scoreboard"
        params = {
            "allteams": allteams,
            "category": category,
            "country": country,
            "affiliation": affiliation,
            "public": public,
            "sortorder": sortorder
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Scoreboard.model_validate(response.json())