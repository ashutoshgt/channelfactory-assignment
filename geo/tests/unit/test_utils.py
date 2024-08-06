import pytest
from geo.services.utils import haversine_distance

def test_haversine_distance():
    """
        Covers all test cases for the haversine_distance function.
    """
    # Test case 1: Distance between same points should be 0
    assert haversine_distance(40.7128, -74.0060, 40.7128, -74.0060) == 0

    # Test case 2: Distance between New York and Los Angeles
    assert pytest.approx(haversine_distance(40.7128, -74.0060, 34.0522, -118.2437), 0.1) == 3939.2

    # Test case 3: Distance between London and Paris
    assert pytest.approx(haversine_distance(51.5074, -0.1278, 48.8566, 2.3522), 0.1) == 343.8

    # Test case 4: Distance between Sydney and Tokyo
    assert pytest.approx(haversine_distance(-33.8651, 151.2099, 35.6895, 139.6917), 0.1) == 7828.5

    # Test case 5: Distance between North Pole and South Pole
    assert pytest.approx(haversine_distance(90, 0, -90, 0), 0.1) == 20015.1

    # Test case 6: Distance between equator and prime meridian
    assert pytest.approx(haversine_distance(0, 0, 0, 180), 0.1) == 20015.1

    # Test case 7: Distance between two random points
    assert pytest.approx(haversine_distance(37.7749, -122.4194, 34.0522, -118.2437), 0.1) == 543.4

    # Test case 8: Distance between two random points
    assert pytest.approx(haversine_distance(51.5074, -0.1278, 40.7128, -74.0060), 0.1) == 5573.9

    # Test case 9: Distance between two random points
    assert pytest.approx(haversine_distance(-33.8651, 151.2099, 48.8566, 2.3522), 0.1) == 16961.7

    # Test case 10: Distance between two random points
    assert pytest.approx(haversine_distance(37.7749, -122.4194, -33.8651, 151.2099), 0.1) == 12079.2

    # Test case 11: for None value
    assert haversine_distance(None, -122.4194, -33.8651, 151.2099) == None
    assert haversine_distance(None, None, -33.8651, 151.2099) == None
    assert haversine_distance(None, None, None, 151.2099) == None
    assert haversine_distance(None, None, None, None) == None
