import googlemaps

import googlemaps

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
        return cls._instance

    def geocode(self, address):
        """
        Geocodes the given address using the Google Maps API.

        Args:
            address (str): The address to geocode.

        Returns:
            tuple or None: The geocoded location as a dictionary with 'latitude' and 'longitude' keys,
            or None if the address could not be geocoded.
            Tuple will consist of latitude, longitude and formatted_address
        """
        geocode_result = self.client.geocode(address)
        if geocode_result:
            first_result = geocode_result[0]
            location = first_result['geometry']['location']
            formatted_address = first_result['formatted_address']
            return location['lat'], location['lng'], formatted_address
        else:
            return None
