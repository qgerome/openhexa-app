import typing
from urllib.parse import urljoin

import requests
from django.utils import timezone


class AirflowAPIError(Exception):
    pass


class AirflowAPIClient:
    def __init__(self, *, url: str, username: str, password: str):
        self._url = url
        self._session = requests.Session()
        self._session.auth = (username, password)

    def list_dags(self) -> typing.Dict:
        url = urljoin(self._url, "dags")
        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.json()

    def trigger_dag_run(self, dag_id: str) -> typing.Dict:
        url = urljoin(self._url, f"dags/{dag_id}/dagRuns")
        response = self._session.post(
            url,
            json={"execution_date": timezone.now().isoformat()},
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise AirflowAPIError(f"POST {url}: got {response.status_code}")

        return response.json()

    def list_dag_runs(self, dag_id: str) -> typing.Dict:
        url = urljoin(self._url, f"dags/{dag_id}/dagRuns?order_by=-end_date")
        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.json()

    def get_dag_run(self, dag_id: str, run_id: str) -> typing.Dict:
        url = urljoin(
            self._url,
            f"dags/{dag_id}/dagRuns/{run_id}",
        )

        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.json()
