# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""This module contains exceptions used within Sentinel and consuming cogs."""

from tidegear.exceptions import TidegearError


class HandlerError(TidegearError):
    """Raised whenever a moderation handler wants to show an error message to the end user."""


class LoggedHandlerError(TidegearError):
    """Raised whenever a moderation handler wants to show an error message to the end user, while still logging that error for bot owners to see."""


class UpsertError(TidegearError):
    """Raised whenever an upsert operation falis."""
