import logging
import re

from rest_framework import serializers

from api import settings
from geo.constants import (GEOCODE_ERROR, INVALID_DESTINATION_ADDRESS, INVALID_FROM_ADDRESS)
from geo.models import GeocodeCache
from geo.services.google import GoogleService
from geo.services.utils import haversine_distance

logger = logging.getLogger(__name__)

class GeocodeCacheSerializer(serializers.ModelSerializer):
	"""
	Serializer for the GeocodeCache model.
	"""
	class Meta:
		model = GeocodeCache
		fields = ['input_address', 'latitude', 'longitude', 'formatted_address']

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

		google_service = GoogleService(settings.GOOGLE_MAPS_API_KEY)

		# Geocode the origin address
		geocoded_from_address = None
		try:
			# Check cache
			geocoded_from_address = GeocodeCache.objects.filter(
				input_address__iexact=from_address
			).first()
		except Exception as e:
			# Fail silently
			logger.error("Error fetching from_address from cache: %s", e)

		if not geocoded_from_address:
			logger.info("Cache miss for from_address: %s", from_address)
			
			geocode_response = google_service.geocode(from_address)
			
			if not geocode_response:
				raise serializers.ValidationError(f"{GEOCODE_ERROR} from_address: {from_address}")
			
			cache_from_address_serializer = GeocodeCacheSerializer(data={
				"input_address": from_address,
				"formatted_address": geocode_response.get("formatted_address"),
				"latitude": geocode_response.get("geometry", {}).get("location", {}).get("lat"),
				"longitude": geocode_response.get("geometry", {}).get("location", {}).get("lng")
			})
			
			if cache_from_address_serializer.is_valid():
				logger.info("Caching geocoded from_address: %s", from_address)
				try:
					geocoded_from_address = cache_from_address_serializer.save()
				except Exception as e:
					geocoded_from_address = GeocodeCache(
						input_address=cache_from_address_serializer.data.get("input_address"),
						formatted_address=cache_from_address_serializer.data.get("formatted_address"),
						latitude=cache_from_address_serializer.data.get("latitude"),
						longitude=cache_from_address_serializer.data.get("longitude")
					)
					logger.error("Error caching from_address: %s", e)
			else:
				logger.error("Error caching from_address: %s, errors: %s", from_address, cache_from_address_serializer.errors)
		
		# Geocode the destination address
		geocoded_destination_address = GeocodeCache.objects.filter(
			input_address__iexact=destination_address
		).first()
		
		geocoded_destination_address = None
		try:
			# Check cache
			geocoded_destination_address = GeocodeCache.objects.filter(
				input_address__iexact=destination_address
			).first()
		except Exception as e:
			# Fail silently
			logger.error("Error fetching destination_address from cache: %s", e)
		
		if not geocoded_destination_address:
			logger.info("Cache miss for destination_address: %s", destination_address)
			geocode_response = google_service.geocode(destination_address)
			if not geocode_response:
				raise serializers.ValidationError(f"{GEOCODE_ERROR} destination_address: {destination_address}")
			
			cache_dest_address_serializer = GeocodeCacheSerializer(data={
				"input_address": destination_address,
				"formatted_address": geocode_response.get("formatted_address"),
				"latitude": geocode_response.get("geometry", {}).get("location", {}).get("lat"),
				"longitude": geocode_response.get("geometry", {}).get("location", {}).get("lng")
			})

			if cache_dest_address_serializer.is_valid():
				logger.info("Caching geocoded destination_address: %s", destination_address)
				try:
					geocoded_destination_address = cache_dest_address_serializer.save()
				except:
					geocoded_destination_address = GeocodeCache(
						input_address=cache_dest_address_serializer.data.get("input_address"),
						formatted_address=cache_dest_address_serializer.data.get("formatted_address"),
						latitude=cache_dest_address_serializer.data.get("latitude"),
						longitude=cache_dest_address_serializer.data.get("longitude")
					)
					logger.error("Error caching destination_address: %s", destination_address)
			else:
				logger.error("Error caching destination_address: %s, errors: %s", destination_address, cache_dest_address_serializer.errors)
			
		return geocoded_from_address, geocoded_destination_address

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
