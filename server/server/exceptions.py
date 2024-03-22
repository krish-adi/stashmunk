class StashMunkError(Exception):
    """Base class for all StashMunk Errors."""
    pass


class ModelError(StashMunkError):
    """Base class for all model exceptions."""

    def __init__(self, status_code, message, prefix=None):
        self.status_code = status_code
        self.message = message
        self.prefix = prefix

    def __str__(self):
        if self.prefix:
            return f"{self.prefix}::{self.status_code}: {self.message}"
        else:
            return f"{self.status_code}: {self.message}"
