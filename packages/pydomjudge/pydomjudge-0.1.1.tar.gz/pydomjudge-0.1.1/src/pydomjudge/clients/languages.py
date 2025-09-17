from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Language


class LanguagesClient(_Client):
    """
    Client for retrieving language information for contests.
    """
    def get_all_languages(self, contest_id: Union[str, int], idlist: List[str] = None, strict: bool = False) -> List[Language]:
        """
        Retrieve all languages for a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            idlist (List[str], optional): List of language identifiers to filter. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[Language]: List of language objects.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/languages"
        params = {
            "ids[]": idlist,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Language.model_validate(language) for language in response.json()]

    def get_language(self, contest_id: Union[str, int], language_id: str, strict: bool = False) -> Language:
        """
        Retrieve a specific language for a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            language_id (str): The language identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            Language: The requested language object.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/languages/{language_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Language.model_validate(response.json())