"""This module contains exceptions used within Tidegear and consuming cogs."""


class ConfigurationError(Exception):
    """Raised whenever a cog's configuration prevents one of its features from functioning."""


class ContextError(Exception):
    """Raised whenever a command, function, or method is called from a context it is not supposed to be called from."""
