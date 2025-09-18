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


class UpdateUser(TLObject):  # type: ignore
    """User (user and/or userFull) information was updated.
This update can only be received through getDifference or in updates/updatesCombined constructors, so it will always come bundled with the updated user, that should be applied as usual , without re-fetching the info manually.
However, full peer information will not come bundled in updates, so the full peer cache (userFull) must be invalidated for user_id when receiving this update.



    Constructor of :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``214``
        - ID: ``20529438``

    Parameters:
        user_id (``int`` ``64-bit``):
            User ID

    """

    __slots__: list[str] = ["user_id"]

    ID = 0x20529438
    QUALNAME = "types.UpdateUser"

    def __init__(self, *, user_id: int) -> None:
        self.user_id = user_id  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateUser":
        # No flags
        
        user_id = Long.read(b)
        
        return UpdateUser(user_id=user_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.user_id))
        
        return b.getvalue()
