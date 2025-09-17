from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import JudgingRun


class RunsClient(_Client):
    """
    Client for retrieving and managing run (submission) information for contests.
    """
    def get_all_runs(self, contest_id: Union[str, int], idlist: List[str] = None, first_id: str = None, last_id: str = None, judging_id: str = None, limit: int = None, strict: bool = False) -> List[JudgingRun]:
        """
        Retrieve all runs for a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            idlist (List[str], optional): List of run IDs to filter.
            first_id (str, optional): First run ID for pagination.
            last_id (str, optional): Last run ID for pagination.
            judging_id (str, optional): Judging ID to filter runs.
            limit (int, optional): Maximum number of runs to return.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[JudgingRun]: List of JudgingRun objects.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/runs"
        params = {
            "ids[]": idlist,
            "first_id": first_id,
            "last_id": last_id,
            "judging_id": judging_id,
            "limit": limit,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [JudgingRun.model_validate(run) for run in response.json()]

    def get_run(self, contest_id: Union[str, int], run_id: str, strict: bool = False) -> JudgingRun:
        """
        Retrieve a specific run for a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            run_id (str): The run identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            JudgingRun: The requested JudgingRun object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/runs/{run_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return JudgingRun.model_validate(response.json())