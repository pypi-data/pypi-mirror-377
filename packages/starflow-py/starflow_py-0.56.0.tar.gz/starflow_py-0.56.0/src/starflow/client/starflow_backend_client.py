from typing import Any
from starflow.logger import get_configured_logger
from datetime import datetime
import requests
from urllib.parse import urljoin
import os
from keycloak import KeycloakOpenID


class starflowBackendRestClient(requests.Session):
    def __init__(self, base_url: str = None, *args, **kwargs):
        super(starflowBackendRestClient, self).__init__(*args, **kwargs)
        self.logger = get_configured_logger(self.__class__.__name__)
        self.keycloak_openid = KeycloakOpenID(server_url=os.environ["OPEN_ID_SERVER_URL"],
                            client_id=os.environ["OPEN_ID_CLIENT_ID"],
                            realm_name=os.environ["OPEN_ID_REALM_NAME"],
                            client_secret_key=os.environ["OPEN_ID_CLIENT_SECRET"],
                            verify=False)
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.environ.get("STARFLOW_BACKEND_HOST", "http://localhost:8000")

    def openid_get_token(self) -> Any:
        token = self.keycloak_openid.token(username=os.environ["OPEN_ID_USERNAME_SERVICE_USER"], password=os.environ["OPEN_ID_PASSWORD_SERVICE_USER"])
        return token

    def request(self, method, resource, **kwargs) -> requests.Response:
        try:
            bearer_token = self.openid_get_token()
            headers = {"Authorization": "Bearer " + bearer_token['access_token']}
            url = urljoin(self.base_url, resource)
            return super(starflowBackendRestClient, self).request(method, url, verify=False, headers=headers, **kwargs)
        except Exception as e:
            self.logger.exception(e)
            raise e

    def health_check(self) -> requests.Response:
        resource = "/health-check"
        response = self.request(
            method="get",
            resource=resource
        )
        return response

    def get_piece_secrets(self, piece_repository_id: int, piece_name: str) -> requests.Response:
        resource = f"/pieces-repositories/{piece_repository_id}/secrets/{piece_name}/secrets-values"
        response = self.request(
            method='get',
            resource=resource
        )
        return response

    def get_piece_repositories_from_workspace_id(self, params: dict) -> requests.Response:
        resource = "/pieces-repositories/worker"
        response = self.request(
            method='get',
            resource=resource,
            params=params
        )
        return response

    def check_create_airflow_connection(self, conn_id: str, conn_type: str):
        """
        This should check if a specific Airflow connection exists and create it if it doesn't.
        ref: https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_connection
        """
        # TODO - this is WIP
        resource = f"/airflow/connections/{conn_id}"
        response = self.request(
            method='get',
            resource=resource,
        )
        if response.status_code == 404:
            response = self.request(
                method='post',
                resource=resource,
                json={
                    "conn_id": conn_id,
                    "conn_type": conn_type,
                    "login": "",  # TODO: add login and password
                    "password": "",
                    "extra": {
                        # Specify extra parameters here, e.g. "region_name": "eu-central-1"
                    },
                }
            )
            if response.status_code != 200:
                raise Exception(f"Failed to create Airflow connection {conn_id}. \n {response.json()}")
