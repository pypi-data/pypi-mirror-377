#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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

from datetime import datetime

from .message_origin import MessageOrigin

import pyrogram
from pyrogram import types, enums


class MessageOriginChat(MessageOrigin):
    """The message was originally sent on behalf of a chat to a group chat.

    Parameters:
        date (:py:obj:`~datetime.datetime`):
            Date the message was sent originally in Unix time

        sender_chat (:obj:`~pyrogram.types.Chat`):
            Chat that sent the message originally
        
        author_signature (``str``, *optional*):
            For messages originally sent by an anonymous chat administrator, original message author signature

    """

    def __init__(
        self,
        *,
        date: datetime = None,
        sender_chat: "types.Chat" = None,
        author_signature: str = None
    ):
        super().__init__(
            type=enums.MessageOriginType.CHAT,
            date=date
        )

        self.sender_chat = sender_chat
        self.author_signature = author_signature
