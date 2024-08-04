import pytest
from requests_mock import Mocker
from rest_framework.test import APIClient


@pytest.fixture
def invalid_geocode_response():
    with Mocker() as mock:
        # Mock the response for a successful geocode API call
        mock.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"results": [], "status": "ZERO_RESULTS"},
        )

        yield mock

@pytest.fixture
def valid_geocode_response():
    with Mocker() as mock:
        # Mock the response for a successful geocode API call
        mock.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={
                "results": [
                    {
                        "formatted_address": "Formatted Address",
                        "geometry": {
                            "location": {
                                "lat": 37.7749295,
                                "lng": -122.4194155
                            }
                        }
                    }
                ],
                "status": "OK"
            },
        )

        yield mock

@pytest.fixture
def api_client():
    return APIClient()
