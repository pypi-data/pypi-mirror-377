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

import logging

import pyrogram
from pyrogram import raw
from pyrogram import types

log = logging.getLogger(__name__)


class GetStickers:
    async def get_stickers(
        self: "pyrogram.Client",
        short_name: str
    ) -> list["types.Sticker"]:
        """Get all stickers from set by short name.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str``):
                Short name of the sticker set, serves as the unique identifier for the sticker set.

        Returns:
            List of :obj:`~pyrogram.types.Sticker`: A list of stickers is returned.

        Example:
            .. code-block:: python

                # Get all stickers by short name
                await app.get_stickers("short_name")

        Raises:
            ValueError: In case of invalid arguments.
        """
        r, _ = await self._get_raw_stickers(
            raw.types.InputStickerSetShortName(
                short_name=short_name
            )
        )
        return r


    async def _get_raw_stickers(
        self: "pyrogram.Client",
        sticker_set: "raw.base.InputStickerSet"
    ) -> list["types.Sticker"]:
        """Internal Method.

        Parameters:
            sticker_set (:obj:`~pyrogram.raw.base.InputStickerSet`):

        Returns:
            List of :obj:`~pyrogram.types.Sticker`: A list of stickers is returned.

        Raises:
            ValueError: In case of invalid arguments.
        """
        sticker_set = await self.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=sticker_set,
                hash=0
            )
        )
        r = types.List([
            await types.Sticker._parse(
                self, doc, {type(a): a for a in doc.attributes}
            ) for doc in sticker_set.documents
        ])
        return r, sticker_set.set
