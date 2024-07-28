from rest_framework.decorators import api_view
from rest_framework.response import Response
from geo.serializers import AddressSerializer

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
    
    serialized_data = AddressSerializer(data=request.data)
    
    if not serialized_data.is_valid():
        return Response(serialized_data.errors, status=400)
    
    return Response(serialized_data.validated_data)
