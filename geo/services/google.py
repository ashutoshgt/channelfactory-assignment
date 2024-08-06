import logging

import googlemaps

logger = logging.getLogger(__name__)

class GoogleService:
    """
    A class that provides geocoding services using the Google Maps API.
    """

    _instance = None

    def __new__(cls, api_key):
        """
        Creates a new instance of the GoogleService class.

        Args:
            api_key (str): The API key for accessing the Google Maps API.

        Returns:
            GoogleService: An instance of the GoogleService class.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.client = googlemaps.Client(api_key)
        print(cls._instance.client)
        return cls._instance

    def geocode(self, address):
        """
        Geocodes the given address using the Google Maps API.

        Args:
            address (str): The address to geocode.

        Returns:
            dict: A dictionary containing the geocoded address information.
        """
        logger.info("Geocoding address: %s", address)

        geocode_result = self.client.geocode(address)
        print(geocode_result)
        if geocode_result:
            return geocode_result[0]
        else:
            logger.error("Could not geocode address: %s", address)
            return None
