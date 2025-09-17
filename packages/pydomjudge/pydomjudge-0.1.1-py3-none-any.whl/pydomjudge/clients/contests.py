from typing import List, Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Contest, Event, ContestState, ContestStatus


class ContestsClient(_Client):
    """
    Client for retrieving contest information.
    """
    def get_all_contests(self, idlist: List[str] = None, only_active: bool = False, strict: bool = False) -> List[Contest]:
        """
        Retrieve a list of contests from the API.

        Args:
            idlist (List[str], optional): A list of contest IDs to filter the results. Defaults to None.
            only_active (bool, optional): If True, only return active contests. Defaults to False.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Contest]: A list of Contest objects retrieved from the API.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/v4/contests"
        params = {
            "ids[]": idlist,
            "onlyActive": only_active,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Contest.model_validate(contest) for contest in response.json()]

    def get_contest(self, contest_id: Union[str, int], strict: bool = False) -> Contest:
        """
        Retrieve contest information by contest ID.

        Args:
            contest_id (Union[str, int]): The unique identifier of the contest to retrieve.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Contest: An instance of the Contest model populated with the contest data.

        Raises:
            requests.HTTPError: If the HTTP request to the contest API fails.
            ValidationError: If the response data cannot be validated against the Contest model.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Contest.model_validate(response.json())

    def add_contest(self, contest_data: dict, strict: bool = False) -> str:
        """
        Adds a new contest to the system using the provided contest data.

        Args:
            contest_data (dict): A dictionary containing the contest information to be added.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The response from the server after adding the contest.

        Raises:
            requests.HTTPError: If the request to add the contest fails.
        """
        url = f"{self.base_url}/api/v4/contests"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=contest_data)
        response.raise_for_status()
        return response.json()

    def change_contest_start_time(self, contest_id: Union[str, int], start_time: str, force: bool = False, strict: bool = False) -> str:
        """
        Change the start time of a contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to update.
            start_time (str): The new start time for the contest in ISO 8601 format.
            force (bool, optional): Whether to force the change even if there are conflicts. Defaults to False.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The response from the server as a JSON string.

        Raises:
            requests.HTTPError: If the request to the server fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/starttime"
        params = {
            "strict": strict
        }
        data = {
            "start_time": start_time,
            "force": force
        }
        response = self.session.patch(url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def get_contest_banner(self, contest_id: Union[str, int], strict: bool = False) -> bytes:
        """
        Retrieve the banner image for a specific contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve the banner for.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The content of the contest banner image.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/banner"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def set_contest_banner(self, contest_id: Union[str, int], banner: bytes, strict: bool = False) -> None:
        """
        Uploads and sets a banner image for a specific contest.

        Args:
            contest_id (Union[str, int]): The unique identifier of the contest.
            banner (bytes): The banner image data to upload.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Raises:
            requests.HTTPError: If the HTTP request fails or the server returns an error response.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/banner"
        params = {
            "strict": strict
        }
        files = {
            "banner": banner
        }
        response = self.session.put(url, params=params, files=files)
        response.raise_for_status()

    def delete_contest_banner(self, contest_id: Union[str, int], strict: bool = False) -> None:
        """
        Deletes the banner associated with a specific contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest whose banner is to be deleted.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Raises:
            requests.HTTPError: If the HTTP request to delete the banner fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/banner"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()

    def get_contest_yaml(self, contest_id: Union[str, int], strict: bool = False) -> str:
        """
        Retrieve the contest YAML configuration for a specified contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve the YAML for.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The contest YAML configuration as a string.

        Raises:
            requests.HTTPError: If the HTTP request to the server fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/contest-yaml"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.text

    def get_contest_state(self, contest_id: Union[str, int], strict: bool = False) -> ContestState:
        """
        Retrieve the state of a specific contest.

        Args:
            contest_id (Union[str, int]): The unique identifier of the contest.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            ContestState: An instance representing the current state of the contest.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            pydantic.ValidationError: If the response data cannot be validated as a ContestState.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/state"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return ContestState.model_validate(response.json())

    def get_event_feed(self, contest_id: Union[str, int], since_id: str = None, types: List[str] = None,
                       stream: bool = True, strict: bool = False) -> List[Event]:
        """
        Retrieves the event feed for a specific contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve events for.
            since_id (str, optional): If provided, only events after this ID will be returned.
            types (List[str], optional): A list of event types to filter the feed.
            stream (bool, optional): If True, enables streaming of events. Defaults to True.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Event]: A list of validated Event objects from the contest's event feed.

        Raises:
            requests.HTTPError: If the HTTP request to the event feed fails.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/event-feed"
        params = {
            "since_id": since_id,
            "types": types,
            "stream": stream,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Event.model_validate(event) for event in response.json()]

    def get_contest_status(self, contest_id: Union[str, int], strict: bool = False) -> ContestStatus:
        """
        Retrieves the status of a specific contest.

        Args:
            contest_id (Union[str, int]): The unique identifier of the contest.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            ContestStatus: An object representing the contest's status.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            pydantic.ValidationError: If the response data cannot be validated into a ContestStatus object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/status"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return ContestStatus.model_validate(response.json())

    def get_samples_zip(self, contest_id: Union[str, int], strict: bool = False) -> bytes:
        """
        Downloads a ZIP file containing sample data for a specified contest.

        Args:
            contest_id (Union[str, int]): The ID of the contest to retrieve samples for.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The content of the ZIP file containing the samples.

        Raises:
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/samples.zip"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content