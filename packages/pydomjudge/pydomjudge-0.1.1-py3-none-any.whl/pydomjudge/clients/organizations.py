from typing import List, Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import TeamAffiliation


class OrganizationsClient(_Client):
    """
    Client for retrieving and managing organization (team affiliation) information for contests.
    """
    def get_all_organizations(self, contest_id: Union[str, int], idlist: List[str] = None, country: str = None,
                              strict: bool = False) -> List[TeamAffiliation]:
        """
        Retrieve all organizations (team affiliations) for a given contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            idlist (List[str], optional): List of organization IDs to filter. Defaults to None.
            country (str, optional): Country code to filter organizations. Defaults to None.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            List[TeamAffiliation]: List of organization details.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations"
        params = {
            "ids[]": idlist,
            "country": country,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [TeamAffiliation.model_validate(org) for org in response.json()]

    def add_organization(self, contest_id: Union[str, int], organization_data: dict,
                         strict: bool = False) -> TeamAffiliation:
        """
        Add a new organization (team affiliation) to a contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            organization_data (dict): The organization data to add.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            TeamAffiliation: The added organization details.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=organization_data)
        response.raise_for_status()
        return TeamAffiliation.model_validate(response.json())

    def get_organization(self, contest_id: Union[str, int], organization_id: str,
                         strict: bool = False) -> TeamAffiliation:
        """
        Retrieve details of a specific organization (team affiliation) for a given contest.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            organization_id (str): The organization identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            TeamAffiliation: The organization details.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return TeamAffiliation.model_validate(response.json())

    def get_organization_logo(self, contest_id: Union[str, int], organization_id: str,
                               strict: bool = False) -> bytes:
        """
        Get the logo of an organization.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            organization_id (str): The organization identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            bytes: The logo image data.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}/logo"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def set_organization_logo(self, contest_id: Union[str, int], organization_id: str, logo: bytes,
                              strict: bool = False) -> None:
        """
        Set the logo of an organization.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            organization_id (str): The organization identifier.
            logo (bytes): The logo image data.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}/logo"
        params = {
            "strict": strict
        }
        files = {
            "logo": logo
        }
        response = self.session.put(url, params=params, files=files)
        response.raise_for_status()

    def delete_organization_logo(self, contest_id: Union[str, int], organization_id: str,
                                 strict: bool = False) -> None:
        """
        Delete the logo of an organization.

        Args:
            contest_id (Union[str, int]): The contest identifier.
            organization_id (str): The organization identifier.
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.
        """
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}/logo"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()