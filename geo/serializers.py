import re
import logging
from rest_framework import serializers

from geo.services.google import GoogleService
from geo.services.utils import haversine_distance
from geo.constants import INVALID_FROM_ADDRESS, INVALID_DESTINATION_ADDRESS, GEOCODE_ERROR
from api import settings

logger = logging.getLogger(__name__)

class AddressSerializer(serializers.Serializer):
	"""
	Serializer for validating and geocoding address data.
	"""

	from_address = serializers.CharField(max_length=255)
	destination_address = serializers.CharField(max_length=255)

	def validate(self, data):
		"""
		Validates the from_address and destination_address fields.
		Geocodes both the origin and destination addresses.
		Calculates the distance between the two addresses using haversine formula.

		Args:
			data (dict): The input data containing from_address and destination_address.

		Returns:
			dict: The validated and geocoded data containing from_address, destination_address, and distance.
		"""

		address_pattern = r'^[a-zA-Z0-9\s\.,-]+$'

		from_address = data.get("from_address")
		destination_address = data.get("destination_address")

		if not from_address or not re.match(address_pattern, from_address):
			logger.error("%s: %s", INVALID_FROM_ADDRESS, from_address)
			raise serializers.ValidationError(INVALID_FROM_ADDRESS)

		if not destination_address or not re.match(address_pattern, destination_address):
			logger.error("%s: %s", INVALID_DESTINATION_ADDRESS, destination_address)
			raise serializers.ValidationError(INVALID_DESTINATION_ADDRESS)

		# Geocode both the origin and destination addresses
		google_service = GoogleService(settings.GOOGLE_MAPS_API_KEY)

		from_geocode_response = google_service.geocode(from_address)
		if not from_geocode_response:
			raise serializers.ValidationError(f"{GEOCODE_ERROR} from_address")
		
		destination_geocode_response = google_service.geocode(destination_address)
		if not destination_geocode_response:
			raise serializers.ValidationError(f"{GEOCODE_ERROR} destination_address")
		
		from_location = from_geocode_response.get("geometry", {}).get("location")
		from_lat = from_location.get("lat") if from_location else None
		from_lng = from_location.get("lng") if from_location else None

		destination_location = destination_geocode_response.get("geometry", {}).get("location")
		destination_lat = destination_location.get("lat") if destination_location else None
		destination_lng = destination_location.get("lng") if destination_location else None

		data = {
			"from_address": {
				"original": from_address,
				"lat": from_lat,
				"long": from_lng,
				"formatted_address": from_geocode_response.get("formatted_address")
			},
			"destination_address": {
				"original": destination_address,
				"lat": destination_lat,
				"long": destination_lng,
				"formatted_address": destination_geocode_response.get("formatted_address")
			},
			"distance": haversine_distance(from_lat, from_lng, destination_lat, destination_lng)
		}

		return data
