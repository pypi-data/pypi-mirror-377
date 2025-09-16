#!/usr/bin/env python3
"""Example usage of the PeerTube API client.

This script demonstrates the basic usage patterns for the generated PeerTube client.
"""

from peertube import AuthenticatedClient, Client


def basic_client_usage():
    """Demonstrate basic unauthenticated client usage."""
    print("=== Basic Client Usage ===")

    # Create an unauthenticated client
    _client = Client(base_url="https://peertube.example.com")

    print("Client created successfully")
    print(
        "This client can be used for public endpoints that don't require authentication."
    )

    # Note: We're not making actual API calls since this is just a demo
    print("Example usage (not executed):")
    print("  categories = get_categories.sync(client=client)")
    print("  languages = get_languages.sync(client=client)")
    print()


def authenticated_client_usage():
    """Demonstrate authenticated client usage."""
    print("=== Authenticated Client Usage ===")

    # Create an authenticated client
    auth_client = AuthenticatedClient(
        base_url="https://peertube.example.com", token="your-api-token-here"
    )

    print("Authenticated client created successfully")
    print(f"Authentication token prefix: {auth_client.prefix}")
    print(f"Auth header name: {auth_client.auth_header_name}")
    print("This client can be used for endpoints that require authentication.")
    print()


def async_client_usage():
    """Demonstrate async client usage patterns."""
    print("=== Async Client Usage ===")
    print("For asynchronous operations, use the asyncio methods:")
    print()
    print("async def get_video_data(client):")
    print("    async with client as async_client:")
    print("        categories = await get_categories.asyncio(client=async_client)")
    print("        languages = await get_languages.asyncio(client=async_client)")
    print("        return categories, languages")
    print()


def advanced_client_configuration():
    """Demonstrate advanced client configuration."""
    print("=== Advanced Client Configuration ===")

    # Client with custom timeout and SSL settings
    _client = Client(
        base_url="https://peertube.example.com",
        timeout=30.0,
        verify_ssl=False,  # Only for testing!
        follow_redirects=True,
        headers={"User-Agent": "MyPeerTubeApp/1.0"},
        cookies={"session": "example-session-id"},
    )

    print("Client configured with custom options:")
    print("  - Custom timeout")
    print("  - SSL verification disabled")
    print("  - Redirect following disabled")
    print("  - Custom headers")
    print("  - Session cookies")
    print()


def response_handling_patterns():
    """Demonstrate response handling patterns."""
    print("=== Response Handling Patterns ===")
    print()
    print("# Simple response (just the data):")
    print("categories = get_categories.sync(client=client)")
    print()
    print("# Detailed response (includes status code, headers, etc.):")
    print("response = get_categories.sync_detailed(client=client)")
    print("if response.status_code == 200:")
    print("    categories = response.parsed")
    print("    print(f'Status: {response.status_code}')")
    print("    print(f'Headers: {response.headers}')")
    print()


def main():
    """Run all examples."""
    print("PeerTube API Client Usage Examples")
    print("=" * 50)
    print()

    basic_client_usage()
    authenticated_client_usage()
    async_client_usage()
    advanced_client_configuration()
    response_handling_patterns()

    print("=== Available API Modules ===")
    print("The following API modules are available:")
    api_modules = [
        "accounts",
        "video",
        "videos",
        "users",
        "session",
        "config",
        "search",
        "video_channels",
        "video_playlists",
        "my_user",
        "my_subscriptions",
        "my_notifications",
        "register",
    ]

    for module in api_modules:
        print(f"  - peertube.api.{module}")

    print()
    print("For complete API documentation, see:")
    print("https://docs.joinpeertube.org/api-rest-reference.html")


if __name__ == "__main__":
    main()
