from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Submission
from pydomjudge.models.shared import ArchiveFile, SourceCode


class SubmissionsClient(_Client):
    """
    Client for retrieving and managing submission information for contests.
    """
    def get_submissions(self, contest_id: Union[str, int], idlist: List[Union[str, int]] = None, language_id: str = None,
                        strict: bool = False) -> List[Submission]:
        """
        Retrieve a list of submissions for a contest.

        Args:
            contest_id (Union[str, int]): The contest ID.
            idlist (List[Union[str, int]], optional): List of submission IDs to filter. Defaults to None.
            language_id (str, optional): Filter submissions by language ID. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Submission]: A list of Submission objects.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions"
        params = {
            "ids[]": idlist,
            "language_id": language_id,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Submission.model_validate(submission) for submission in response.json()]

    def get_submission(self, contest_id: Union[str, int], submission_id: Union[str, int], strict: bool = False) -> Submission:
        """
        Retrieve a specific submission.

        Args:
            contest_id (Union[str, int]): The contest ID.
            submission_id (Union[str, int]): The submission ID.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Submission: The requested Submission object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Submission.model_validate(response.json())

    def get_submission_files(self, contest_id: Union[str, int], submission_id: Union[str, int], strict: bool = False) -> List[ArchiveFile]:
        """
        Retrieve the archive files for a specific submission.

        Args:
            contest_id (Union[str, int]): The contest ID.
            submission_id (Union[str, int]): The submission ID.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[ArchiveFile]: A list of ArchiveFile objects for the submission.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}/files"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [ArchiveFile.model_validate(file) for file in response.json()]

    def get_submission_source_code(self, contest_id: Union[str, int], submission_id: Union[str, int], strict: bool = False) -> List[SourceCode]:
        """
        Retrieve the source code files for a specific submission.

        Args:
            contest_id (Union[str, int]): The contest ID.
            submission_id (Union[str, int]): The submission ID.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[SourceCode]: A list of SourceCode objects for the submission.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}/source-code"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [SourceCode.model_validate(source_code) for source_code in response.json()]

    def add_submission(self, contest_id: Union[str, int], submission_data: dict, strict: bool = False) -> str:
        """
        Add a new submission.

        Args:
            contest_id (Union[str, int]): The contest ID.
            submission_data (dict): The submission data to send (should include files and metadata).
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The created submission response.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=submission_data)
        response.raise_for_status()
        return response.json()

    def update_submission(self, contest_id: Union[str, int], submission_id: str, submission_data: dict, strict: bool = False) -> str:
        """
        Update a submission.

        Args:
            contest_id (Union[str, int]): The contest ID.
            submission_id (str): The submission ID.
            submission_data (dict): The data to update the submission with.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The updated submission response.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=submission_data)
        response.raise_for_status()
        return response.json()