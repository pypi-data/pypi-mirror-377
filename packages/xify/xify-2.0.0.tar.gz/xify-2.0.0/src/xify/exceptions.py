class XifyError(Exception):
    """A base exception for general library errors."""


class ConfigError(XifyError):
    """Raise for configuration related errors."""
