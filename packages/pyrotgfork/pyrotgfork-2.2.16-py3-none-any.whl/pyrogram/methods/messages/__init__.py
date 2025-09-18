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

from .copy_media_group import CopyMediaGroup
from .copy_message import CopyMessage
from .delete_chat_history import DeleteChatHistory
from .delete_messages import DeleteMessages
from .download_media import DownloadMedia
from .edit_cached_media import EditCachedMedia
from .edit_inline_caption import EditInlineCaption
from .edit_inline_media import EditInlineMedia
from .edit_inline_reply_markup import EditInlineReplyMarkup
from .edit_inline_text import EditInlineText
from .edit_message_caption import EditMessageCaption
from .edit_message_media import EditMessageMedia
from .edit_message_reply_markup import EditMessageReplyMarkup
from .edit_message_text import EditMessageText
from .forward_messages import ForwardMessages
from .get_chat_history import GetChatHistory
from .get_chat_history_count import GetChatHistoryCount
from .get_custom_emoji_stickers import GetCustomEmojiStickers
from .get_discussion_message import GetDiscussionMessage
from .get_discussion_replies import GetDiscussionReplies
from .get_discussion_replies_count import GetDiscussionRepliesCount
from .get_media_group import GetMediaGroup
from .get_messages import GetMessages
from .read_chat_history import ReadChatHistory
from .retract_vote import RetractVote
from .search_global import SearchGlobal
from .search_global_count import SearchGlobalCount
from .search_messages import SearchMessages
from .search_messages_count import SearchMessagesCount
from .send_animation import SendAnimation
from .send_audio import SendAudio
from .send_cached_media import SendCachedMedia
from .send_chat_action import SendChatAction
from .send_contact import SendContact
from .send_dice import SendDice
from .send_document import SendDocument
from .send_location import SendLocation
from .send_media_group import SendMediaGroup
from .send_message import SendMessage
from .send_paid_media import SendPaidMedia
from .send_photo import SendPhoto
from .send_poll import SendPoll
from .add_paid_message_reaction import AddPaidMessageReaction
from .set_reaction import SetReaction
from .send_sticker import SendSticker
from .send_venue import SendVenue
from .send_video import SendVideo
from .send_video_note import SendVideoNote
from .send_voice import SendVoice
from .stop_poll import StopPoll
from .stream_media import StreamMedia
from .view_messages import ViewMessages
from .vote_poll import VotePoll
from .get_chat_sponsored_messages import GetChatSponsoredMessages
from .search_public_messages_by_tag import SearchPublicMessagesByTag
from .count_public_messages_by_tag import CountPublicMessagesByTag
from .translate_text import TranslateText
from .send_screenshot_notification import SendScreenshotNotification
from .send_checklist import SendChecklist
from .edit_message_checklist import EditMessageChecklist
from .mark_checklist_tasks_as_done import MarkChecklistTasksAsDone

class Messages(
    CopyMediaGroup,
    CopyMessage,
    DeleteChatHistory,
    DeleteMessages,
    DownloadMedia,
    EditCachedMedia,
    EditInlineCaption,
    EditInlineMedia,
    EditInlineReplyMarkup,
    EditInlineText,
    EditMessageCaption,
    EditMessageMedia,
    EditMessageReplyMarkup,
    EditMessageText,
    ForwardMessages,
    GetChatHistory,
    GetChatHistoryCount,
    GetCustomEmojiStickers,
    GetDiscussionMessage,
    GetDiscussionReplies,
    GetDiscussionRepliesCount,
    GetMediaGroup,
    GetMessages,
    ReadChatHistory,
    RetractVote,
    SearchGlobal,
    SearchGlobalCount,
    SearchMessages,
    SearchMessagesCount,
    SearchPublicMessagesByTag,
    CountPublicMessagesByTag,
    SendAnimation,
    SendAudio,
    SendCachedMedia,
    SendChatAction,
    SendContact,
    SendDice,
    SendDocument,
    SendLocation,
    SendMediaGroup,
    SendMessage,
    SendPaidMedia,
    SendPhoto,
    SendPoll,
    SendScreenshotNotification,
    SendSticker,
    SendVenue,
    SendVideo,
    SendVideoNote,
    SendVoice,
    AddPaidMessageReaction,
    SetReaction,
    StopPoll,
    StreamMedia,
    ViewMessages,
    VotePoll,
    GetChatSponsoredMessages,
    TranslateText,
    SendChecklist,
    EditMessageChecklist,
    MarkChecklistTasksAsDone,
):
    pass
