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

from datetime import datetime
from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw, utils


class SearchMessagesCount:
    async def search_messages_count(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        query: str = "",
        filter: "enums.MessagesFilter" = enums.MessagesFilter.EMPTY,
        from_user: Union[int, str] = None,
        message_thread_id: int = None,
        min_date: datetime = utils.zero_datetime(),
        max_date: datetime = utils.zero_datetime(),
        min_id: int = 0,
        max_id: int = 0,
        saved_messages_topic_id: Optional[Union[int, str]] = None
    ) -> int:
        """Get the count of messages resulting from a search inside a chat.

        If you want to get the actual messages, see :meth:`~pyrogram.Client.search_messages`.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            query (``str``, *optional*):
                Text query string.
                Required for text-only messages, optional for media messages (see the ``filter`` argument).
                When passed while searching for media messages, the query will be applied to captions.
                Defaults to "" (empty string).

            filter (:obj:`~pyrogram.enums.MessagesFilter`, *optional*):
                Pass a filter in order to search for specific kind of messages only:

            from_user (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target user you want to search for messages from.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum; for forum supergroups only

            min_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date as offset to retrieve only older messages starting from that date.
            
            max_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date as offset to retrieve only newer messages starting from that date.
            
            min_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages with IDs more than min_id.
            
            max_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages with IDs less than max_id.      

            saved_messages_topic_id (``int`` | ``str``, *optional*):
                If not None, only messages in the specified Saved Messages topic will be returned; pass None to return all messages, or for chats other than Saved Messages.

        Returns:
            ``int``: On success, the messages count is returned.

        """
        r = await self.invoke(
            raw.functions.messages.Search(
                peer=await self.resolve_peer(chat_id),
                q=query,
                filter=filter.value(),
                min_date=utils.datetime_to_timestamp(min_date),
                max_date= utils.datetime_to_timestamp(max_date),
                offset_id=0,
                add_offset=0,
                limit=1,
                min_id=min_id,
                max_id=max_id,
                from_id=(
                    await self.resolve_peer(from_user)
                    if from_user
                    else None
                ),
                hash=0,
                top_msg_id=message_thread_id,
                saved_peer_id=await self.resolve_peer(saved_messages_topic_id) if saved_messages_topic_id else None
                # saved_reaction:flags.3?Vector<Reaction>
            )
        )

        if hasattr(r, "count"):
            return r.count
        else:
            return len(r.messages)
