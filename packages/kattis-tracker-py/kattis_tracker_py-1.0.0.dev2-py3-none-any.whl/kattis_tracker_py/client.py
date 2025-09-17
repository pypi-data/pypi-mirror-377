# SPDX-FileCopyrightText: 2025-present Christian <chrille_0313@hotmail.com>
#
# SPDX-License-Identifier: MIT

import requests


class KattisTrackerClient:
    class ServerError(Exception):
        pass

    class ClientError(Exception):
        pass

    def __init__(self, api_url: str = "https://api.kattis-tracker.com"):
        self.api_url = api_url

        if not self.check_backend_status():
            raise ConnectionError(f"Failed to connect to backend at: {api_url}!")

    def check_backend_status(self) -> tuple[int, dict]:
        response = self.get("/health")
        return response.get("status") == "success"

    def get_url(self, route: str) -> str:
        return f"{self.api_url}{route}"

    def get(self, route: str, params: dict[str, str | list[str]] = None):
        response = requests.get(self.get_url(route), params=params).json()

        status = response.get("status")
        if status == "fail":
            raise KattisTrackerClient.ClientError(f"Request to {route} failed: {response.get("data")}")
        elif status == "error":
            raise KattisTrackerClient.ServerError(f"Request to {route} failed: {response.get("message")}")

        return response

    def post(self, route: str, data: dict):
        response = requests.post(self.get_url(route), json=data).json()

        status = response.get("status")
        if status == "fail":
            raise KattisTrackerClient.ClientError(f"Request to {route} failed: {response.get("data")}")
        elif status == "error":
            raise KattisTrackerClient.ServerError(f"Request to {route} failed: {response.get("message")}")

        return response
