from django.db import models

# Create your models here.
class GeocodeCache(models.Model):
    """
    Model representing a geocode cache entry.

    Attributes:
        input_address (str): The input address used for geocoding.
        formatted_address (str): The formatted address returned by geocoding.
        latitude (float): The latitude coordinate of the geocoded address.
        longitude (float): The longitude coordinate of the geocoded address.
        created_at (datetime): The timestamp when the cache entry was created.

    Methods:
        __str__(): Returns a string representation of the geocode cache entry.
    """

    input_address = models.CharField(max_length=255)
    formatted_address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['input_address'], name='input_address_hash_idx'),
        ]

    def __str__(self):
        return f"{self.input_address}->{self.latitude}, {self.longitude}"
