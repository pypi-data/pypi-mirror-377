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

from typing import Union

import pyrogram
from pyrogram import raw, utils, types, enums

from ..object import Object


class InputPollOption(Object):
    """This object contains information about one answer option in a poll to send.

    Parameters:
        text (``str``):
            Option text, 1-100 characters after entity parsing.

        text_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.
            Currently, only custom emoji entities are allowed to be added and only by Upgraded bots OR Premium users.

        text_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            List of special entities that appear in the poll option text, which can be specified instead of *text_parse_mode*.

    """

    def __init__(
        self,
        *,
        text: str,
        text_parse_mode: "enums.ParseMode" = None,
        text_entities: list["types.MessageEntity"] = None,
    ):
        super().__init__()

        self.text = text
        self.text_parse_mode = text_parse_mode
        self.text_entities = text_entities
