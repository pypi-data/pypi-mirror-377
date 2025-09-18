# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""This module contains exceptions used within Sentinel and consuming cogs."""

from typing import Any


class HandlerError(Exception):
    """Raised whenever a moderation handler wants to show an error message to the end user.

    Attributes:
        message: An error message. Will be shown to end users.
        send_error_kwargs: Additional keyword arguments to pass to [`send_error()`][tidegear.utils.send_error]. Does not support `content`.
    """

    message: str
    send_error_kwargs: dict[str, Any]

    def __init__(self, message: str, **send_error_kwargs: Any) -> None:
        super().__init__(message)
        self.send_error_kwargs = send_error_kwargs
        self.send_error_kwargs.pop("content", None)


class LoggedHandlerError(Exception):
    """Raised whenever a moderation handler wants to show an error message to the end user, while still logging that error for bot owners to see.

    Attributes:
        message: An error message. Will be shown to end users.
        send_error_kwargs: Additional keyword arguments to pass to [`send_error()`][tidegear.utils.send_error]. Does not support `content`.
    """

    message: str
    send_error_kwargs: dict[str, Any]

    def __init__(self, message: str, **send_error_kwargs: Any) -> None:
        super().__init__(message)
        self.send_error_kwargs = send_error_kwargs
        self.send_error_kwargs.pop("content", None)
