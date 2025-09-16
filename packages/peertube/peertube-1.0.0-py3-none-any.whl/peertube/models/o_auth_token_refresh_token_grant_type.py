from enum import Enum


class OAuthTokenRefreshTokenGrantType(str, Enum):
    """OAuthTokenRefreshTokenGrantType enumeration."""

    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"

    def __str__(self) -> str:
        return str(self.value)
