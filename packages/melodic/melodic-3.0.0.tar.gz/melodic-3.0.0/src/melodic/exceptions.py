class MelodicError(Exception):
    """A base exception for general library errors."""


class ConfigError(MelodicError):
    """Raise for configuration related errors."""


class NetworkError(MelodicError):
    """Raise for network issues, such as connection errors or bad responses."""

    def __init__(self, message: str, status: int | None = None):
        """Initialize the NetworkError.

        Args:
            message: The error message.
            status: The HTTP status code, if available.
        """
        super().__init__(message)
        self.status = status


class SessionNotStartedError(NetworkError):
    """Raise when a network operation is attempted before starting a session."""


class DiscographyNotFoundError(MelodicError):
    """Raise when an artist's discography page contains no track metadata."""


class IPBlockedError(NetworkError):
    """Raise when an IP has been blocked by the target website."""


class StorageError(MelodicError):
    """Raise for storage related errors."""
