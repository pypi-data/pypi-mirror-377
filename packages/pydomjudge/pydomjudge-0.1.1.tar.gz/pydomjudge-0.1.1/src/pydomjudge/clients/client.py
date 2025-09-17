import requests
from requests.auth import HTTPBasicAuth


class _Client:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
