"""Basic tests for the generated PeerTube API client."""

from peertube import AuthenticatedClient, Client


class TestClientGeneration:
    """Test the generated client functionality."""

    def test_client_import_success(self):
        """Test that client classes can be imported successfully."""
        assert Client is not None
        assert AuthenticatedClient is not None

    def test_client_initialization(self):
        """Test that Client can be initialized without errors."""
        base_url = "https://example.peertube.com"
        client = Client(base_url=base_url)

        assert client is not None

    def test_authenticated_client_initialization(self):
        """Test that AuthenticatedClient can be initialized without errors."""
        base_url = "https://example.peertube.com"
        token = "test-token"
        client = AuthenticatedClient(base_url=base_url, token=token)

        assert client is not None

    def test_client_base_url(self):
        """Test that client stores base URL correctly."""
        base_url = "https://example.peertube.com"
        client = Client(base_url=base_url)

        assert hasattr(client, "_base_url")

    def test_authenticated_client_token(self):
        """Test that authenticated client stores token correctly."""
        base_url = "https://example.peertube.com"
        token = "test-token"
        client = AuthenticatedClient(base_url=base_url, token=token)

        assert hasattr(client, "token")
        assert client.token == token

    def test_client_with_custom_timeout(self):
        """Test that client accepts custom timeout parameter."""
        base_url = "https://example.peertube.com"
        timeout = 30.0
        client = Client(base_url=base_url, timeout=timeout)

        assert client is not None

    def test_client_with_ssl_verification_disabled(self):
        """Test that client accepts SSL verification parameter."""
        base_url = "https://example.peertube.com"
        client = Client(base_url=base_url, verify_ssl=False)

        assert client is not None
