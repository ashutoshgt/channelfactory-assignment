import pytest
from unittest.mock import patch

from geo.serializers import DistanceSerializer

@pytest.fixture
def mock_google_service():
    with patch('geo.serializers.GoogleService') as MockGoogleService:
        yield MockGoogleService()

@pytest.fixture
def mock_geocode_cache():
    with patch('geo.serializers.GeocodeCache') as MockGeocodeCache:
        yield MockGeocodeCache

@pytest.fixture
def distance_serializer():
    return DistanceSerializer()

@pytest.fixture
def mock_google_client():
    with patch('geo.services.google.googlemaps.Client') as MockGoogleClient:
        yield MockGoogleClient
