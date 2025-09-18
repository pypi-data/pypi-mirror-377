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

import io
import logging
from datetime import datetime
from typing import Callable, Optional, Union

import pyrogram
from pyrogram import raw, utils, types, enums
from ..object import Object
from ..update import Update
from ..messages_and_media.message import Str
from pyrogram.errors import RPCError

log = logging.getLogger(__name__)


class Story(Object, Update):
    """This object represents a story.

    Parameters:
        id (``int``):
            Unique story identifier among stories of the given sender.

        chat (:obj:`~pyrogram.types.Chat`):
            Identifier of the chat that posted the story.
        
        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the story was published.
        
        expire_date (:py:obj:`~datetime.datetime`, *optional*):
            Date the story will be expired.
        
        is_edited (``bool``, *optional*):
            True, if the story was edited.

        is_posted_to_chat_page (``bool``, *optional*):
            True, if the story is saved in the sender's profile and will be available there after expiration

        is_visible_only_for_self (``bool``, *optional*):
            True, if the story is visible only for the current user.

        repost_info (:obj:`~pyrogram.types.StoryRepostInfo`, *optional*):
            Information about the original story; may be None if the story wasn't reposted.

        privacy_settings (:obj:`~pyrogram.types.StoryPrivacySettings`, *optional*):
            Privacy rules affecting story visibility; may be approximate for non-owned stories.

        media (:obj:`~pyrogram.enums.MessageMediaType`, *optional*):
            The media type of the Story.
            This field will contain the enumeration type of the media message.
            You can use ``media = getattr(story, story.media.value)`` to access the media message.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Story is a photo, information about the photo.

        video (:obj:`~pyrogram.types.Video`, *optional*):
            Story is a video, information about the video.

        caption (``str``, *optional*):
            Caption for the Story, 0-1024 characters.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the caption.

        areas (List of :obj:`~pyrogram.types.StoryArea`, *optional*):
            Clickable areas to be shown on the story content.

        has_protected_content (``bool``, *optional*):
            True, if the story can't be forwarded.

        reactions (List of :obj:`~pyrogram.types.Reaction`):
            List of the reactions to this story.

        views (``int``, *optional*):
            Stories views.

        forwards (``int``, *optional*):
            Stories forwards.

        skipped (``bool``, *optional*):
            The story is skipped.
            A story can be skipped in case it was skipped.

        deleted (``bool``, *optional*):
            The story is deleted.
            A story can be deleted in case it was deleted or you tried to retrieve a story that doesn't exist yet.
        
        album_ids (List of ``int``):
            Identifiers of story albums to which the story is added; only for manageable stories.

        link (``str``, *property*):
            Generate a link to this story, only for Telegram Premium chats having usernames. Can be None if the story cannot have a link.

    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int = None,
        chat: "types.Chat" = None,
        date: datetime = None,
        expire_date: datetime = None,
        is_edited: bool = None,
        is_posted_to_chat_page: bool = None,
        is_visible_only_for_self: bool = None,
        repost_info: "types.StoryRepostInfo" = None,
        privacy_settings: "types.StoryPrivacySettings" = None,
        media: "enums.MessageMediaType" = None,
        photo: "types.Photo" = None,
        video: "types.Video" = None,
        caption: Str = None,
        caption_entities: list["types.MessageEntity"] = None,
        areas: list["types.StoryArea"] = None,
        has_protected_content: bool = None,
        reactions: list["types.Reaction"] = None,
        views: int = None,
        forwards: int = None,
        skipped: bool = None,
        deleted: bool = None,
        album_ids: list[int] = None,
        _raw = None
    ):
        super().__init__(client)

        self.id = id
        self.chat = chat
        self.date = date
        self.expire_date = expire_date
        self.is_edited = is_edited
        self.is_posted_to_chat_page = is_posted_to_chat_page
        self.is_visible_only_for_self = is_visible_only_for_self
        self.repost_info = repost_info
        self.privacy_settings = privacy_settings
        self.media = media
        self.photo = photo
        self.video = video
        self.caption = caption
        self.caption_entities = caption_entities
        self.areas = areas
        self.has_protected_content = has_protected_content
        self.reactions = reactions
        self.views = views
        self.forwards = forwards
        self.skipped = skipped
        self.deleted = deleted
        self.album_ids = album_ids
        self._raw = _raw

    @staticmethod
    def _parse_story_item(
        client,
        story_item: "raw.types.StoryItem"
    ):
        date = None
        expire_date = None
        media = None
        has_protected_content = None
        photo = None
        video = None
        is_edited = None
        is_posted_to_chat_page = None
        caption = None
        caption_entities = None
        views = None
        forwards = None
        reactions = None
        skipped = None
        deleted = None
        is_visible_only_for_self = None
        areas = None
        privacy_settings = None
        album_ids = None

        if isinstance(story_item, raw.types.StoryItemDeleted):
            deleted = True
        elif isinstance(story_item, raw.types.StoryItemSkipped):
            skipped = True
            date = utils.timestamp_to_datetime(story_item.date)
            expire_date = utils.timestamp_to_datetime(story_item.expire_date)
            # close_friends:flags.8?true
        else:
            date = utils.timestamp_to_datetime(story_item.date)
            expire_date = utils.timestamp_to_datetime(story_item.expire_date)
            # close_friends:flags.8?true
            # contacts:flags.12?true
            # selected_contacts:flags.13?true

            is_visible_only_for_self = not story_item.public

            # out:flags.16?true
            if story_item.privacy:
                privacy_settings = types.StoryPrivacySettings._parse(client, story_item.privacy)

            # sent_reaction:flags.15?Reaction = StoryItem;

            if isinstance(story_item.media, raw.types.MessageMediaPhoto):
                photo = types.Photo._parse(client, story_item.media.photo, story_item.media.ttl_seconds)
                media = enums.MessageMediaType.PHOTO
            elif isinstance(story_item.media, raw.types.MessageMediaDocument):
                doc = story_item.media.document
                attributes = {type(i): i for i in doc.attributes}
                video_attributes = attributes.get(raw.types.DocumentAttributeVideo, None)
                video = types.Video._parse(client, story_item.media, video_attributes, None)
                media = enums.MessageMediaType.VIDEO
            has_protected_content = story_item.noforwards
            is_edited = story_item.edited
            is_posted_to_chat_page = story_item.pinned
            entities = [e for e in (types.MessageEntity._parse(client, entity, {}) for entity in story_item.entities) if e]
            caption = Str(story_item.caption or "").init(entities) or None
            caption_entities = entities or None
            if story_item.views:
                views = getattr(story_item.views, "views_count", None)
                forwards = getattr(story_item.views, "forwards_count", None)
                reactions = [
                    types.Reaction._parse_count(client, reaction)
                    for reaction in getattr(story_item.views, "reactions", [])
                ] or None
            
            if story_item.media_areas:
                areas = [
                    types.StoryArea._parse(
                        client,
                        area,
                    ) for area in story_item.media_areas
                ]
            
            album_ids = story_item.albums

        return (
            date,
            expire_date,
            media,
            has_protected_content,
            photo,
            video,
            is_edited,
            is_posted_to_chat_page,
            caption,
            caption_entities,
            views,
            forwards,
            reactions,
            skipped,
            deleted,
            is_visible_only_for_self,
            areas,
            privacy_settings,
            album_ids,
        )

    @staticmethod
    async def _parse(
        client,
        users: dict,
        chats: dict,
        story_media: "raw.types.MessageMediaStory",
        reply_story: "raw.types.MessageReplyStoryHeader",
        story_update: "raw.types.UpdateStory",
        story_item: "raw.types.StoryItem",
        peer: "raw.base.peer"
    ) -> "Story":
        story_id = None
        chat = None

        rawupdate = None

        date = None
        expire_date = None
        media = None
        has_protected_content = None
        photo = None
        video = None
        is_edited = None
        is_posted_to_chat_page = None
        is_visible_only_for_self = None
        caption = None
        caption_entities = None
        views = None
        forwards = None
        reactions = None
        skipped = None
        deleted = None
        areas = None
        privacy_settings = None
        repost_info = None
        album_ids = None

        if story_media:
            rawupdate = story_media

            if story_media.peer:
                raw_peer_id = utils.get_raw_peer_id(story_media.peer)
                if isinstance(story_media.peer, raw.types.PeerUser):
                    chat = types.Chat._parse_chat(client, users.get(raw_peer_id))
                else:
                    chat = types.Chat._parse_chat(client, chats.get(raw_peer_id))
            story_id = getattr(story_media, "id", None)
        
        if reply_story:
            rawupdate = reply_story

            if reply_story.peer:
                raw_peer_id = utils.get_raw_peer_id(reply_story.peer)
                if isinstance(reply_story.peer, raw.types.PeerUser):
                    chat = types.Chat._parse_chat(client, users.get(raw_peer_id))
                else:
                    chat = types.Chat._parse_chat(client, chats.get(raw_peer_id))
            story_id = getattr(reply_story, "story_id", None)
        
        if story_update:
            rawupdate = story_update

            raw_peer_id = utils.get_raw_peer_id(story_update.peer)
            if isinstance(story_update.peer, raw.types.PeerUser):
                chat = types.Chat._parse_chat(client, users.get(raw_peer_id))
            else:
                chat = types.Chat._parse_chat(client, chats.get(raw_peer_id))
            
            story_id = getattr(story_update.story, "id", None)
            story_item = story_update.story

        if (
            not story_item and
            story_id and
            not (client.me and client.me.is_bot)
        ):
            try:
                story_item = (
                    await client.invoke(
                        raw.functions.stories.GetStoriesByID(
                            peer=await client.resolve_peer(raw_peer_id),
                            id=[story_id]
                        )
                    )
                ).stories[0]
            except (RPCError, IndexError):
                pass

        if peer:
            raw_peer_id = utils.get_raw_peer_id(peer)
            if isinstance(peer, raw.types.PeerUser):
                chat = types.Chat._parse_chat(client, users.get(raw_peer_id))
            else:
                chat = types.Chat._parse_chat(client, chats.get(raw_peer_id))

        if story_item:
            rawupdate = story_item

            if not story_id:
                story_id = getattr(story_item, "id", None)
            (
                date,
                expire_date,
                media,
                has_protected_content,
                photo,
                video,
                is_edited,
                is_posted_to_chat_page,
                caption,
                caption_entities,
                views,
                forwards,
                reactions,
                skipped,
                deleted,
                is_visible_only_for_self,
                areas,
                privacy_settings,
                album_ids,
            ) = Story._parse_story_item(client, story_item)

            if not chat and story_item.from_id:
                peer_id = utils.get_peer_id(story_item.from_id)
                if isinstance(story_item.from_id, raw.types.PeerUser):
                    chat = types.Chat._parse_user_chat(client, users.get(peer_id, None))
                elif isinstance(story_item.from_id, raw.types.PeerChat):
                    chat = types.Chat._parse_chat_chat(client, chats.get(peer_id, None))
                else:
                    chat = types.Chat._parse_channel_chat(client, chats.get(peer_id, None))

            if getattr(story_item, "fwd_from", None):
                repost_info = types.StoryRepostInfo._parse(
                    client, story_item.fwd_from,
                    users, chats
                )

        return Story(
            client=client,
            _raw=rawupdate,
            id=story_id,
            chat=chat,
            date=date,
            expire_date=expire_date,
            media=media,
            has_protected_content=has_protected_content,
            photo=photo,
            video=video,
            is_edited=is_edited,
            is_posted_to_chat_page=is_posted_to_chat_page,
            is_visible_only_for_self=is_visible_only_for_self,
            caption=caption,
            caption_entities=caption_entities,
            views=views,
            forwards=forwards,
            reactions=reactions,
            skipped=skipped,
            deleted=deleted,
            areas=areas,
            privacy_settings=privacy_settings,
            repost_info=repost_info,
            album_ids=album_ids,
        )

    async def react(
        self,
        reaction: Union[
            int,
            str
        ] = None,
        add_to_recent: bool = True
    ) -> "types.MessageReactions":
        """Bound method *react* of :obj:`~pyrogram.types.Story`.

        Use as a shortcut for:

        .. code-block:: python

            await client.set_reaction(
                chat_id=chat_id,
                story_id=message.id,
                reaction=[ReactionTypeEmoji(emoji="👍")]
            )

        Example:
            .. code-block:: python

                # Send a reaction
                await story.react([ReactionTypeEmoji(emoji="👍")])

                # Retract a reaction
                await story.react()

        Parameters:
            reaction (``int`` | ``str``, *optional*):
                New list of reaction types to set on the message.
                Pass None as emoji (default) to retract the reaction.

            add_to_recent (``bool``, *optional*):
                Pass True if the reaction should appear in the recently used reactions.
                This option is applicable only for users.
                Defaults to True.
        Returns:
            On success, :obj:`~pyrogram.types.MessageReactions`: is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        sr = None

        if isinstance(reaction, list):
            sr = []
            for i in reaction:
                if isinstance(i, types.ReactionType):
                    sr.append(i)
                elif isinstance(i, int):
                    sr.append(types.ReactionTypeCustomEmoji(
                        custom_emoji_id=str(i)
                    ))
                else:
                    sr.append(types.ReactionTypeEmoji(
                        emoji=i
                    ))

        elif isinstance(reaction, int):
            sr = [
                types.ReactionTypeCustomEmoji(
                    custom_emoji_id=str(reaction)
                )
            ]

        elif isinstance(reaction, str):
            sr = [
                types.ReactionTypeEmoji(
                    emoji=reaction
                )
            ]

        return await self._client.set_reaction(
            chat_id=self.chat.id,
            story_id=self.id,
            reaction=sr,
            add_to_recent=add_to_recent
        )

    async def download(
        self,
        file_name: str = "",
        in_memory: bool = False,
        block: bool = True,
        progress: Callable = None,
        progress_args: tuple = ()
    ) -> Optional[Union[str, "io.BytesIO"]]:
        """Bound method *download* of :obj:`~pyrogram.types.Story`.

        Use as a shortcut for:

        .. code-block:: python

            await client.download_media(story)

        Example:
            .. code-block:: python

                await story.download()

        Parameters:
            file_name (``str``, *optional*):
                A custom *file_name* to be used instead of the one provided by Telegram.
                By default, all files are downloaded in the *downloads* folder in your working directory.
                You can also specify a path for downloading files in a custom location: paths that end with "/"
                are considered directories. All non-existent folders will be created automatically.

            in_memory (``bool``, *optional*):
                Pass True to download the media in-memory.
                A binary file-like object with its attribute ".name" set will be returned.
                Defaults to False.

            block (``bool``, *optional*):
                Blocks the code execution until the file has been downloaded.
                Defaults to True.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            ``str`` | ``None`` | :obj:`io.BytesIO`: On success, the absolute path of the downloaded file is returned,
            otherwise, in case the download failed or was deliberately stopped with
            :meth:`~pyrogram.Client.stop_transmission`, None is returned.
            Otherwise, in case ``in_memory=True``, a binary file-like object with its attribute ".name" set is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ``ValueError``: If the message doesn't contain any downloadable media
        """
        return await self._client.download_media(
            message=self,
            file_name=file_name,
            in_memory=in_memory,
            block=block,
            progress=progress,
            progress_args=progress_args,
        )

    @property
    def link(self) -> str:
        if self.chat and self.chat.username:
            return f"https://t.me/{self.chat.username}/s/{self.id}"

    @property
    def edited(self) -> bool:
        log.warning(
            "This property is deprecated. "
            "Please use is_edited instead"
        )
        return self.is_edited

    @property
    def pinned(self) -> bool:
        log.warning(
            "This property is deprecated. "
            "Please use is_posted_to_chat_page instead"
        )
        return self.is_posted_to_chat_page
