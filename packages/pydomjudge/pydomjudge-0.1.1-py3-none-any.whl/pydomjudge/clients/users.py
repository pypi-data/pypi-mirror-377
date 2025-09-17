from typing import List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import User


class UsersClient(_Client):
    """
    Client for retrieving and managing user information from the API.
    """
    def get_all_users(self, idlist: List[str] = None, team_id: str = None) -> List[User]:
        """
        Retrieve a list of users from the API.

        Args:
            idlist (List[str], optional): A list of user IDs to filter the results. Defaults to None.
            team_id (str, optional): The team ID to filter users by team. Defaults to None.

        Returns:
            List[User]: A list of User objects retrieved from the API.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/users"
        params = {
            "ids[]": idlist,
            "team_id": team_id
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [User.model_validate(user) for user in response.json()]

    def get_user(self, user_id: str) -> User:
        url = f"{self.base_url}/api/v4/users/{user_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return User.model_validate(response.json())

    def add_user(self, user_data: dict) -> User:
        """
        Adds a new user to the system using the provided user data.

        Args:
            user_data (dict): A dictionary containing the user's information to be added.

        Returns:
            User: An instance of the User model representing the newly created user.

        Raises:
            requests.HTTPError: If the request to add the user fails.
        """
        url = f"{self.base_url}/api/v4/users"
        response = self.session.post(url, json=user_data)
        response.raise_for_status()
        return User.model_validate(response.json())

    def update_user(self, user_id: str, user_data: dict) -> User:
        """
        Updates the details of a user with the specified user ID.

        Args:
            user_id (str): The unique identifier of the user to update.
            user_data (dict): A dictionary containing the user fields to update.

        Returns:
            User: An instance of the User model representing the updated user.

        Raises:
            requests.HTTPError: If the HTTP request to update the user fails.
        """
        url = f"{self.base_url}/api/v4/users/{user_id}"
        response = self.session.put(url, json=user_data)
        response.raise_for_status()
        return User.model_validate(response.json())

    def delete_user(self, user_id: str) -> None:
        """
        Deletes a user with the specified user ID from the system.

        Args:
            user_id (str): The unique identifier of the user to be deleted.

        Raises:
            requests.HTTPError: If the HTTP request to delete the user fails.
        """
        url = f"{self.base_url}/api/v4/users/{user_id}"
        response = self.session.delete(url)
        response.raise_for_status()

    def add_groups(self, groups_data: dict) -> dict:
        """
        Adds user groups by sending a POST request to the API.

        Args:
            groups_data (dict): A dictionary containing group data to be added.

        Returns:
            dict: The JSON response from the API after adding the groups.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/users/groups"
        response = self.session.post(url, files=groups_data)
        response.raise_for_status()
        return response.json()

    def add_organizations(self, organizations_data: dict) -> dict:
        """
        Adds organizations to a user via the API.

        Args:
            organizations_data (dict): A dictionary containing organization data to be added.

        Returns:
            dict: The JSON response from the API after adding the organizations.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/users/organizations"
        response = self.session.post(url, files=organizations_data)
        response.raise_for_status()
        return response.json()

    def add_teams(self, teams_data: dict) -> dict:
        """
        Adds multiple teams to the system via the API.

        Args:
            teams_data (dict): A dictionary containing team data to be uploaded. 
                The structure should match the expected format for the API endpoint.

        Returns:
            dict: The JSON response from the API after adding the teams.

        Raises:
            requests.HTTPError: If the API request fails or returns an error status code.
        """
        url = f"{self.base_url}/api/v4/users/teams"
        response = self.session.post(url, files=teams_data)
        response.raise_for_status()
        return response.json()

    def add_accounts(self, accounts_data: dict) -> dict:
        """
        Adds multiple user accounts by sending account data to the API.

        Args:
            accounts_data (dict): A dictionary containing account information to be uploaded.

        Returns:
            dict: The JSON response from the API after creating the accounts.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/users/accounts"
        response = self.session.post(url, files=accounts_data)
        response.raise_for_status()
        return response.json()