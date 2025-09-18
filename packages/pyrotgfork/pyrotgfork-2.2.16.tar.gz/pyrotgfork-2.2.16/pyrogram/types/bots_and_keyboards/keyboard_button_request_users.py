#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2021 Dan <https://github.com/delivrance>
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

from ..object import Object


class KeyboardButtonRequestUsers(Object):
    """This object defines the criteria used to request suitable users.
    The identifiers of the selected users will be shared with the bot when the corresponding button is pressed.
    `More about requesting users. <https://core.telegram.org/bots/features#chat-and-user-selection>`_

    Parameters:
        request_id (``int``):
            Signed 32-bit identifier of the request, which will be received back in the :obj:`~pyrogram.types.UsersShared` object. Must be unique within the message

        user_is_bot (``bool``, *optional*):
            Pass True to request bots, pass False to request regular users. If not specified, no additional restrictions are applied.

        user_is_premium (``bool``, *optional*):
            Pass True to request premium users, pass False to request non-premium users. If not specified, no additional restrictions are applied.

        max_quantity (``int``, *optional*):
            The maximum number of users to be selected; 1-10. Defaults to 1.

        request_name (``bool``, *optional*):
            Pass True to request the users' first and last name

        request_username (``bool``, *optional*):
            Pass True to request the users' username

        request_photo (``bool``, *optional*):
            Pass True to request the users' photo

    """
    def __init__(
        self,
        request_id: int,
        user_is_bot: bool = None,
        user_is_premium: bool = None,
        max_quantity: int = 1,
        request_name: bool = None,
        request_username: bool = None,
        request_photo: bool = None
    ):
        self.request_id = request_id
        self.user_is_bot = user_is_bot
        self.user_is_premium = user_is_premium
        self.max_quantity = max_quantity
        self.request_name = request_name
        self.request_username = request_username
        self.request_photo = request_photo
