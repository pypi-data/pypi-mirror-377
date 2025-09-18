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

from pyrogram import raw, types, utils
from ..object import Object
from .message import Str


class GiftCode(Object):
    """Contains gift code data.

    Parameters:
        via_giveaway (``bool``):
            True if the gift code is received via giveaway.

        is_unclaimed (``bool``):
            True, if the winner for the corresponding Telegram Premium subscription wasn't chosen.
            `The code is received by creator of a chat, which started the giveaway that had less winners than planned. <https://telegram.org/tos/in#7-8-giveaways-in-channels>`_

        boosted_chat (:obj:`~pyrogram.types.Chat`):
            The channel where the gift code was won.

        premium_subscription_month_count (``int``):
            Number of months of subscription.

        slug (``str``):
            Identifier of gift code.
            You can combine it with `t.me/giftcode/{slug}`
            to get link for this gift.

        currency (``str``):
            Currency for the paid amount

        amount (``int``):
            The paid amount, in the smallest units of the currency

        cryptocurrency (``str``):
            Cryptocurrency used to pay for the gift; may be empty if none

        cryptocurrency_amount (``int``):
            The paid amount, in the smallest units of the cryptocurrency; 0 if none

        caption (``str``, *optional*):
            Text message chosen by the sender.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Entities of the text message.

        link (``str``, *property*):
            Generate a link to this gift code.
    """

    def __init__(
        self,
        *,
        via_giveaway: bool,
        is_unclaimed: bool,
        boosted_chat: "types.Chat",
        premium_subscription_month_count: int,
        slug: str,
        currency: str = None,
        amount: int = None,
        cryptocurrency: str = None,
        cryptocurrency_amount: int = None,
        caption: Str = None,
        caption_entities: list["types.MessageEntity"] = None
    ):
        super().__init__()

        self.via_giveaway = via_giveaway
        self.is_unclaimed = is_unclaimed
        self.boosted_chat = boosted_chat
        self.premium_subscription_month_count = premium_subscription_month_count
        self.slug = slug
        self.currency = currency
        self.amount = amount
        self.cryptocurrency = cryptocurrency
        self.cryptocurrency_amount = cryptocurrency_amount
        self.caption = caption
        self.caption_entities = caption_entities

    @staticmethod
    def _parse(
        client,
        giftcode: "raw.types.MessageActionGiftCode",
        chats: dict
    ):
        peer = chats.get(
            utils.get_raw_peer_id(giftcode.boost_peer)
        )

        caption = None
        caption_entities = []
        if giftcode.message:
            caption_entities = [
                types.MessageEntity._parse(client, entity, {})
                for entity in giftcode.message.entities
            ]
            caption_entities = types.List(filter(lambda x: x is not None, caption_entities))
            caption = Str(giftcode.message.text).init(caption_entities) or None

        return GiftCode(
            via_giveaway=giftcode.via_giveaway,
            is_unclaimed=giftcode.unclaimed,
            boosted_chat=types.Chat._parse_chat(
                client, peer
            ) if peer else None,
            premium_subscription_month_count=giftcode.months,
            slug=giftcode.slug,
            currency=giftcode.currency,
            amount=giftcode.amount,
            cryptocurrency=getattr(giftcode, "crypto_currency", None),
            cryptocurrency_amount=getattr(giftcode, "crypto_amount", None),
            caption=caption,
            caption_entities=caption_entities
        )

    @property
    def link(self) -> str:
        return f"https://t.me/giftcode/{self.slug}"
