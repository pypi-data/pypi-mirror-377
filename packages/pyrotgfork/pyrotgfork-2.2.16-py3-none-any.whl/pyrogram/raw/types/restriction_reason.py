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


class RestrictionReason(TLObject):  # type: ignore
    """Restriction reason.
Contains the reason why access to a certain object must be restricted. Clients are supposed to deny access to the channel if the platform field is equal to all or to the current platform (ios, android, wp, etc.). Platforms can be concatenated (ios-android, ios-wp), unknown platforms are to be ignored. The text is the error message that should be shown to the user.
The restriction_add_platforms  client configuration parameter contains an array of platform identifiers that must also be treated as our own, in additional to the one hardcoded in the client.



    Constructor of :obj:`~pyrogram.raw.base.RestrictionReason`.

    Details:
        - Layer: ``214``
        - ID: ``D072ACB4``

    Parameters:
        platform (``str``):
            Platform identifier (ios, android, wp, all, etc.), can be concatenated with a dash as separator (android-ios, ios-wp, etc)

        reason (``str``):
            Restriction reason (porno, terms, etc.). Ignore this restriction reason if it is contained in the ignore_restriction_reasons » client configuration parameter.

        text (``str``):
            Error message to be shown to the user

    """

    __slots__: list[str] = ["platform", "reason", "text"]

    ID = 0xd072acb4
    QUALNAME = "types.RestrictionReason"

    def __init__(self, *, platform: str, reason: str, text: str) -> None:
        self.platform = platform  # string
        self.reason = reason  # string
        self.text = text  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "RestrictionReason":
        # No flags
        
        platform = String.read(b)
        
        reason = String.read(b)
        
        text = String.read(b)
        
        return RestrictionReason(platform=platform, reason=reason, text=text)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.platform))
        
        b.write(String(self.reason))
        
        b.write(String(self.text))
        
        return b.getvalue()
