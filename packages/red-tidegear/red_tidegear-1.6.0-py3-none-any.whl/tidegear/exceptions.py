"""This module contains exceptions used within Tidegear and consuming cogs."""

from typing import Any, Callable

import discord
from redbot.core import commands

from tidegear import chat_formatting as cf


class TidegearError(Exception):
    """Parent exception for all exceptions originating from Tidegear.

    Attributes:
        message: An error message. May be shown to end users.
        send_error_kwargs: Additional keyword arguments to pass to [`send_error()`][tidegear.utils.send_error]. Does not support `content`.
    """

    message: str
    send_error_kwargs: dict[str, Any]

    def __init__(self, message: str, /, **send_error_kwargs: Any) -> None:
        super().__init__(message)
        self.send_error_kwargs = send_error_kwargs
        self.send_error_kwargs.pop("content", None)
        self.send_error_kwargs.setdefault("ephemeral", True)

    async def send(
        self, messeagable: commands.Context | discord.abc.Messageable, /, func: Callable[[str], str] = cf.error, **kwargs: Any
    ) -> discord.Message:
        """Send a message with the contents of this error's message.

        Args:
            messeagable: The channel or context to send the message to.
            func: The function to use to wrap the message.
            **kwargs: Additional keyword arguments to pass to `await messeagable.send()`.

        Returns:
            The sent message.
        """
        from tidegear.utils import send_error  # noqa: PLC0415 # this is here to prevent potential circular imports in the future

        return await send_error(messeagable, content=self.message, func=func, **self.send_error_kwargs | kwargs)


class ConfigurationError(TidegearError):
    """Raised whenever a cog's configuration prevents one of its features from functioning."""


class NotFoundError(TidegearError):
    """Raised whenever an operation doing some kind of search or query fails.
    Essentially a [`LookupError`][], but it is a subclass of [`TidegearError`][tidegear.exceptions.TidegearError].
    """


class ContextError(TidegearError):
    """Raised whenever a command, function, or method is called from a context it is not supposed to be called from."""
