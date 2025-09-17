from pydomjudge.clients.client import _Client


class MetricsClient(_Client):
    """
    Client for retrieving Prometheus metrics from the API.
    """
    def get_metrics(self, strict: bool = False) -> str:
        """
        Retrieve Prometheus metrics.

        Args:
            strict (bool, optional): Whether to only include CCS compliant properties in the response. Defaults to False.

        Returns:
            str: The metrics in Prometheus format.
        """
        url = f"{self.base_url}/api/v4/metrics/prometheus"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.text
