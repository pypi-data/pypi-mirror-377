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

    # Countries

    def get_countries(self, query: dict[str, str | list[str]] = None) -> tuple[int, dict]:
        response = self.get("/countries", params=query)
        return response.get("data")

    def create_countries(self, countries: list[dict]):
        response = self.post("/countries", {
            "items": countries
        })

        return response.get("data")

    # Subdivisions

    def get_subdivisions(self, country: str, query: dict[str, str | list[str]] = None) -> tuple[int, dict]:
        response = self.get(f"/countries/{country}/subdivisions", params=query)
        return response.get("data")

    def create_subdivisions(self, country: str, subdivisions: list[dict]):
        response = self.post(f"/countries/{country}/subdivisions", {
            "items": subdivisions
        })

        return response.get("data")

    # Affiliations

    def get_affiliations(self, query: dict[str, str | list[str]] = None) -> tuple[int, dict]:
        response = self.get("/affiliations", params=query)
        return response.get("data")

    def create_affiliations(self, affiliations: list[dict]):
        response = self.post("/affiliations", {
            "items": affiliations
        })

        return response.get("data")

    # Users

    def get_users(self, query: dict[str, str | list[str]] = None) -> tuple[int, dict]:
        response = self.get("/users", params=query)
        return response.get("data")

    def create_users(self, users: list[dict]):
        response = self.post("/users", {
            "items": users
        })

        return response.get("data")

    def create_users_global_rank_snapshot(self, snapshot: dict):
        response = self.post("/users/snapshots/rank/global", snapshot)
        return response.get("data")

    def create_users_country_rank_snapshot(self, snapshot: dict):
        response = self.post(f"/users/snapshots/rank/country", snapshot)
        return response.get("data")

    def create_users_subdivision_rank_snapshot(self, snapshot: dict):
        response = self.post("/users/snapshots/rank/subdivision", snapshot)
        return response.get("data")

    def create_users_affiliation_rank_snapshot(self, snapshot: dict):
        response = self.post("/users/snapshots/rank/affiliation", snapshot)
        return response.get("data")
    