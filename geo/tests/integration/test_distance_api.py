import json
import pytest
from django.urls import reverse
from django.test import override_settings
from rest_framework.exceptions import ErrorDetail

DISTANCE_URL = reverse('distance')
class TestDistanceAPI:

    def test_empty_body(self, api_client):
        """
        Scenario:
            - A request is made to the distance API with an empty body.
        Expectation:
            - The API returns a 400 Bad Request response.        
        """
        response = api_client.post(DISTANCE_URL, data={}, content_type='application/json')
        assert response.data == {
            'from_address': [ErrorDetail(string='This field is required.', code='required')],
            'destination_address': [ErrorDetail(string='This field is required.', code='required')]
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
            data=json.dumps({'from_address': 'invalid&%', 'destination_address': '123 Main St'}),
            content_type='application/json'
        )
        assert response.data == {
            'from_address': [ErrorDetail(string='Invalid from address: invalid&%', code='invalid')],
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
            data=json.dumps({'from_address': '123 Main St', 'destination_address': 'invalid&%'}),
            content_type='application/json'
        )
        assert response.data == {
            'destination_address': [ErrorDetail(string='Invalid destination address: invalid&%', code='invalid')],
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
            data=json.dumps({'from_address': 'none', 'destination_address': '456 Elm St'}),
            content_type='application/json'
        )
        assert response.data == [ErrorDetail(string='Could not geocode from_address: none', code='invalid')]
        assert response.status_code == 400
