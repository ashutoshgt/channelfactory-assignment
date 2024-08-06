import logging
import re

from django.db.utils import Error
from rest_framework import serializers

from api import settings
from geo.constants import (GEOCODE_ERROR, INVALID_DESTINATION_ADDRESS, INVALID_FROM_ADDRESS)
from geo.models import GeocodeCache
from geo.services.google import GoogleService
from geo.services.utils import haversine_distance

logger = logging.getLogger(__name__)

class DistanceSerializer(serializers.Serializer):
	"""
	Serializer for validating, geocoding address data and calculating distance between them.
	"""
	ADDRESS_PATTERN = r'^[a-zA-Z0-9\s\.,-]+$'

	from_address = serializers.CharField(max_length=255)
	destination_address = serializers.CharField(max_length=255)

	def validate_from_address(self, value):
		"""Validates the from_address field.

		Args:
			value (string): The from_address field value.
		"""
		if not re.match(self.ADDRESS_PATTERN, value):
			logger.error("%s: %s", INVALID_FROM_ADDRESS, value)
			raise serializers.ValidationError(f"{INVALID_FROM_ADDRESS}: {value}")
		return value

	def validate_destination_address(self, value):
		"""Validates the destination_address field.

		Args:
			value (string): The destination_address field value.
		"""
		if not re.match(self.ADDRESS_PATTERN, value):
			logger.error("%s: %s", INVALID_DESTINATION_ADDRESS, value)
			raise serializers.ValidationError(f"{INVALID_DESTINATION_ADDRESS}: {value}")
		return value

	def geocode(self, address) -> GeocodeCache:
		"""
		Geocodes the given address using the Google Maps API.

		Args:
			address (str): The address to be geocoded.

		Returns:
			GeocodeCache: The geocoded address information.

		Raises:
			serializers.ValidationError: If the geocoding fails or the address is invalid.
		"""

		google_service = GoogleService(settings.GOOGLE_MAPS_API_KEY)

		geocoded_address = None

		try:
			# Check cache
			geocoded_address = GeocodeCache.objects.filter(input_address__iexact=address).first()
		except Error as e:
			# Fail silently
			logger.error("Error fetching address from cache: %s", e)

		if not geocoded_address:
			logger.info("Cache miss for address: %s", address)

			geocode_response = google_service.geocode(address)

			if not geocode_response:
				raise serializers.ValidationError(f"{GEOCODE_ERROR} address: {address}")

			geocoded_data = {
				"input_address": address,
				"formatted_address": geocode_response.get("formatted_address"),
				"latitude": geocode_response.get("geometry", {}).get("location", {}).get("lat"),
				"longitude": geocode_response.get("geometry", {}).get("location", {}).get("lng")
			}

			logger.info("Caching geocoded address: %s", address)
			try:
				geocoded_address = GeocodeCache.objects.create(**geocoded_data)
			except Error as e:
				logger.error("Error caching address: %s", e)
				geocoded_address = GeocodeCache(**geocoded_data)

		return geocoded_address

	def create(self, validated_data):
		"""
		Geocodes both the origin and destination addresses if not present in cache.
		Caches the output of geocoding in the database in case of cache miss.

		Args:
			data (dict): The input data containing from_address and destination_address.

		Returns:
			tuple: The geocoded from_address and destination_address objects of GeocodeCache.
		"""
		from_address = validated_data.get("from_address")
		destination_address = validated_data.get("destination_address")
			
		return self.geocode(from_address), self.geocode(destination_address)

	def calculate_distance(self) -> dict:
		"""
		Calculates the distance between two addresses and returns the geocoded addresses and the distance.

		Returns:
			dict: A dictionary containing the geocoded from address, geocoded destination address, and the distance between them.
		"""
		geocoded_from_address, geocoded_destination_address = self.save()

		return {
			"from_address": {
				"original": geocoded_from_address.input_address,
				"formatted": geocoded_from_address.formatted_address,
				"lat": geocoded_from_address.latitude,
				"long": geocoded_from_address.longitude
			},
			"destination_address": {
				"original": geocoded_destination_address.input_address,
				"formatted": geocoded_destination_address.formatted_address,
				"lat": geocoded_destination_address.latitude,
				"long": geocoded_destination_address.longitude
			},
			"distance": haversine_distance(
				geocoded_from_address.latitude,
				geocoded_from_address.longitude,
				geocoded_destination_address.latitude,
				geocoded_destination_address.longitude
			)
		}
