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
from pyrogram import raw, types, enums, utils


class SendGift:
    async def send_gift(
        self: "pyrogram.Client",
        *,
        user_id: Union[int, str] = None,
        chat_id: Union[int, str] = None,
        gift_id: int = None,
        pay_for_upgrade: Optional[bool] = None,
        text: Optional[str] = None,
        text_parse_mode: Optional["enums.ParseMode"] = None,
        text_entities: Optional[list["types.MessageEntity"]] = None,
        is_private: Optional[bool] = None,
    ) -> bool:
        """Sends a gift to the given user or channel chat. The gift can't be converted to Telegram Stars by the receiver.

        .. include:: /_includes/usable-by/users-bots.rst

        You must use exactly one of ``user_id`` OR ``chat_id``.

        Parameters:
            user_id (``int`` | ``str``):
                Required if ``chat_id`` is not specified.
                Unique identifier (int) or username (str) of the target user that will receive the gift.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            chat_id (``int`` | ``str``):
                Required if ``user_id`` is not specified.
                Unique identifier (int) or username (str) for the chat or username of the channel that will receive the gift.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            gift_id (``int``):
                Identifier of the gift.

            pay_for_upgrade (``bool``, *optional*):
                Pass True to pay for the gift upgrade from the sender's balance, thereby making the upgrade free for the receiver.

            text (``str``, *optional*):
                Text that will be shown along with the gift. 0-``gift_text_length_max`` characters.

            text_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            text_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be specified instead of *text_parse_mode*.
                Only Bold, Italic, Underline, Strikethrough, Spoiler, and CustomEmoji entities are allowed.

            is_private (``bool``, *optional*):
                For users only: Pass True to show the current user as sender and gift text only to the gift receiver; otherwise, everyone will be able to see them.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.

        Example:
            .. code-block:: python

                # Send gift
                app.send_gift(user_id=user_id, gift_id=123)

        """
        peer = None
        if user_id:
            peer = await self.resolve_peer(user_id)
        elif chat_id:
            peer = await self.resolve_peer(chat_id)
        # TODO
        if not peer:
            raise ValueError("You must use exactly one of user_id OR chat_id")
        text, entities = (await utils.parse_text_entities(self, text, text_parse_mode, text_entities)).values()

        invoice = raw.types.InputInvoiceStarGift(
            user_id=peer,
            gift_id=gift_id,
            hide_name=is_private,
            include_upgrade=pay_for_upgrade,
            message=raw.types.TextWithEntities(
                text=text, entities=entities or []
            ) if text else None
        )

        form = await self.invoke(
            raw.functions.payments.GetPaymentForm(
                invoice=invoice
            )
        )

        await self.invoke(
            raw.functions.payments.SendStarsForm(
                form_id=form.form_id,
                invoice=invoice
            )
        )

        return True
