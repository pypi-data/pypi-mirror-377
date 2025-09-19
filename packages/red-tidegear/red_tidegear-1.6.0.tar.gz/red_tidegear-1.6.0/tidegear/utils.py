# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""A collection of useful utility functions and classes, to reduce repetitiveness between cogs."""

import functools
import inspect
import os
import warnings
from contextlib import contextmanager
from datetime import datetime
from enum import StrEnum
from importlib.resources import as_file, files
from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, Callable, Generator

import discord
from discord.utils import MISSING
from red_commons.logging import RedTraceLogger
from redbot.core import commands

from tidegear import chat_formatting as cf
from tidegear.constants import FALSE, NONE, TRUE
from tidegear.metadata import SemVer
from tidegear.version import version

if TYPE_CHECKING:
    from functools import _Wrapped


def deprecated_alias(
    *,
    new_func: Callable,
    old_name: str,
    module_name: str = "tidegear",
    current_version: SemVer = version,
    removal_version: SemVer | None = None,
    kwarg_map: dict[str, str] | None = None,
) -> "_Wrapped[..., Any, ..., Any]":
    """Create a deprecated alias for a function.

    Args:
        new_func: The new function to forward calls to.
        old_name: The deprecated function name.
        module_name: The name of the module to mention in the deprecation warning. Only does anything if `removal_version` is also passed.
        current_version: The current version of whatever module the deprecated function is coming from.
            For Tidegear cogs, this would be [`tidegear.Cog.metadata.version`][tidegear.metadata.CogMetadata].
        removal_version: The version in which the alias will be removed.
        kwarg_map: Optional mapping from old kwarg names to new kwarg names.

    Returns:
        The wrapped alias function.
    """

    @functools.wraps(new_func)
    def wrapper(*args, **kwargs):
        if removal_version and current_version >= removal_version:
            raise AttributeError(old_name)

        if kwarg_map is not None:
            for old_kw, new_kw in list(kwarg_map.items()):
                if old_kw in kwargs:
                    if new_kw in kwargs:
                        msg = f"{old_name} received both '{old_kw}' (deprecated) and '{new_kw}'"
                        raise TypeError(msg)
                    kwargs[new_kw] = kwargs.pop(old_kw)

        warnings.warn(
            (
                f"'{old_name}' is deprecated{f', and will be removed in {module_name} {removal_version}' if removal_version else ''}. "
                f"Please use '{new_func.__module__}.{new_func.__name__}' instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return new_func(*args, **kwargs)

    wrapper.__name__ = old_name
    return wrapper


@contextmanager
def set_env(
    key: str,
    value: str | None,
    logger: RedTraceLogger | None = None,
) -> Generator[None, Any, None]:
    """Temporarily set or unset an environment variable, then restore old value or delete on exit.

    Example:
        ```python
        import os
        from tidegear.utils import set_env


        def hello_world():
            return os.environ.get("HELLO_WORLD")


        with set_env(key="HELLO_WORLD", value="hello world"):
            print(hello_world())  # hello world

        print(hello_world())  # None
        ```

    Args:
        key: The environment variable to set.
        value: The content you want to set the environment variable to.
            If this is None, the environment variable will be deleted if it exists.
        logger: The logger to use to log the environment variables. Logs at `TRACE` level.
    """
    old_value = os.environ.get(key)
    if logger:
        logger.trace("Setting '%s' -> '%s'", key, value)
    if value is not None:
        os.environ[key] = value
    else:
        os.environ.pop(key, None)

    try:
        yield
    finally:
        if logger:
            logger.trace("Restoring '%s' -> '%s'", key, old_value)
        if old_value is not None:
            os.environ[key] = old_value
        else:
            os.environ.pop(key, None)


def class_overrides_attribute(child: type, parent: type, attribute: str) -> bool:
    """Check whether or not a child class overrides an attribute from a parent class.

    Args:
        child (type): The child class to check against.
        parent (type): The parent class to check against.
        attribute (str): The name of the attribute to check for.

    Raises:
        TypeError: If the `child` class is not a subclass of `parent`.
        AttributeError: If `attribute` does not exist on `parent`.

    Returns:
        Whether or not the attribute specified is overridden on `child`.
    """
    if not issubclass(child, parent):
        msg = f"{child.__name__} is not a subclass of {parent.__name__}!"
        raise TypeError(msg)

    child_attr = inspect.getattr_static(obj=child, attr=attribute, default=None)

    try:
        parent_attr = inspect.getattr_static(obj=parent, attr=attribute)
    except AttributeError as e:
        msg = f"Parent class {parent} does not have an attribute named {attribute}!"
        raise AttributeError(msg) from e

    return child_attr is not parent_attr


def get_bool_emoji(value: bool | None) -> str:
    """Return a unicode emoji based on a boolean value.

    Example:
        ```python
        from tidegear.utils import get_bool_emoji

        print(get_bool_emoji(True))  # ✅
        print(get_bool_emoji(False))  # 🚫
        print(get_bool_emoji(None))  # ❓️
        ```

    Args:
        value: The boolean value to check against.

    Returns:
        The corresponding unicode emoji.
    """
    match value:
        case True:
            return TRUE
        case False:
            return FALSE
        case _:
            return NONE


def get_asset_as_file(*, package: str = "tidegear.assets", filename: str, description: str | None = None, spoiler: bool = MISSING) -> discord.File:
    """Create a [`discord.File`][] from a file within a Python package.

    Args:
        package: The package to retrieve the file from.
        filename: The name of the file you'd like to retrieve. Does not support subpaths.
        description: The description of the uploaded file on Discord, used by screen readers.
        spoiler: Whether or not to mark the image as a spoiler on Discord.

    Raises:
        ImportError: Raised if the package provided cannot be found.
        FileNotFoundError: Raised if the filename provided does not exist within the provided package.

    Returns:
        The resulting object.
    """
    if not find_spec(name=package):
        msg = f"Unable to find a package named '{package}'!"
        raise ImportError(msg)

    asset = files(package=package).joinpath(filename)
    with as_file(asset) as path:
        if not path.exists():
            msg = f"Asset at path '{path}' does not exist! Is there a file named '{filename}' in the '{package}' package?"
            raise FileNotFoundError(msg)
        return discord.File(fp=path, filename=filename, description=description, spoiler=spoiler)


def title(string: str, /) -> str:
    """Replace any underscores in a string with spaces, then titlecase it.

    Args:
        string: The string to modify.

    Returns:
        The modified string.
    """
    return string.replace("_", " ").title()


class TimestampStyle(StrEnum):
    """Discord timestamp format options."""

    SHORT_TIME = "t"
    """`4:45 PM`"""
    LONG_TIME = "T"
    """`4:45:33 PM`"""
    SHORT_DATE = "d"
    """`7/5/25`"""
    LONG_DATE = "D"
    """`July 5th, 2025`"""
    SHORT_DATE_AND_TIME = "f"
    """`July 5th, 2025 at 4:45 PM`"""
    LONG_DATE_AND_TIME = "F"
    """`Saturday, July 5th, 2025 at 4:45 PM`"""
    RELATIVE = "R"
    """`3 minutes ago`"""


def format_datetime(dt: datetime, style: TimestampStyle = TimestampStyle.SHORT_DATE_AND_TIME) -> str:
    """Format a datetime into a Discord-compatible timestamp string.

    Similar to [`discord.utils.format_dt`][], but uses an enum to provide better code readability.

    Example:
        ```python
        from discord.utils import utcnow
        from tidegear.utils import TimestampStyle, format_datetime

        datetime = utcnow()
        print(format_datetime(dt=datetime, style=TimestampStyle.LONG_DATE_AND_TIME))
        ```

    Args:
        dt: The datetime to convert into a Discord timestamp.
        style: The timestamp style to apply.

    Returns:
        A string like `<t:1618924800:f>` that Discord will render according to the given style.
    """
    return f"<t:{int(dt.timestamp())}:{style}>"


async def send_error(
    messeagable: commands.Context | discord.abc.Messageable,
    /,
    content: str | None = None,
    func: Callable[[str], str] = cf.error,
    **kwargs: Any,
) -> discord.Message:
    """Send a message with the content wrapped in an error function.

    Args:
        messeagable: The channel or context to send the message to.
        content: The content of the message.
        func: The function to use to wrap the message.
        **kwargs: Additional keyword arguments to pass to `await messeagable.send()`.

    Returns:
        The sent message.
    """
    if content:
        content = func(content)
    return await messeagable.send(content=content, **kwargs)


def truncate_string(string: str, max_length: int) -> str:
    """Truncate a string to a maximum length, preserving whole words when possible.

    If the string exceeds `max_length`, it will be cut off at the last full word that fits, and "..." will be appended to indicate truncation.
    The resulting string will not exceed `max_length` characters.

    Args:
        string: The string to truncate.
        max_length: The maximum allowed length of the returned string. Must be >= 4.

    Raises:
        ValueError: If `max_length` is less than 4, since the ellipsis itself requires 3 characters.

    Returns:
        The truncated string with "..." appended if truncation occurred, or the original string if it fits within `max_length`.
    """
    min_max_length = 4
    if max_length < min_max_length:
        msg = f"max_length must be {min_max_length} or higher!"
        raise ValueError(msg)

    if len(string) <= max_length:
        return string

    truncated = string[: max_length - 3]

    last_space = truncated.rfind(" ")
    if last_space != -1:
        truncated = truncated[:last_space]

    return truncated + "..."
