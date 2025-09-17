from typing import Dict, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import User


class GeneralClient(_Client):
    """
    Client for retrieving general information from the API.
    """
    def get_api_version(self, strict: bool = False) -> Dict:
        """
        Retrieves the API version information from the server.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: A dictionary containing the API version details.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/version"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_api_info(self, strict: bool = False) -> Dict:
        """
        Retrieves API information from the server.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: The JSON response containing API information.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/info"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_api_root(self, strict: bool = False) -> Dict:
        """
        Retrieves the API root information from the server.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: The JSON response from the API root endpoint.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_general_status(self, strict: bool = False) -> List[Dict]:
        """
        Retrieves the general status from the API.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Dict]: A list of dictionaries containing the general status information from the API.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/status"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_user_info(self, strict: bool = False) -> User:
        """
        Retrieves information about the current user from the API.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            User: An instance of the User model populated with the user's information from the API.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            pydantic.ValidationError: If the response data cannot be validated against the User model.
        """
        url = f"{self.base_url}/api/v4/user"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return User.model_validate(response.json())

    def get_config(self, name: str = None, strict: bool = False) -> Dict:
        """
        Retrieve configuration settings from the API.

        Args:
            name (str, optional): The name of the configuration setting to retrieve. If None, retrieves all settings.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: The configuration data returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/config"
        params = {
            "name": name,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def update_config(self, config_data: Dict, strict: bool = False) -> Dict:
        """
        Updates the configuration on the server with the provided data.

        Args:
            config_data (Dict): A dictionary containing the configuration data to be updated.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: The server's response as a dictionary after updating the configuration.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/config"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=config_data)
        response.raise_for_status()
        return response.json()

    def check_config(self, strict: bool = False) -> Dict:
        """
        Checks the configuration of the server via the API.
        
        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Dict: The JSON response from the server containing the configuration check results.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/config/check"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_country_flag(self, country_code: str, size: str, strict: bool = False) -> bytes:
        """
        Retrieves the flag image for a specified country.

        Args:
            country_code (str): The ISO country code for which to retrieve the flag.
            size (str): The desired size of the flag image (e.g., 'small', 'medium', 'large').
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The binary content of the flag image.

        Raises:
            requests.HTTPError: If the HTTP request fails or returns an error status code.
        """
        url = f"{self.base_url}/api/v4/country-flags/{country_code}/{size}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content