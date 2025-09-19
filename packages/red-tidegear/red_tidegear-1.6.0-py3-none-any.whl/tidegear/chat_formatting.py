"""Wrapper around [`redbot.core.utils.chat_formatting`][] that overrides a couple functions to use Tidegear constants."""

from redbot.core.utils.chat_formatting import *  # noqa: F403  # pyright: ignore[reportWildcardImportFromLibrary]

from tidegear.constants import FALSE, INFO, NONE, TRUE, WARNING


def success(text: str) -> str:
    """Wrap a string in a success emoji.

    Args:
        text: The text to wrap.

    Returns:
        The wrapped text, prefixed with the [success constant][tidegear.constants.TRUE].
    """
    return f"{TRUE} {text}"


def error(text: str) -> str:
    """Wrap a string in an error emoji.

    Args:
        text: The text to wrap.

    Returns:
        The wrapped text, prefixed with the [error constant][tidegear.constants.FALSE].
    """
    return f"{FALSE} {text}"


def warning(text: str) -> str:
    """Wrap a string in a warning emoji.

    Args:
        text: The text to wrap.

    Returns:
        The wrapped text, prefixed with the [warning constant][tidegear.constants.WARNING].
    """
    return f"{WARNING} {text}"


def question(text: str) -> str:
    """Wrap a string in a question emoji.

    Args:
        text: The text to wrap.

    Returns:
        The wrapped text, prefixed with the [question constant][tidegear.constants.NONE].
    """
    return f"{NONE} {text}"


def info(text: str) -> str:
    """Wrap a string in an information emoji.

    Args:
        text: The text to wrap.

    Returns:
        The wrapped text, prefixed with the [info constant][tidegear.constants.INFO].
    """
    return f"{INFO} {text}"
