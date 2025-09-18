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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types, utils, enums
from ..object import Object
from ..messages_and_media.message import Str


class TextQuote(Object):
    """This object contains information about the quoted part of a message that is replied to by the given message.

    Parameters:
        text (``str``):
            Text of the quoted part of a message that is replied to by the given message

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Special entities that appear in the quote. Currently, only bold, italic, underline, strikethrough, spoiler, and custom_emoji entities are kept in quotes.

        position (``int``):
            Approximate quote position in the original message in UTF-16 code units as specified by the sender

        is_manual  (``bool``, *optional*):
            True, if the quote was chosen manually by the message sender. Otherwise, the quote was added automatically by the server.

    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        text: Str = None,
        entities: list["types.MessageEntity"] = None,
        position: int = None,
        is_manual: bool = None
    ):
        super().__init__(client)

        self.text = text
        self.entities = entities
        self.position = position
        self.is_manual = is_manual

    @staticmethod
    def _parse(
        client,
        chats: dict,
        users: dict,
        reply_to: "raw.types.MessageReplyHeader"
    ) -> "TextQuote":
        if isinstance(reply_to, raw.types.MessageReplyHeader):
            if not reply_to.quote:
                return None
            quote_text = reply_to.quote_text
            quote_entities = reply_to.quote_entities
            position = reply_to.quote_offset or 0

            entities = [
                types.MessageEntity._parse(client, entity, users)
                for entity in quote_entities
            ]
            entities = types.List(
                filter(lambda x: x is not None, entities)
            )
            
            return TextQuote(
                text=Str(quote_text).init(entities) or None,
                entities=entities,
                position=position,
                is_manual=bool(reply_to.quote) or None
            )
