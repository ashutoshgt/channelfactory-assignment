from api import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re
from geo.services.google import GoogleService
from geo.services.utils import haversine_distance

@api_view(['POST'])
def distance(request):

    # Validate the request payload
    from_address = request.POST.get('from_address')
    destination_address = request.POST.get('destination_address')

    if not from_address:
        return Response({"error": "Missing from_address"})
    
    if not destination_address:
        return Response({"error": "Missing destination_address"})
    
    # Validate the addresses using regex
    address_pattern = r'^[a-zA-Z0-9\s\.,]+$'
    if not re.match(address_pattern, from_address):
        return Response({"error": "Invalid/missing from_address"})
    
    if not re.match(address_pattern, destination_address):
        return Response({"error": "Invalid/missing destination_address"})
    
    # Geocode both the origin and destination addresses

    google_service = GoogleService(settings.GOOGLE_MAPS_API_KEY)
    from_response = google_service.geocode(from_address)
    destination_response = google_service.geocode(destination_address)

    # Calculate the distance between the two points
    

    return Response({"from_address": from_response, "destination_address": destination_response})
