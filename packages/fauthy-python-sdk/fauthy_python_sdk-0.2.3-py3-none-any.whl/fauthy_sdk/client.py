"""
Fauthy SDK Client

This module provides a client for interacting with the Fauthy API.
"""

from typing import Any, Dict, Optional

import requests

from fauthy_sdk.management import ManagementMixin


class FauthyClient(ManagementMixin):
    """Client for interacting with the Fauthy API."""

    BASE_URL = "https://api.fauthy.com/v1/management"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the Fauthy client.

        Args:
            client_id (str): Your Fauthy client ID
            client_secret (str): Your Fauthy client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Client-ID": self.client_id,
                "X-Client-Secret": self.client_secret,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make an HTTP request to the Fauthy API.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint to call
            data (Optional[Dict[str, Any]]): Request body data
            params (Optional[Dict[str, Any]]): URL parameters

        Returns:
            requests.Response: The API response

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method, url=url, json=data, params=params
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # You might want to add custom error handling here
            raise e

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Make a GET request to the Fauthy API."""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Make a POST request to the Fauthy API."""
        return self._make_request("POST", endpoint, data=data)

    def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Make a PUT request to the Fauthy API."""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> requests.Response:
        """Make a DELETE request to the Fauthy API."""
        return self._make_request("DELETE", endpoint)
