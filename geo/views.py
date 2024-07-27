from api import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re
from geo.services.google import GoogleService
from geo.services.utils import haversine_distance

@api_view(['POST'])
def distance(request):
    """
    Calculate the distance between two addresses and return the response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the calculated distance and address details.

    Raises:
        None

    """

    # Validate the request payload
    from_address = request.data.get('from_address')
    destination_address = request.data.get('destination_address')
    
    # Validate the addresses using regex
    address_pattern = r'^[a-zA-Z0-9\s\.,]+$'
    if not from_address or not re.match(address_pattern, from_address):
        return Response({"error": "Invalid/missing from_address"})
    
    if not destination_address or not re.match(address_pattern, destination_address):
        return Response({"error": "Invalid/missing destination_address"})
    
    # Geocode both the origin and destination addresses
    google_service = GoogleService(settings.GOOGLE_MAPS_API_KEY)
    from_lat, from_lng, from_formatted_address = google_service.geocode(from_address)
    destination_lat, destination_lng, destination_formatted_address = google_service.geocode(destination_address)

    # Calculate the distance between the two points and return the response

    return Response(
        {
            "from_address": {
                "original": from_address,
                "lat": from_lat,
                "long": from_lng,
                "formatted_address": from_formatted_address
            }, 
            "destination_address": {
                "original": destination_address,
                "lat": destination_lat,
                "long": destination_lng,
                "formatted_address": destination_formatted_address
            },
            "distance": haversine_distance(from_lat, from_lng, destination_lat, destination_lng)
        }
    )
