from geo.services.google import GoogleService

class TestGoogleService:

    def test_singleton(self, mock_google_client):
        """
        Scenario:
            - Two instances of GoogleService are created.
        Expectation:
            - Both instances are the same object.
        """
        google_service1 = GoogleService("API_KEY")
        google_service2 = GoogleService("API_KEY")

        assert google_service1 is google_service2
        mock_google_client.assert_called_once_with("API_KEY")
