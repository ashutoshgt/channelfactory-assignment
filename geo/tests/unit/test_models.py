from django.utils import timezone
from django.db import models
from geo.models import GeocodeCache

class TestGeocodeCache:
    
    def test_fields(self):
        """
        Scenario:
            - A GeocodeCache model is present in code.
        Expectation:
            - The model has the expected fields.
        """
        # Get the model's metadata
        meta = GeocodeCache._meta

        expected_fields = {
            'id',
            'input_address',
            'latitude',
            'longitude',
            'formatted_address',
            'created_at'
        }

        # Get the actual fields from the model
        actual_fields = {field.name for field in meta.get_fields()}

        assert actual_fields == expected_fields, f"GeocodeCache model fields do not match. Expected: {expected_fields}, but got: {actual_fields}"

    def test_has_index(self):
        """
        Scenario:
            - A GeocodeCache model is present in code.
        Expectation:
            - The model has an index on the input_address field.
        """
        # Get the model's metadata
        meta = GeocodeCache._meta

        # Check if the index exists
        index_exists = any(isinstance(index, models.Index) and 'input_address' in index.fields for index in meta.indexes)

        assert index_exists, "GeocodeCache model should have an index on the input_address field"

    def test_str(self):
        """Scenario:
            - A GeocodeCache instance is created.
        Expectation:
            - The __str__() method returns a string representation of the geocode cache
        """
        geocode_cache = GeocodeCache(
            input_address="123 Main St",
            formatted_address="123 Main St, City, State",
            latitude=37.123456,
            longitude=-122.987654,
            created_at=timezone.now()
        )
        expected_str = "123 Main St -> 37.123456, -122.987654"
        assert str(geocode_cache) == expected_str
    
