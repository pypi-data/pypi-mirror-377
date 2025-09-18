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

import pyrogram

from pyrogram import raw, types, utils
from ..object import Object



class GiveawayWinners(Object):
    """This object represents a message about the completion of a giveaway with public winners.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            The chat that created the giveaway

        giveaway_message_id (``int``):
            Identifier of the message with the giveaway in the chat

        winners_selection_date (:py:obj:`~datetime.datetime`):
            Point in time (Unix timestamp) when winners of the giveaway were selected
        
        winner_count (``int``):
            Total number of winners in the giveaway

        winners (:obj:`~pyrogram.types.User`):
            List of up to 100 winners of the giveaway
        
        additional_chat_count (``int``, *optional*):
            The number of other chats the user had to join in order to be eligible for the giveaway

        prize_star_count (``int``, *optional*):
            The number of Telegram Stars to be split between giveaway winners; for Telegram Star giveaways only

        premium_subscription_month_count (``int``, *optional*):
            The number of months the Telegram Premium subscription won from the giveaway will be active for

        unclaimed_prize_count (``int``, *optional*):
            Number of undistributed prizes

        only_new_members (``bool``, *optional*):
            True, if only users who had joined the chats after the giveaway started were eligible to win
        
        was_refunded (``bool``, *optional*):
            True, if the giveaway was canceled because the payment for it was refunded
        
        prize_description (``str``, *optional*):
            Description of additional giveaway prize

    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        chat: "types.Chat",
        giveaway_message_id: int,
        winners_selection_date: datetime,
        winner_count: int,
        winners: list["types.User"],
        additional_chat_count: int = None,
        prize_star_count: int = None,
        premium_subscription_month_count: int = None,
        unclaimed_prize_count: int = None,
        only_new_members: bool = None,
        was_refunded: bool = None,
        prize_description: str = None
    ):
        super().__init__(client)

        self.chat = chat
        self.giveaway_message_id = giveaway_message_id
        self.winners_selection_date = winners_selection_date
        self.winner_count = winner_count
        self.winners = winners
        self.additional_chat_count = additional_chat_count
        self.prize_star_count = prize_star_count
        self.premium_subscription_month_count = premium_subscription_month_count
        self.unclaimed_prize_count = unclaimed_prize_count
        self.only_new_members = only_new_members
        self.was_refunded = was_refunded
        self.prize_description = prize_description

    @staticmethod
    def _parse(
        client,
        chats: dict,
        users: dict,
        giveaway_media: "raw.types.MessageMediaGiveawayResults"
    ) -> "GiveawayWinners":
        if isinstance(giveaway_media, raw.types.MessageMediaGiveawayResults):
            return GiveawayWinners(
                client=client,
                chat=types.Chat._parse_channel_chat(
                    client, chats.get(giveaway_media.channel_id)
                ),
                giveaway_message_id=giveaway_media.launch_msg_id,
                winners_selection_date=utils.timestamp_to_datetime(giveaway_media.until_date),
                winner_count=giveaway_media.winners_count,
                winners=types.List(
                    types.User._parse(
                        client,
                        users.get(user_id)
                    )
                    for user_id in giveaway_media.winners
                ),
                additional_chat_count=getattr(giveaway_media, "additional_peers_count", None),
                prize_star_count=giveaway_media.stars,
                premium_subscription_month_count=giveaway_media.months,
                unclaimed_prize_count=getattr(giveaway_media, "unclaimed_count", None),
                only_new_members=getattr(giveaway_media, "only_new_subscribers", None),
                was_refunded=getattr(giveaway_media, "refunded", None),
                prize_description=getattr(giveaway_media, "prize_description", None)   
            )
