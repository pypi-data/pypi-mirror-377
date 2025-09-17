import requests

from requests import Session
from newsdata_client.newsdata_auth import NewsDataAuth
from newsdata_client.newsdata_exception import NewsDataException
from newsdata_client.newsdata_client_helper import (
    add_latest_params,
    add_crypto_params,
    add_archive_params,
    add_sources_params,
)


class NewsDataClient:
    def __init__(self, api_key: str, session: Session = None):
        self.base_api_url = "https://newsdata.io/api/1/"
        self.latest_endpoint = f"{self.base_api_url}latest"
        self.crypto_endpoint = f"{self.base_api_url}crypto"
        self.archive_endpoint = f"{self.base_api_url}archive"
        self.sources_endpoint = f"{self.base_api_url}sources"

        self.auth = NewsDataAuth(api_key)
        if session is None:
            self.request_method = requests
        else:
            self.request_method = session

    def latest(self, **kwargs):
        payload = dict()
        add_latest_params(payload, **kwargs)

        response = self.request_method.get(
            self.latest_endpoint, auth=self.auth, params=payload
        )

        if response.status_code != requests.codes.ok:
            if response.headers.get("content-type") == "application/json":
                raise NewsDataException(response.json())
            else:
                raise NewsDataException(str(response.content))

        return response.json()

    def crypto(self, **kwargs):
        payload = dict()
        add_crypto_params(payload, **kwargs)

        response = self.request_method.get(
            self.crypto_endpoint, auth=self.auth, params=payload
        )

        if response.status_code != requests.codes.ok:
            if response.headers.get("content-type") == "application/json":
                raise NewsDataException(response.json())
            else:
                raise NewsDataException(str(response.content))

        return response.json()

    def archive(self, **kwargs):
        payload = dict()
        add_archive_params(payload, **kwargs)

        response = self.request_method.get(
            self.archive_endpoint, auth=self.auth, params=payload
        )

        if response.status_code != requests.codes.ok:
            if response.headers.get("content-type") == "application/json":
                raise NewsDataException(response.json())
            else:
                raise NewsDataException(str(response.content))

        return response.json()

    def sources(self, **kwargs):
        payload = dict()
        add_sources_params(payload, **kwargs)

        response = self.request_method.get(self.sources_endpoint, auth=self.auth)

        if response.status_code != requests.codes.ok:
            if response.headers.get("content-type") == "application/json":
                raise NewsDataException(response.json())
            else:
                raise NewsDataException(str(response.content))

        return response.json()
