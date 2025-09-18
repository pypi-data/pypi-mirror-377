#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import re
from typing import Any, Callable, Literal, Optional, Pattern, Union

import pyrogram
from pyrogram import enums
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChosenInlineResult,
    InlineQuery,
    InlineKeyboardMarkup,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
    Update,
)
from pyrogram.types.messages_and_media.message import Str


class Filter:
    async def __call__(self, client: "pyrogram.Client", update: Update) -> None:
        raise NotImplementedError

    def __invert__(self) -> "InvertFilter":
        return InvertFilter(self)

    def __and__(self, other) -> "AndFilter":
        return AndFilter(self, other)

    def __or__(self, other) -> "OrFilter":
        return OrFilter(self, other)


class InvertFilter(Filter):
    def __init__(self, base) -> None:
        self.base: Any = base

    async def __call__(self, client: "pyrogram.Client", update: Update) -> bool:
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor, self.base, client, update
            )

        return not x


class AndFilter(Filter):
    def __init__(self, base, other) -> None:
        self.base = base
        self.other = other

    async def __call__(
        self, client: "pyrogram.Client", update: Update
    ) -> Union[Any, Literal[False]]:
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor, self.base, client, update
            )

        # short circuit
        if not x:
            return False

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor, self.other, client, update
            )

        return x and y


class OrFilter(Filter):
    def __init__(self, base, other) -> None:
        self.base = base
        self.other = other

    async def __call__(
        self, client: "pyrogram.Client", update: Update
    ) -> Union[Any, Literal[True]]:
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor, self.base, client, update
            )

        # short circuit
        if x:
            return True

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor, self.other, client, update
            )

        return x or y


CUSTOM_FILTER_NAME = "CustomFilter"


def create(func: Callable, name: str = None, **kwargs) -> Filter:
    """Easily create a custom filter.

    Custom filters give you extra control over which updates are allowed or not to be processed by your handlers.

    Parameters:
        func (``Callable``):
            A function that accepts three positional arguments *(filter, client, update)* and returns a boolean: True if the
            update should be handled, False otherwise.
            The *filter* argument refers to the filter itself and can be used to access keyword arguments (read below).
            The *client* argument refers to the :obj:`~pyrogram.Client` that received the update.
            The *update* argument type will vary depending on which `Handler <handlers>`_ is coming from.
            For example, in a :obj:`~pyrogram.handlers.MessageHandler` the *update* argument will be a :obj:`~pyrogram.types.Message`; in a :obj:`~pyrogram.handlers.CallbackQueryHandler` the *update* will be a :obj:`~pyrogram.types.CallbackQuery`; in a :obj:`~pyrogram.handlers.RawUpdateHandler` the *update* will be a :obj:`~pyrogram.raw.base.Update`.
            Your function body can then access the incoming update attributes and decide whether to allow it or not.

        name (``str``, *optional*):
            Your filter's name. Can be anything you like.
            Defaults to "CustomFilter".

        **kwargs (``any``, *optional*):
            Any keyword argument you would like to pass. Useful when creating parameterized custom filters, such as
            :meth:`~pyrogram.filters.command` or :meth:`~pyrogram.filters.regex`.

    """
    return type(
        name or func.__name__ or CUSTOM_FILTER_NAME,
        (Filter,),
        {"__call__": func, **kwargs},
    )()


# region all_filter
async def all_filter(_, __, ___) -> Literal[True]:
    return True


all = create(all_filter)
"""Filter all messages."""


# endregion


# region me_filter
async def me_filter(_, __, m: Message) -> bool:
    return bool(m.from_user and m.from_user.is_self or getattr(m, "outgoing", False))


me: Filter = create(me_filter)
"""Filter messages generated by you yourself."""


# endregion


# region bot_filter
async def bot_filter(_, __, m: Message) -> bool:
    return bool(m.from_user and m.from_user.is_bot)


bot = create(bot_filter)
"""Filter messages coming from bots."""


# endregion


# region incoming_filter
async def incoming_filter(_, __, m: Message) -> bool:
    return not m.outgoing


incoming: Filter = create(incoming_filter)
"""Filter incoming messages. Messages sent to your own chat (Saved Messages) are also recognised as incoming."""


# endregion


# region outgoing_filter
async def outgoing_filter(_, __, m: Message) -> bool:
    return m.outgoing


outgoing = create(outgoing_filter)
"""Filter outgoing messages. Messages sent to your own chat (Saved Messages) are not recognized as outgoing."""


# endregion


# region text_filter
async def text_filter(_, __, m: Message) -> bool:
    return bool(m.text)


text: Filter = create(text_filter)
"""Filter text messages."""


# endregion


# region reply_filter
async def reply_filter(_, __, m: Message) -> bool:
    return bool(m.reply_to_message_id)


reply = create(reply_filter)
"""Filter messages that are replies to other messages."""


# endregion


# region forwarded_filter
async def forwarded_filter(_, __, m: Message) -> bool:
    return bool(m.forward_origin)


forwarded = create(forwarded_filter)
"""Filter messages that are forwarded."""


# endregion


# region caption_filter
async def caption_filter(_, __, m: Message) -> bool:
    return bool(m.caption)


caption: Filter = create(caption_filter)
"""Filter media messages that contain captions."""


# endregion


# region audio_filter
async def audio_filter(_, __, m: Message) -> bool:
    return bool(m.audio)


audio: Filter = create(audio_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Audio` objects."""


# endregion


# region document_filter
async def document_filter(_, __, m: Message) -> bool:
    return bool(m.document)


document = create(document_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Document` objects."""


# endregion


# region photo_filter
async def photo_filter(_, __, m: Message) -> bool:
    return bool(m.photo)


photo: Filter = create(photo_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Photo` objects."""


# endregion


# region sticker_filter
async def sticker_filter(_, __, m: Message) -> bool:
    return bool(m.sticker)


sticker: Filter = create(sticker_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Sticker` objects."""


# endregion


# region animation_filter
async def animation_filter(_, __, m: Message) -> bool:
    return bool(m.animation)


animation: Filter = create(animation_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Animation` objects."""


# endregion


# region game_filter
async def game_filter(_, __, m: Message) -> bool:
    return bool(m.game)


game: Filter = create(game_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Game` objects."""


# endregion

# region giveaway_filter
async def giveaway_filter(_, __, m: Message):
    return bool(m.giveaway)


giveaway = create(giveaway_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Giveaway` objects."""


# endregion

# region giveaway_result_filter
async def giveaway_result_filter(_, __, m: Message):
    return bool(m.giveaway_winners or m.giveaway_completed)


giveaway_result = create(giveaway_result_filter)
"""Filter messages that contain :obj:`~pyrogram.types.GiveawayWinners` or :obj:`~pyrogram.types.GiveawayCompleted` objects."""


# endregion

# region gift_code_filter
async def gift_code_filter(_, __, m: Message):
    return bool(m.gift_code)


gift_code = create(gift_code_filter)
"""Filter messages that contain :obj:`~pyrogram.types.GiftCode` objects."""


# endregion

# region received_gift
async def received_gift_filter(_, __, m: Message):
    return bool(m.received_gift)


received_gift = create(received_gift_filter)
"""Filter messages that contain :obj:`~pyrogram.types.ReceivedGift` objects."""


# endregion

# region video_filter
async def video_filter(_, __, m: Message) -> bool:
    return bool(m.video)


video: Filter = create(video_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Video` objects."""


# endregion


# region media_group_filter
async def media_group_filter(_, __, m: Message) -> bool:
    return bool(m.media_group_id)


media_group: Filter = create(media_group_filter)
"""Filter messages containing photos or videos being part of an album."""


# endregion


# region voice_filter
async def voice_filter(_, __, m: Message) -> bool:
    return bool(m.voice)


voice: Filter = create(voice_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Voice` note objects."""


# endregion


# region video_note_filter
async def video_note_filter(_, __, m: Message) -> bool:
    return bool(m.video_note)


video_note: Filter = create(video_note_filter)
"""Filter messages that contain :obj:`~pyrogram.types.VideoNote` objects."""


# endregion


# region contact_filter
async def contact_filter(_, __, m: Message) -> bool:
    return bool(m.contact)


contact: Filter = create(contact_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Contact` objects."""


# endregion


# region location_filter
async def location_filter(_, __, m: Message) -> bool:
    return bool(m.location)


location: Filter = create(location_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Location` objects."""


# endregion


# region venue_filter
async def venue_filter(_, __, m: Message) -> bool:
    return bool(m.venue)


venue: Filter = create(venue_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Venue` objects."""


# endregion


# region web_page_filter
async def web_page_filter(_, __, m: Message) -> bool:
    return bool(m.web_page)


web_page: Filter = create(web_page_filter)
"""Filter messages sent with a webpage preview."""


# endregion


# region poll_filter
async def poll_filter(_, __, m: Message) -> bool:
    return bool(m.poll)


poll: Filter = create(poll_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Poll` objects."""


# endregion


# region dice_filter
async def dice_filter(_, __, m: Message) -> bool:
    return bool(m.dice)


dice: Filter = create(dice_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Dice` objects."""


# endregion


# region media_spoiler
async def media_spoiler_filter(_, __, m: Message) -> bool:
    return bool(m.has_media_spoiler)


media_spoiler: Filter = create(media_spoiler_filter)
"""Filter media messages that contain a spoiler."""


# endregion


# region private_filter
async def private_filter(_, __, m: Union[Message, CallbackQuery]) -> bool:
    m = getattr(m, "message", None) if isinstance(m, CallbackQuery) else m
    if not m:
        raise ValueError(
            "filters.private is not supported here "
        )
    return bool(m.chat and m.chat.type in {enums.ChatType.PRIVATE, enums.ChatType.BOT})


private: Filter = create(private_filter)
"""Filter messages sent in private chats."""


# endregion


# region group_filter
async def group_filter(_, __, m: Union[Message, CallbackQuery]) -> bool:
    m = getattr(m, "message", None) if isinstance(m, CallbackQuery) else m
    if not m:
        raise ValueError(
            "filters.group is not supported here "
        )
    return bool(
        m.chat and m.chat.type in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP}
    )


group: Filter = create(group_filter)
"""Filter messages sent in group or supergroup chats."""


# endregion


# region channel_filter
async def channel_filter(_, __, m: Union[Message, CallbackQuery]) -> bool:
    m = getattr(m, "message", None) if isinstance(m, CallbackQuery) else m
    if not m:
        raise ValueError(
            "filters.channel is not supported here "
        )
    return bool(m.chat and m.chat.type == enums.ChatType.CHANNEL)


channel: Filter = create(channel_filter)
"""Filter messages sent in channels."""


# endregion


# region new_chat_members_filter
async def new_chat_members_filter(_, __, m: Message) -> bool:
    return bool(m.new_chat_members)


new_chat_members: Filter = create(new_chat_members_filter)
"""Filter service messages for new chat members."""


# endregion


# region left_chat_member_filter
async def left_chat_member_filter(_, __, m: Message) -> bool:
    return bool(m.left_chat_member)


left_chat_member: Filter = create(left_chat_member_filter)
"""Filter service messages for members that left the chat."""


# endregion


# region new_chat_title_filter
async def new_chat_title_filter(_, __, m: Message) -> bool:
    return bool(m.new_chat_title)


new_chat_title: Filter = create(new_chat_title_filter)
"""Filter service messages for new chat titles."""


# endregion


# region new_chat_photo_filter
async def new_chat_photo_filter(_, __, m: Message) -> bool:
    return bool(m.new_chat_photo)


new_chat_photo: Filter = create(new_chat_photo_filter)
"""Filter service messages for new chat photos."""


# endregion


# region delete_chat_photo_filter
async def delete_chat_photo_filter(_, __, m: Message) -> bool:
    return bool(m.delete_chat_photo)


delete_chat_photo: Filter = create(delete_chat_photo_filter)
"""Filter service messages for deleted photos."""


# endregion


# region group_chat_created_filter
async def group_chat_created_filter(_, __, m: Message) -> bool:
    return bool(m.group_chat_created)


group_chat_created: Filter = create(group_chat_created_filter)
"""Filter service messages for group chat creations."""


# endregion


# region supergroup_chat_created_filter
async def supergroup_chat_created_filter(_, __, m: Message) -> bool:
    return bool(m.supergroup_chat_created)


supergroup_chat_created: Filter = create(supergroup_chat_created_filter)
"""Filter service messages for supergroup chat creations."""


# endregion


# region channel_chat_created_filter
async def channel_chat_created_filter(_, __, m: Message) -> bool:
    return bool(m.channel_chat_created)


channel_chat_created: Filter = create(channel_chat_created_filter)
"""Filter service messages for channel chat creations."""


# endregion


# region migrate_to_chat_id_filter
async def migrate_to_chat_id_filter(_, __, m: Message) -> bool:
    return bool(m.migrate_to_chat_id)


migrate_to_chat_id: Filter = create(migrate_to_chat_id_filter)
"""Filter service messages that contain migrate_to_chat_id."""


# endregion


# region migrate_from_chat_id_filter
async def migrate_from_chat_id_filter(_, __, m: Message) -> bool:
    return bool(m.migrate_from_chat_id)


migrate_from_chat_id: Filter = create(migrate_from_chat_id_filter)
"""Filter service messages that contain migrate_from_chat_id."""


# endregion


# region pinned_message_filter
async def pinned_message_filter(_, __, m: Message) -> bool:
    return bool(m.pinned_message)


pinned_message: Filter = create(pinned_message_filter)
"""Filter service messages for pinned messages."""


# endregion


# region game_high_score_filter
async def game_high_score_filter(_, __, m: Message) -> bool:
    return bool(m.game_high_score)


game_high_score: Filter = create(game_high_score_filter)
"""Filter service messages for game high scores."""


# endregion


# region reply_keyboard_filter
async def reply_keyboard_filter(_, __, m: Message) -> bool:
    return isinstance(m.reply_markup, ReplyKeyboardMarkup)


reply_keyboard: Filter = create(reply_keyboard_filter)
"""Filter messages containing reply keyboard markups"""


# endregion


# region inline_keyboard_filter
async def inline_keyboard_filter(_, __, m: Message) -> bool:
    return isinstance(m.reply_markup, InlineKeyboardMarkup)


inline_keyboard: Filter = create(inline_keyboard_filter)
"""Filter messages containing inline keyboard markups"""


# endregion


# region mentioned_filter
async def mentioned_filter(_, __, m: Message) -> bool:
    return bool(m.mentioned)


mentioned: Filter = create(mentioned_filter)
"""Filter messages containing mentions"""


# endregion


# region via_bot_filter
def via_bot_filter(flt, *args):
    # https://t.me/c/1220993104/1379819
    if isinstance(args[0], pyrogram.Client):
        _, m, *__ = args
        return bool(m.via_bot) and (
            len(flt) == 0
            or (
                m.via_bot.id in flt or (
                    m.via_bot.username and m.via_bot.username.lower() in flt
                )
            )
        )
    bots = args[0] if isinstance(args[0], list) else [args[0]]
    flt = type(flt)(u.lower().lstrip("@") if isinstance(u, str) else u for u in bots)
    return flt

via_bot: Filter = type(
    via_bot_filter.__name__,
    (Filter, set),
    dict(__call__=via_bot_filter),
)()
"""Filter messages sent via inline bots

    Parameters:
        user_ids (``int`` | ``str`` | Iterable of ``int`` | Iterable of ``str``, *optional*):
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            For a contact that exists in your Telegram address book you can use his phone number (str).
            Defaults to None (all bots).
"""


# endregion


# region video_chat_started_filter
async def video_chat_started_filter(_, __, m: Message) -> bool:
    return bool(m.video_chat_started)


video_chat_started: Filter = create(video_chat_started_filter)
"""Filter messages for started video chats"""


# endregion


# region video_chat_ended_filter
async def video_chat_ended_filter(_, __, m: Message) -> bool:
    return bool(m.video_chat_ended)


video_chat_ended: Filter = create(video_chat_ended_filter)
"""Filter messages for ended video chats"""


# endregion


# region business message
async def tg_business_filter(_, __, m: Union[Message, list[Message]]):
    if (
        isinstance(m, list) and
        len(m) > 0
    ):
        return bool(m[0].business_connection_id)
    elif isinstance(m, Message):
        return bool(m.business_connection_id)


tg_business = create(tg_business_filter)
"""Filter non-service messages from a connected business account"""


# endregion

# region video_chat_participants_invited_filter
async def video_chat_participants_invited_filter(_, __, m: Message) -> bool:
    return bool(m.video_chat_participants_invited)


video_chat_participants_invited = create(video_chat_participants_invited_filter)
"""Filter messages for voice chat invited members"""


# endregion

# region successful_payment_filter
async def successful_payment_filter(_, __, m: Message):
    return bool(m.successful_payment)


successful_payment = create(successful_payment_filter)
"""Filter messages for successful payments"""


# endregion

# region service_filter
async def service_filter(_, __, m: Message) -> bool:
    return bool(m.service)


service: Filter = create(service_filter)
"""Filter service messages.

A service message contains any of the following fields set: *left_chat_member*,
*new_chat_title*, *new_chat_photo*, *delete_chat_photo*, *group_chat_created*, *supergroup_chat_created*,
*channel_chat_created*, *migrate_to_chat_id*, *migrate_from_chat_id*, *pinned_message*, *game_score*,
*video_chat_started*, *video_chat_ended*, *video_chat_participants_invited*, *successful_payment*.
"""


# endregion


# region media_filter
async def media_filter(_, __, m: Message) -> bool:
    return bool(m.media)


media: Filter = create(media_filter)
"""Filter media messages.

A media message contains any of the following fields set: *animation*, *audio*, *contact*, *dice*, *document*, *game*, *giveaway*, *giveaway_winners*, *location*, *photo*, *poll*, *sticker*, *story*, *venue*, *video*, *video_note*, *voice*, *web_page*.
"""


# endregion


# region scheduled_filter
async def scheduled_filter(_, __, m: Message) -> bool:
    return bool(m.scheduled)


scheduled: Filter = create(scheduled_filter)
"""Filter messages that have been scheduled (not yet sent)."""


# endregion


# region from_scheduled_filter
async def from_scheduled_filter(_, __, m: Message) -> bool:
    return bool(m.from_scheduled)


from_scheduled: Filter = create(from_scheduled_filter)
"""Filter new automatically sent messages that were previously scheduled."""


# endregion


# region linked_channel_filter
async def linked_channel_filter(_, __, m: Message) -> bool:
    return bool(
        m.forward_origin and
        m.forward_origin.type == enums.MessageOriginType.CHANNEL and
        m.forward_origin.chat == m.sender_chat
    )

linked_channel: Filter = create(linked_channel_filter)
"""Filter messages that are automatically forwarded from the linked channel to the group chat."""


# endregion


# region command_filter
def command(
    commands: Union[str, list[str]],
    prefixes: Union[str, list[str]] = "/",
    case_sensitive: bool = False,
) -> Filter:
    """Filter commands, i.e.: text messages starting with "/" or any other custom prefix.

    Parameters:
        commands (``str`` | ``list``):
            The command or list of commands as string the filter should look for.
            Examples: "start", ["start", "help", "settings"]. When a message text containing
            a command arrives, the command itself and its arguments will be stored in the *command*
            field of the :obj:`~pyrogram.types.Message`.

        prefixes (``str`` | ``list``, *optional*):
            A prefix or a list of prefixes as string the filter should look for.
            Defaults to "/" (slash). Examples: ".", "!", ["/", "!", "."], list(".:!").
            Pass None or "" (empty string) to allow commands with no prefix at all.

        case_sensitive (``bool``, *optional*):
            Pass True if you want your command(s) to be case sensitive. Defaults to False.
            Examples: when True, command="Start" would trigger /Start but not /start.
    """
    command_re: Pattern[str] = re.compile(pattern=r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: pyrogram.Client, message: Message) -> bool:
        username: str = (client.me and client.me.username) or ""
        text: Str = message.text or message.caption
        message.command = None

        if not text:
            return False

        for prefix in flt.prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix) :]

            for cmd in flt.commands:
                if not re.match(
                    pattern=rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)",
                    string=without_prefix,
                    flags=re.IGNORECASE if not flt.case_sensitive else 0,
                ):
                    continue

                without_command: str = re.sub(
                    pattern=rf"{cmd}(?:@?{username})?\s?",
                    repl="",
                    string=without_prefix,
                    count=1,
                    flags=re.IGNORECASE if not flt.case_sensitive else 0,
                )

                # match.groups are 1-indexed, group(1) is the quote, group(2) is the text
                # between the quotes, group(3) is unquoted, whitespace-split text

                # Remove the escape character from the arguments
                message.command = [cmd] + [
                    re.sub(
                        pattern=r"\\([\"'])",
                        repl=r"\1",
                        string=m.group(2) or m.group(3) or "",
                    )
                    for m in command_re.finditer(string=without_command)
                ]

                return True

        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return create(
        func=func,
        name="CommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive,
    )


# endregion


# region cq_data_filter
def cq_data(data: Union[str, list[str]]):
    """Filter callback query updates that match a given string or list of strings.

    Can be applied to handlers that receive :obj:`~pyrogram.types.CallbackQuery` updates.

    Parameters:
        data (``str`` | ``list[str]``):
            The data or list of data strings to match against the callback query.

    Returns:
        :obj:`callable`: A filter function that matches callback query updates based on the provided data.
    """

    async def func(_, __, callback_query: CallbackQuery):
        if isinstance(data, str):
            return callback_query.data == data
        elif isinstance(data, list):
            return callback_query.data in data
        else:
            return False
    return filters.create(func)


# endregion


# region regex_filter
def regex(pattern: Union[str, Pattern], flags: int = 0) -> Filter:
    """Filter updates that match a given regular expression pattern.

    Can be applied to handlers that receive one of the following updates:

    - :obj:`~pyrogram.types.Message`: The filter will match ``text`` or ``caption``.
    - :obj:`~pyrogram.types.CallbackQuery`: The filter will match ``data``.
    - :obj:`~pyrogram.types.ChosenInlineResult`: The filter will match ``query``.
    - :obj:`~pyrogram.types.InlineQuery`: The filter will match ``query``.
    - :obj:`~pyrogram.types.PreCheckoutQuery`: The filter will match ``payload``.

    When a pattern matches, all the `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_ are
    stored in the ``matches`` field of the update object itself.

    Parameters:
        pattern (``str`` | ``Pattern``):
            The regex pattern as string or as pre-compiled pattern.

        flags (``int``, *optional*):
            Regex flags.
    """

    async def func(flt, _, update: Update) -> bool:
        if isinstance(update, Message):
            value: Str = update.text or update.caption
        elif isinstance(update, CallbackQuery):
            value: str | bytes = update.data
        elif isinstance(update, (ChosenInlineResult, InlineQuery)):
            value: str = update.query
        elif isinstance(update, PreCheckoutQuery):
            value: str = update.invoice_payload
        else:
            raise ValueError(f"Regex filter doesn't work with {type(update)}")

        if value:
            update.matches = list(flt.p.finditer(value)) or None

        return bool(update.matches)

    return create(
        func=func,
        name="RegexFilter",
        p=pattern if isinstance(pattern, Pattern) else re.compile(pattern, flags),
    )


# endregion


# noinspection PyPep8Naming
class user(Filter, set):
    """Filter messages coming from one or more users.

    You can use `set bound methods <https://docs.python.org/3/library/stdtypes.html#set>`_ to manipulate the
    users container.

    Parameters:
        users (``int`` | ``str`` | ``list``):
            Pass one or more user ids/usernames to filter users.
            For you yourself, "me" or "self" can be used as well.
            Defaults to None (no users).
    """

    def __init__(self, users: Optional[Union[int, str, list[Union[int, str]]]] = None) -> None:
        users = [] if users is None else users if isinstance(users, list) else [users]

        super().__init__(
            (
                "me"
                if u in ["me", "self"]
                else u.lower().strip("@") if isinstance(u, str) else u
            )
            for u in users
        )

    async def __call__(self, _, message: Message) -> bool:
        return message.from_user and (
            message.from_user.id in self
            or (
                message.from_user.username
                and message.from_user.username.lower() in self
            )
            or ("me" in self and message.from_user.is_self)
        )


# noinspection PyPep8Naming
class chat(Filter, set):
    """Filter messages coming from one or more chats.

    You can use `set bound methods <https://docs.python.org/3/library/stdtypes.html#set>`_ to manipulate the
    chats container.

    Parameters:
        chats (``int`` | ``str`` | ``list``):
            Pass one or more chat ids/usernames to filter chats.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            Defaults to None (no chats).
    """

    def __init__(self, chats: Optional[Union[int, str, list[Union[int, str]]]] = None) -> None:
        chats = [] if chats is None else chats if isinstance(chats, list) else [chats]

        super().__init__(
            (
                "me"
                if c in ["me", "self"]
                else c.lower().strip("@") if isinstance(c, str) else c
            )
            for c in chats
        )

    async def __call__(self, _, message: Message) -> bool:
        return message.chat and (
            message.chat.id in self
            or (message.chat.username and message.chat.username.lower() in self)
            or (
                "me" in self
                and message.from_user
                and message.from_user.is_self
                and not message.outgoing
            )
        )


# region chat_shared filter

chat_shared: Filter = create(
    lambda _, __, m: (
        bool(m.chat_shared)
    )
)
"""Filter service messages for chat shared."""

# endregion


# region users_shared filter

users_shared: Filter = create(
    lambda _, __, m: (
        bool(m.users_shared)
    )
)
"""Filter service messages for chat shared."""

# endregion

# noinspection PyPep8Naming
class thread(Filter, set):
    """Filter messages coming from one or more threads.

    You can use `set bound methods <https://docs.python.org/3/library/stdtypes.html#set>`_ to manipulate the
    message_thread_ids container.

    Parameters:
        message_thread_ids (``int`` | ``list``):
            Pass one or more message thread ids to filter messages in specific threads.
            Defaults to None (no threads).
    """

    def __init__(self, message_thread_ids: Optional[Union[int, list[int]]] = None):
        message_thread_ids = [] if message_thread_ids is None else message_thread_ids if isinstance(message_thread_ids, list) else [message_thread_ids]

        super().__init__(
            t for t in message_thread_ids
        )

    async def __call__(self, _, message: Message):
        return message.message_thread_id and message.message_thread_id in self


# region self_destruct_filter

async def self_destruct_filter(_, __, m: Message):
    return bool(
        m.media and
        getattr(
            getattr(
                m,
                m.media.value,
                None
            ),
            "ttl_seconds",
            None
        )
    )


self_destruct = create(self_destruct_filter)
"""Filter self destruct media messages."""


# endregion
