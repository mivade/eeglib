"""Custom exception types."""


class BaseError(Exception):
    pass


class InvalidPathError(BaseError):
    """Raised when an invalid path is encountered."""
