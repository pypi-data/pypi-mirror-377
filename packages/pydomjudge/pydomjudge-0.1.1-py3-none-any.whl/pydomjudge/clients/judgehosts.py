from typing import List, Dict

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Judgehost, Judging


class JudgehostsClient(_Client):
    """
    Client for retrieving and managing judgehost information from the API.
    """
    def get_judgehosts(self, hostname: str = None, strict: bool = False) -> List[Judgehost]:
        """
        Retrieve a list of judgehosts from the API.

        Args:
            hostname (str, optional): Filter judgehosts by hostname. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Judgehost]: A list of Judgehost objects retrieved from the API.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/judgehosts"
        params = {
            "hostname": hostname,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Judgehost.model_validate(judgehost) for judgehost in response.json()]

    def add_judgehost(self, strict: bool = False) -> List[Judging]:
        """
        Adds a new judgehost to the system.

        Sends a POST request to the judgehosts API endpoint to add a judgehost.
        
        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Judging]: A list of Judging objects returned by the API after adding the judgehost.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/judgehosts"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()

    def update_judgehost(self, hostname: str, judgehost_data: dict, strict: bool = False) -> List[Judgehost]:
        """
        Updates the information of a specific judgehost.

        Args:
            hostname (str): The hostname of the judgehost to update.
            judgehost_data (dict): A dictionary containing the updated judgehost data.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Judgehost]: A list of Judgehost objects representing the updated judgehost(s).

        Raises:
            requests.HTTPError: If the HTTP request to update the judgehost fails.
        """
        url = f"{self.base_url}/api/v4/judgehosts/{hostname}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=judgehost_data)
        response.raise_for_status()
        return [Judgehost.model_validate(judgehost) for judgehost in response.json()]

    def update_judging(self, hostname: str, judgetask_id: int, judging_data: dict, strict: bool = False) -> None:
        """
        Updates the judging data for a specific judgehost and judgetask.

        Args:
            hostname (str): The hostname of the judgehost.
            judgetask_id (int): The ID of the judgetask to update.
            judging_data (dict): The data to update for the judging task.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        url = f"{self.base_url}/api/v4/judgehosts/update-judging/{hostname}/{judgetask_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=judging_data)
        response.raise_for_status()

    def add_debug_info(self, hostname: str, judgetask_id: int, debug_info: dict, strict: bool = False) -> None:
        """
        Adds debug information to a specific judgehost and judgetask.

        Args:
            hostname (str): The hostname of the judgehost.
            judgetask_id (int): The ID of the judgetask to associate the debug info with.
            debug_info (dict): A dictionary containing the debug information to be added.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/judgehosts/add-debug-info/{hostname}/{judgetask_id}"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=debug_info)
        response.raise_for_status()

    def add_judging_run(self, hostname: str, judgetask_id: int, judging_run_data: dict,
                        strict: bool = False) -> None:
        """
        Adds a judging run to a specified judgehost for a given judgetask.

        Sends a POST request to the judgehost API to register a new judging run.

        Args:
            hostname (str): The hostname of the judgehost to add the judging run to.
            judgetask_id (int): The ID of the judgetask associated with the judging run.
            judging_run_data (dict): The data describing the judging run to be added.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Raises:
            requests.HTTPError: If the API request fails or returns an error status code.
        """
        url = f"{self.base_url}/api/v4/judgehosts/add-judging-run/{hostname}/{judgetask_id}"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=judging_run_data)
        response.raise_for_status()

    def report_internal_error(self, error_data: dict, strict: bool = False) -> int:
        """
        Reports an internal error to the judgehosts API.

        Args:
            error_data (dict): A dictionary containing error details to be reported.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            int: The response from the API after reporting the error.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/judgehosts/internal-error"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=error_data)
        response.raise_for_status()
        return response.json()

    def get_files(self, file_type: str, file_id: str, strict: bool = False) -> bytes:
        """
        Retrieve files of a specified type and ID from the judgehost API.

        Args:
            file_type (str): The type of file to retrieve (e.g., 'executable', 'source').
            file_id (str): The unique identifier of the file.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The content of the requested file.

        Raises:
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/judgehosts/get_files/{file_type}/{file_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def fetch_work_tasks(self, strict: bool = False) -> List[Dict]:
        """
        Fetches work tasks for judgehosts from the API.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Dict]: A list of dictionaries representing the fetched work tasks.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/judgehosts/fetch-work"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()