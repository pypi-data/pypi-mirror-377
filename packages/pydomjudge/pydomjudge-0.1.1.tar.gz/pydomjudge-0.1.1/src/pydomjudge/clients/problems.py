from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import ContestProblem


class ProblemsClient(_Client):
    """
    Client for retrieving and managing problem information for contests.
    """
    def get_all_problems(self, contest_id: Union[str, int], idlist: List[str] = None, strict: bool = False) -> List[ContestProblem]:
        """
        Retrieve all problems from a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            idlist (List[str], optional): List of problem IDs to filter. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[ContestProblem]: List of retrieved problem objects.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems"
        params = {
            "ids[]": idlist,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [ContestProblem.model_validate(problem) for problem in response.json()]

    def get_problem(self, contest_id: Union[str, int], problem_id: str, strict: bool = False) -> ContestProblem:
        """
        Retrieve a specific problem from a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            problem_id (str): The problem identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            ContestProblem: The retrieved problem object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return ContestProblem.model_validate(response.json())

    def add_problem(self, contest_id: Union[str, int], problem_data: dict, strict: bool = False) -> str:
        """
        Add a single problem to a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            problem_data (dict): The problem data to upload.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The added problem ID.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=problem_data)
        response.raise_for_status()
        return response.json()

    def link_problem(self, contest_id: Union[str, int], problem_id: str, problem_data: dict, strict: bool = False) -> ContestProblem:
        """
        Link a problem to a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            problem_id (str): The problem identifier.
            problem_data (dict): The data to link the problem.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            ContestProblem: The linked problem object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=problem_data)
        response.raise_for_status()
        return ContestProblem.model_validate(response.json())

    def unlink_problem(self, contest_id: Union[str, int], problem_id: str, strict: bool = False) -> None:
        """
        Unlink a problem from a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            problem_id (str): The problem identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            None
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()

    def get_problem_statement(self, contest_id: Union[str, int], problem_id: str, strict: bool = False) -> bytes:
        """
        Retrieve the statement for a specific problem in a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            problem_id (str): The problem identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The problem statement content.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}/statement"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def add_problems(self, contest_id: Union[str, int], problems_data: dict, strict: bool = False) -> List[str]:
        """
        Add multiple problems to a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            problems_data (dict): The problems data to upload.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[str]: List of added problem IDs.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/add-data"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=problems_data)
        response.raise_for_status()
        return response.json()