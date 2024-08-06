import pytest
from django.db.utils import Error
from rest_framework.exceptions import ValidationError

from geo.serializers import DistanceSerializer


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

    def test_geocode_cache_hit(self, mock_geocode_cache, distance_serializer, mock_google_service):
        """
        Scenario:
            - geocode is called with an address that is already in the cache.
        Expectation:
            - Google API is not called
            - The cached GeocodeCache instance is returned.
            - The cache is not populated with the geocoded address.
        """
        address = "123 Main St"
        geocode_cache = mock_geocode_cache(
            input_address=address,
            formatted_address=address,
            latitude=37.123456,
            longitude=-122.987654
        )

        mock_geocode_cache.objects.filter.return_value.first.return_value = geocode_cache

        assert distance_serializer.geocode(address) == geocode_cache
        mock_geocode_cache.objects.filter.assert_called_once_with(input_address__iexact=address)
        mock_google_service.geocode.assert_not_called()

    def test_geocode_cache_miss(self, mock_geocode_cache, distance_serializer, mock_google_service):
        """
        Scenario:
            - geocode is called with an address that is not in the cache.
        Expectation:
            - The geocoded GeocodeCache instance is returned.
            - Google geocode api is used to fetch the geocode.
            - The cache is populated with the geocoded address.
        """
        address = "123 Main St"
        geocode_cache = mock_geocode_cache(
            input_address=address,
            formatted_address=address,
            latitude=37.123456,
            longitude=-122.987654
        )
        mock_geocode_cache.objects.filter.return_value.first.return_value = None
        mock_geocode_cache.objects.create.return_value = geocode_cache

        mock_google_service.geocode.return_value = {
            "formatted_address": geocode_cache.formatted_address,
            "geometry": {
                "location": {
                    "lat": geocode_cache.latitude,
                    "lng": geocode_cache.longitude
                }
            }
        }

        assert distance_serializer.geocode(address) == geocode_cache
        mock_geocode_cache.objects.filter.assert_called_once_with(input_address__iexact=address)
        mock_google_service.geocode.assert_called_once_with(address)
        mock_geocode_cache.objects.create.assert_called_once_with(
            input_address=address,
            formatted_address=geocode_cache.formatted_address,
            latitude=geocode_cache.latitude,
            longitude=geocode_cache.longitude
        )

    def test_geocode_cache_error(self, mock_geocode_cache, distance_serializer, mock_google_service):
        """
        Scenario:
            - geocode is called with cache failing due to DB issues.
        Expectation:
            - The geocoded GeocodeCache instance is returned.
            - Google geocode api is used to fetch the geocode.
            - The cache is not populated with the geocoded address.
        """
        address = "123 Main St"
        geocode_cache = mock_geocode_cache(
            input_address=address,
            formatted_address=address,
            latitude=37.123456,
            longitude=-122.987654
        )

        mock_geocode_cache.return_value = geocode_cache
        mock_geocode_cache.objects.filter.side_effect = Error('test error')
        mock_geocode_cache.objects.create.side_effect = Error('test error')

        mock_google_service.geocode.return_value = {
            "formatted_address": geocode_cache.formatted_address,
            "geometry": {
                "location": {
                    "lat": geocode_cache.latitude,
                    "lng": geocode_cache.longitude
                }
            }
        }
        
        assert distance_serializer.geocode(address) == geocode_cache
        mock_geocode_cache.objects.filter.assert_called_once_with(input_address__iexact=address)
        mock_google_service.geocode.assert_called_once_with(address)
        mock_geocode_cache.objects.create.assert_called_once_with(
            input_address=address,
            formatted_address=geocode_cache.formatted_address,
            latitude=geocode_cache.latitude,
            longitude=geocode_cache.longitude
        )

    def test_geocode_error(self, mock_geocode_cache, distance_serializer, mock_google_service):
        """
        Scenario:
            - geocode is called with Google geocode api failing.
        Expectation:
            - ValidationError is raised
            - Google Geocode API is called
            - Cache lookup is done
            - Cache population is not done
        """
        address = "123 Main St"

        mock_geocode_cache.objects.filter.return_value.first.return_value = None
        mock_google_service.geocode.return_value = None

        with pytest.raises(ValidationError) as error:
            distance_serializer.geocode(address)
        
        assert error.value.detail[0] == f"Could not geocode address: {address}"
        mock_geocode_cache.objects.filter.assert_called_once_with(input_address__iexact=address)
        mock_google_service.geocode.assert_called_once_with(address)
        mock_geocode_cache.objects.create.assert_not_called()
