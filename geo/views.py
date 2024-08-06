from rest_framework.decorators import api_view
from rest_framework.response import Response

from geo.serializers import DistanceSerializer


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
    
    distance_serializer = DistanceSerializer(data=request.data)
    
    if not distance_serializer.is_valid():
        return Response(distance_serializer.errors, status=400)
    
    # Get the response from the calculate_distance method
    response = distance_serializer.calculate_distance()

    return Response(response)
