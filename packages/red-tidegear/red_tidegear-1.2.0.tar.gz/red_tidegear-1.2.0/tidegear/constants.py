"""This module contains constants related to the Discord API or general cog development."""

from redbot.core.commands.context import TICK

MAX_MESSAGE_CHARACTERS: int = 2000
"""The maximum amount of characters Discord will allow you to post in a single message when using the `content` field."""
MAX_EMBED_CHARACTERS: int = 4096
"""The maximum amount of characters Discord will allow you to post in a single message when using embeds or components."""
ALLOWED_EMOJI_EXTENSIONS: set[str] = {"PNG", "WEBP", "JPEG", "JPG", "GIF", "AVIF"}
"""The file extensions accepted by Discord for use in custom emojis."""

TRUE: str = TICK
"""The emoji used for [`ctx.tick()`][redbot.core.commands.Context.tick] calls, and for truthy values in [`tidegear.utils.get_bool_emoji`][].
Corresponds to `redbot.core.commands.context.Tick`.
"""
FALSE: str = "\N{NO ENTRY SIGN}"
"""The emoji used for falsy values in [`tidegear.utils.get_bool_emoji`][]."""
NONE: str = "\N{BLACK QUESTION MARK ORNAMENT}\N{VARIATION SELECTOR-16}"
"""The emoji used for NoneType values in [`tidegear.utils.get_bool_emoji`][]."""
