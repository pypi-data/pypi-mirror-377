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
import os
import re
from datetime import datetime
from typing import Union

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import FileType
from .inline_session import get_session

log = logging.getLogger(__name__)


class SendMediaGroup:
    # TODO: Add progress parameter
    async def send_media_group(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        media: list[Union[
            "types.InputMediaPhoto",
            "types.InputMediaVideo",
            "types.InputMediaAudio",
            "types.InputMediaDocument"
        ]],
        disable_notification: bool = None,
        reply_parameters: "types.ReplyParameters" = None,
        message_thread_id: int = None,
        business_connection_id: str = None,
        send_as: Union[int, str] = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        allow_paid_broadcast: bool = None,
        paid_message_star_count: int = None,
        message_effect_id: int = None,
        reply_to_message_id: int = None
    ) -> list["types.Message"]:
        """Send a group of photos or videos as an album.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            media (List of :obj:`~pyrogram.types.InputMediaPhoto`, :obj:`~pyrogram.types.InputMediaVideo`, :obj:`~pyrogram.types.InputMediaAudio` and :obj:`~pyrogram.types.InputMediaDocument`):
                A list describing photos and videos to be sent, must include 2–10 items.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Description of the message to reply to

            message_thread_id (``int``, *optional*):
                If the message is in a thread, ID of the original message.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            send_as (``int`` | ``str``):
                Unique identifier (int) or username (str) of the chat or channel to send the message as.
                You can use this to send the message on behalf of a chat or channel where you have appropriate permissions.
                Use the :meth:`~pyrogram.Client.get_send_as_chats` to return the list of message sender identifiers, which can be used to send messages in the chat, 
                This setting applies to the current message and will remain effective for future messages unless explicitly changed.
                To set this behavior permanently for all messages, use :meth:`~pyrogram.Client.set_send_as_chat`.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Pass True if the content of the message must be protected from forwarding and saving; for bots only.

            allow_paid_broadcast (``bool``, *optional*):
                Pass True to allow the message to ignore regular broadcast limits for a small fee; for bots only

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            message_effect_id (``int`` ``64-bit``, *optional*):
                Unique identifier of the message effect to be added to the message; for private chats only.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of the sent messages is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto, InputMediaVideo

                await app.send_media_group(
                    "me",
                    [
                        InputMediaPhoto("photo1.jpg"),
                        InputMediaPhoto("photo2.jpg", caption="photo caption"),
                        InputMediaVideo("video.mp4", caption="video caption")
                    ]
                )
        """

        if reply_to_message_id and reply_parameters:
            raise ValueError(
                "Parameters `reply_to_message_id` and `reply_parameters` are mutually "
                "exclusive."
            )
        
        if reply_to_message_id is not None:
            log.warning(
                "This property is deprecated. "
                "Please use reply_parameters instead"
            )
            reply_parameters = types.ReplyParameters(message_id=reply_to_message_id)

        show_caption_above_media = []
        multi_media = []

        for i in media:
            if isinstance(i, types.InputMediaPhoto):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedPhoto(
                                    file=await self.save_file(i.media),
                                    spoiler=i.has_spoiler
                                )
                            )
                        )

                        media = raw.types.InputMediaPhoto(
                            id=raw.types.InputPhoto(
                                id=media.photo.id,
                                access_hash=media.photo.access_hash,
                                file_reference=media.photo.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaPhotoExternal(
                                    url=i.media,
                                    spoiler=i.has_spoiler
                                )
                            )
                        )

                        media = raw.types.InputMediaPhoto(
                            id=raw.types.InputPhoto(
                                id=media.photo.id,
                                access_hash=media.photo.access_hash,
                                file_reference=media.photo.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    else:
                        media = utils.get_input_media_from_file_id(
                            i.media,
                            FileType.PHOTO,
                            has_spoiler=i.has_spoiler
                        )
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            business_connection_id=business_connection_id,
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedPhoto(
                                file=await self.save_file(i.media),
                                spoiler=i.has_spoiler
                            )
                        )
                    )

                    media = raw.types.InputMediaPhoto(
                        id=raw.types.InputPhoto(
                            id=media.photo.id,
                            access_hash=media.photo.access_hash,
                            file_reference=media.photo.file_reference
                        ),
                        spoiler=i.has_spoiler
                    )
                show_caption_above_media.append(i.show_caption_above_media)
            elif isinstance(i, types.InputMediaVideo):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedDocument(
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    nosound_video=i.disable_content_type_detection or True,
                                    spoiler=i.has_spoiler,
                                    mime_type=self.guess_mime_type(i.media) or "video/mp4",
                                    attributes=[
                                        raw.types.DocumentAttributeVideo(
                                            supports_streaming=i.supports_streaming or None,
                                            duration=i.duration,
                                            w=i.width,
                                            h=i.height
                                        ),
                                        raw.types.DocumentAttributeFilename(file_name=i.file_name or os.path.basename(i.media))
                                    ]
                                )
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media,
                                    spoiler=i.has_spoiler
                                )
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.VIDEO, has_spoiler=i.has_spoiler)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            business_connection_id=business_connection_id,
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedDocument(
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                nosound_video=i.disable_content_type_detection or True,
                                spoiler=i.has_spoiler,
                                mime_type=self.guess_mime_type(getattr(i.media, "name", "video.mp4")) or "video/mp4",
                                attributes=[
                                    raw.types.DocumentAttributeVideo(
                                        supports_streaming=i.supports_streaming or None,
                                        duration=i.duration,
                                        w=i.width,
                                        h=i.height
                                    ),
                                    raw.types.DocumentAttributeFilename(file_name=i.file_name or getattr(i.media, "name", "video.mp4"))
                                ]
                            )
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        ),
                        spoiler=i.has_spoiler
                    )
                show_caption_above_media.append(i.show_caption_above_media)
            elif isinstance(i, types.InputMediaAudio):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedDocument(
                                    mime_type=self.guess_mime_type(i.media) or "audio/mpeg",
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    attributes=[
                                        raw.types.DocumentAttributeAudio(
                                            duration=i.duration,
                                            performer=i.performer,
                                            title=i.title
                                        ),
                                        raw.types.DocumentAttributeFilename(file_name=i.file_name or os.path.basename(i.media))
                                    ]
                                )
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media
                                )
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.AUDIO)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            business_connection_id=business_connection_id,
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedDocument(
                                mime_type=self.guess_mime_type(getattr(i.media, "name", "audio.mp3")) or "audio/mpeg",
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                attributes=[
                                    raw.types.DocumentAttributeAudio(
                                        duration=i.duration,
                                        performer=i.performer,
                                        title=i.title
                                    ),
                                    raw.types.DocumentAttributeFilename(file_name=i.file_name or getattr(i.media, "name", "audio.mp3"))
                                ]
                            )
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        )
                    )
            elif isinstance(i, types.InputMediaDocument):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedDocument(
                                    mime_type=self.guess_mime_type(i.media) or "application/zip",
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    attributes=[
                                        raw.types.DocumentAttributeFilename(file_name=i.file_name or os.path.basename(i.media))
                                    ]
                                    # TODO
                                )
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                business_connection_id=business_connection_id,
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media
                                )
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.DOCUMENT)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            business_connection_id=business_connection_id,
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedDocument(
                                mime_type=self.guess_mime_type(
                                    getattr(i.media, "name", "file.zip")
                                ) or "application/zip",
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                attributes=[
                                    raw.types.DocumentAttributeFilename(file_name=i.file_name or getattr(i.media, "name", "file.zip"))
                                ]
                            )
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        )
                    )
            else:
                raise ValueError(f"{i.__class__.__name__} is not a supported type for send_media_group")

            multi_media.append(
                raw.types.InputSingleMedia(
                    media=media,
                    random_id=self.rnd_id(),
                    **await utils.parse_text_entities(self, i.caption, i.parse_mode, i.caption_entities)
                )
            )

        reply_to = await utils._get_reply_message_parameters(
            self,
            message_thread_id,
            reply_parameters
        )
        rpc = raw.functions.messages.SendMultiMedia(
            peer=await self.resolve_peer(chat_id),
            multi_media=multi_media,
            silent=disable_notification or None,
            reply_to=reply_to,
            send_as=await self.resolve_peer(send_as) if send_as else None,
            schedule_date=utils.datetime_to_timestamp(schedule_date),
            noforwards=protect_content,
            allow_paid_floodskip=allow_paid_broadcast,
            allow_paid_stars=paid_message_star_count,
            effect=message_effect_id,
            invert_media=any(show_caption_above_media)
        )
        session = None
        business_connection = None
        if business_connection_id:
            business_connection = self.business_user_connection_cache[business_connection_id]
            if business_connection is None:
                business_connection = await self.get_business_connection(business_connection_id)
            session = await get_session(
                self,
                business_connection._raw.connection.dc_id
            )
        if business_connection_id:
            r = await session.invoke(
                raw.functions.InvokeWithBusinessConnection(
                    query=rpc,
                    connection_id=business_connection_id
                )
            )
            # await session.stop()
        else:
            r = await self.invoke(
                rpc,
                sleep_threshold=60
            )

        return await utils.parse_messages(
            client=self,
            messages=None,
            business_connection_id=business_connection_id,
            r=r
        )
