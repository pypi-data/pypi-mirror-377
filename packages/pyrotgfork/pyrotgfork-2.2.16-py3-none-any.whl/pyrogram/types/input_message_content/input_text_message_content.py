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
from typing import Optional

import pyrogram
from pyrogram import raw, types, utils, enums
from .input_message_content import InputMessageContent

log = logging.getLogger(__name__)


class InputTextMessageContent(InputMessageContent):
    """Content of a text message to be sent as the result of an inline query.

    Parameters:
        message_text (``str``):
            Text of the message to be sent, 1-4096 characters.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in message text, which can be specified instead of *parse_mode*.

        link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
            Link preview generation options for the message
    """

    def __init__(
        self,
        message_text: str,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: list["types.MessageEntity"] = None,
        link_preview_options: "types.LinkPreviewOptions" = None,
        disable_web_page_preview: bool = None
    ):
        if disable_web_page_preview and link_preview_options:
            raise ValueError(
                "Parameters `disable_web_page_preview` and `link_preview_options` are mutually "
                "exclusive."
            )

        if disable_web_page_preview is not None:
            log.warning(
                "This property is deprecated. "
                "Please use link_preview_options instead"
            )
            link_preview_options = types.LinkPreviewOptions(is_disabled=disable_web_page_preview)

        super().__init__()

        self.message_text = message_text
        self.parse_mode = parse_mode
        self.entities = entities
        self.link_preview_options = link_preview_options

    async def write(self, client: "pyrogram.Client", reply_markup):
        message, entities = (await utils.parse_text_entities(
            client,
            self.message_text,
            # TODO
            self.parse_mode,
            self.entities
        )).values()

        if self.link_preview_options is None:
            self.link_preview_options = client.link_preview_options

        return raw.types.InputBotInlineMessageText(
            no_webpage=self.link_preview_options.is_disabled if self.link_preview_options else None,
            invert_media=self.link_preview_options.show_above_text if self.link_preview_options else None,
            reply_markup=await reply_markup.write(client) if reply_markup else None,
            message=message,
            entities=entities
        )
