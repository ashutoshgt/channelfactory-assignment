import json

from geo.models import GeocodeCache
import pytest
import requests_mock
from django.urls import reverse
from rest_framework.exceptions import ErrorDetail

DISTANCE_URL = reverse("distance")


class TestDistanceAPI:

    def test_empty_body(self, api_client):
        """
        Scenario:
            - A request is made to the distance API with an empty body.
        Expectation:
            - The API returns a 400 Bad Request response.
        """
        response = api_client.post(
            DISTANCE_URL, data={}, content_type="application/json"
        )
        assert response.data == {
            "from_address": [
                ErrorDetail(string="This field is required.", code="required")
            ],
            "destination_address": [
                ErrorDetail(string="This field is required.", code="required")
            ],
        }
        assert response.status_code == 400

    def test_invalid_from_address(self, api_client):
        """
        Scenario:
            - A request is made to the distance API with an invalid from_address.
        Expectation:
            - The API returns a 400 Bad Request response.
        """
        response = api_client.post(
            DISTANCE_URL,
            data=json.dumps(
                {"from_address": "invalid&%", "destination_address": "123 Main St"}
            ),
            content_type="application/json",
        )
        assert response.data == {
            "from_address": [
                ErrorDetail(string="Invalid from address: invalid&%", code="invalid")
            ],
        }
        assert response.status_code == 400

    def test_invalid_destination_address(self, api_client):
        """
        Scenario:
            - A request is made to the distance API with an invalid destination_address.
        Expectation:
            - The API returns a 400 Bad Request response.
        """
        response = api_client.post(
            DISTANCE_URL,
            data=json.dumps(
                {"from_address": "123 Main St", "destination_address": "invalid&%"}
            ),
            content_type="application/json",
        )
        assert response.data == {
            "destination_address": [
                ErrorDetail(
                    string="Invalid destination address: invalid&%", code="invalid"
                )
            ],
        }
        assert response.status_code == 400

    @pytest.mark.django_db(transaction=True)
    def test_invalid_geocode(self, api_client, invalid_geocode_response):
        """
        Scenario:
            - A request is made to the distance API with a valid from_address and destination_address.
            - The geocode API call fails.
        Expectation:
            - The API returns a 400 Bad Request response.
        """
        response = api_client.post(
            DISTANCE_URL,
            data=json.dumps(
                {"from_address": "none", "destination_address": "456 Elm St"}
            ),
            content_type="application/json",
        )
        assert response.data == [
            ErrorDetail(string="Could not geocode address: none", code="invalid")
        ]
        assert response.status_code == 400

    @pytest.mark.django_db(transaction=True)
    @requests_mock.Mocker(kw="request_mocker")
    def test_distance_api_success(self, api_client, **kwargs):
        """
        Scenario:
            - A request is made to the distance API with valid from_address and destination_address.
        Expectation:
            - The API returns a 200 OK response with the distance between the addresses.
            - The geocoded addresses are cached in the database.
            - The API makes a single call to the geocode API.
        """
        from_address = "123 Main St"
        from_lat, from_long = 37.7749295, -122.4194155
        destination_address = "456 Elm St"
        destination_lat, destination_long = 37.7849295, -122.4594155
        
        # Setup
        # Adding from_address in cache
        GeocodeCache.objects.all().delete()
        GeocodeCache.objects.create(
            input_address=from_address,
            formatted_address=from_address,
            latitude=37.7749295,
            longitude=-122.4194155,
        )

        # Setting up mock request to google
        request_mocker = kwargs.get("request_mocker")
        request_mocker.get(
            "https://maps.googleapis.com/maps/api/geocode/json?address=456+Elm+St",
            json={
                "results": [
                    {
                        "formatted_address": destination_address,
                        "geometry": {
                            "location": {"lat": destination_lat, "lng": destination_long}
                        },
                    }
                ],
                "status": "OK",
            },
        )

        # Make the request
        response = api_client.post(
            DISTANCE_URL,
            data=json.dumps(
                {
                    "from_address": from_address,
                    "destination_address": destination_address,
                }
            ),
            content_type="application/json",
        )

        # Assertions

        assert response.status_code == 200

        assert response.data == {
            "from_address": {
                "original": from_address,
                "formatted": from_address,
                "lat": from_lat,
                "long": from_long,
            },
            "destination_address": {
                "original": destination_address,
                "formatted": destination_address,
                "lat": destination_lat,
                "long": destination_long,
            },
            "distance": 3.6870713647672746,
        }

        # Check API calls
        request_mocker.call_count == 1
        
        # Check cache rows
        GeocodeCache.objects.count() == 2
        GeocodeCache.objects.filter(input_address=from_address).exists()
        GeocodeCache.objects.filter(input_address=destination_address).exists()
