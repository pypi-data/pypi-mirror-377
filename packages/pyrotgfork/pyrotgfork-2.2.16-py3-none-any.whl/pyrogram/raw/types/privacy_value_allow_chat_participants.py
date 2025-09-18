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

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class PrivacyValueAllowChatParticipants(TLObject):  # type: ignore
    """Allow all participants of certain chats




	 | title 

	 | megagroup 

	 | color 

	 | photo 

	 | username 

	 | usernames 

	 | has_geo 

	 | noforwards 

	 | emoji_status 

	 | has_link 

	 | slow_mode_enabled 

	 | scam 

	 | fake 

	 | gigagroup 

	 | forum 

	 | level 

	 | restricted 

	 | restriction_reason 

	 | join_to_send 

	 | join_request 

	 | is_verified 

	 | default_banned_rights 

	 | signature_profiles 

	 | autotranslation 




    Constructor of :obj:`~pyrogram.raw.base.PrivacyRule`.

    Details:
        - Layer: ``214``
        - ID: ``6B134E8E``

    Parameters:
        chats (List of ``int`` ``64-bit``):
            Allowed chat IDs (either a chat or a supergroup ID, verbatim the way it is received in the constructor (i.e. unlike with bot API IDs, here group and supergroup IDs should be treated in the same way)).

    """

    __slots__: list[str] = ["chats"]

    ID = 0x6b134e8e
    QUALNAME = "types.PrivacyValueAllowChatParticipants"

    def __init__(self, *, chats: list[int]) -> None:
        self.chats = chats  # Vector<long>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PrivacyValueAllowChatParticipants":
        # No flags
        
        chats = TLObject.read(b, Long)
        
        return PrivacyValueAllowChatParticipants(chats=chats)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.chats, Long))
        
        return b.getvalue()
