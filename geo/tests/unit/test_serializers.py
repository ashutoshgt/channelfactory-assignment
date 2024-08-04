import pytest
from unittest.mock import patch
from rest_framework.exceptions import ValidationError
from geo.serializers import GeocodeCacheSerializer, DistanceSerializer
from geo.models import GeocodeCache

class TestGeocodeCacheSerializer:
    
    def test_fields(self):
        """
        Scenario:
            - A GeocodeCacheSerializer is present in code.
        Expectation:
            - The serializer has the expected fields.
        """
        # Get the serializer's metadata
        meta = GeocodeCacheSerializer.Meta

        expected_fields = {
            'input_address',
            'latitude',
            'longitude',
            'formatted_address'
        }

        # Get the actual fields from the serializer
        actual_fields = set(meta.fields)

        assert actual_fields == expected_fields, f"GeocodeCacheSerializer fields do not match. Expected: {expected_fields}, but got: {actual_fields}"

class TestDistanceSerializer:

    def test_fields(self):
        """
        Scenario:
            - A DistanceSerializer instance is created.
        Expectation:
            - The serializer has the expected fields.
        """
        serializer = DistanceSerializer()

        expected_fields = {
            'from_address',
            'destination_address'
        }

        # Get the actual fields from the serializer
        actual_fields = set(serializer.fields.keys())

        assert actual_fields == expected_fields
        assert DistanceSerializer.ADDRESS_PATTERN == r'^[a-zA-Z0-9\s\.,-]+$'
    
    def test_validate_from_address_success(self):
        """
        Scenario:
            - validate_from_address is called with a valid value.
        Expectation:
            - The from_address value is returned as is.
        """
        serializer = DistanceSerializer()
        value = "123 Main St"
        assert serializer.validate_from_address(value) == value
    
    def test_validate_from_address_failure(self):
        """
        Scenario:
            - validate_from_address is called with an invalid value.
        Expectation:
            - ValidationError is raised
        """
        serializer = DistanceSerializer()
        value = "123 Main St&$"

        with pytest.raises(ValidationError) as error:
            serializer.validate_from_address(value)
        
        assert error.value.detail[0]==f"Invalid from address: {value}"
    
    def test_validate_destination_address_success(self):
        """
        Scenario:
            - validate_destination_address is called with a valid value.
        Expectation:
            - The destination_address value is returned as is.
        """
        serializer = DistanceSerializer()
        value = "123 Main St"
        assert serializer.validate_destination_address(value) == value
    
    def test_validate_destination_address_failure(self):
        """
        Scenario:
            - validate_destination_address is called with an invalid value.
        Expectation:
            - ValidationError is raised
        """
        serializer = DistanceSerializer()
        value = "123 Main St&$"

        with pytest.raises(ValidationError) as error:
            serializer.validate_destination_address(value)
        
        assert error.value.detail[0]==f"Invalid destination address: {value}"
