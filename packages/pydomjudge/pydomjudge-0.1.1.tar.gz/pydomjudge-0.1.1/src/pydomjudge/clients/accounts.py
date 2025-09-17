from typing import List, Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import User


class AccountsClient(_Client):
    """
    Client for retrieving account information for contests.
    """
    def get_all_accounts(self, contest_id: Union[str, int], idlist: List[str] = None, team_id: str = None,
                         strict: bool = False) -> List[User]:
        """
        Retrieves all accounts for a given contest.

        Sends a GET request to `/api/v4/contests/{contest_id}/accounts` to fetch account information.

        Parameters:
            contest_id (Union[str, int]): The contest ID.
            idlist (List[str], optional): List of account IDs to filter the results.
            team_id (str, optional): Only show accounts for the given team.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[User]: A list of User objects representing the accounts for the contest.

        Raises:
            requests.HTTPError: If the request fails with status codes 400, 401, 403, or 404.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/accounts"
        params = {
            "ids[]": idlist,
            "team_id": team_id,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [User.model_validate(account) for account in response.json()]

    def get_account(self, contest_id: Union[str, int], account_id: str, strict: bool = False) -> User:
        """
        Retrieves the given account for a specific contest.

        Sends a GET request to `/api/v4/contests/{contest_id}/accounts/{account_id}`.

        Parameters:
            contest_id (Union[str, int]): The contest ID.
            account_id (str): The account ID.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            User: The User object representing the account.

        Raises:
            requests.HTTPError: If the request fails with status codes 400, 401, 403, or 404.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/accounts/{account_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return User.model_validate(response.json())

    def get_current_account(self, contest_id: Union[str, int], strict: bool = False) -> User:
        """
        Retrieves information about the currently logged in account for a specific contest.

        Sends a GET request to `/api/v4/contests/{contest_id}/account`.

        Parameters:
            contest_id (Union[str, int]): The contest ID.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            User: The User object representing the currently logged in account.

        Raises:
            requests.HTTPError: If the request fails with status codes 400, 401, 403, or 404.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/account"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return User.model_validate(response.json())