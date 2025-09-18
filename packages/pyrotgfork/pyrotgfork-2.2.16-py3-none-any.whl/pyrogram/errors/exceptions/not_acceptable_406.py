# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from ..rpc_error import RPCError


class NotAcceptable(RPCError):
    """Not Acceptable"""
    CODE = 406
    """``int``: RPC Error Code"""
    NAME = __doc__


class AuthKeyDuplicated(NotAcceptable):
    """Concurrent usage of the current session from multiple connections was detected, the current session was invalidated by the server for security reasons!"""
    ID = "AUTH_KEY_DUPLICATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BannedRightsInvalid(NotAcceptable):
    """You provided some invalid flags in the banned rights."""
    ID = "BANNED_RIGHTS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotPrecheckoutFailed(NotAcceptable):
    """Bot precheckout failed."""
    ID = "BOT_PRECHECKOUT_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BusinessAddressActive(NotAcceptable):
    """The user is currently advertising a [Business Location](https://core.telegram.org/api/business#location), the location may only be changed (or removed) using [account.updateBusinessLocation](https://core.telegram.org/method/account.updateBusinessLocation).  ."""
    ID = "BUSINESS_ADDRESS_ACTIVE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallProtocolCompatLayerInvalid(NotAcceptable):
    """The other side of the call does not support any of the VoIP protocols supported by the local client, as specified by the `protocol.layer` and `protocol.library_versions` fields."""
    ID = "CALL_PROTOCOL_COMPAT_LAYER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelPrivate(NotAcceptable):
    """You haven't joined this channel/supergroup."""
    ID = "CHANNEL_PRIVATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelTooLarge(NotAcceptable):
    """Channel is too large to be deleted; this error is issued when trying to delete channels with more than 1000 members (subject to change)."""
    ID = "CHANNEL_TOO_LARGE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatForwardsRestricted(NotAcceptable):
    """You can't forward messages from a protected chat."""
    ID = "CHAT_FORWARDS_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilerefUpgradeNeeded(NotAcceptable):
    """The client has to be updated in order to support [file references](https://core.telegram.org/api/file_reference)."""
    ID = "FILEREF_UPGRADE_NEEDED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FreshChangeAdminsForbidden(NotAcceptable):
    """You were just elected admin, you can't add or modify other admins yet."""
    ID = "FRESH_CHANGE_ADMINS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FreshChangePhoneForbidden(NotAcceptable):
    """You can't change phone number right after logging in, please wait at least 24 hours."""
    ID = "FRESH_CHANGE_PHONE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FreshResetAuthorisationForbidden(NotAcceptable):
    """You can't logout other sessions if less than 24 hours have passed since you logged on the current session."""
    ID = "FRESH_RESET_AUTHORISATION_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteHashExpired(NotAcceptable):
    """The invite link has expired."""
    ID = "INVITE_HASH_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PaymentUnsupported(NotAcceptable):
    """A detailed description of the error will be received separately as described [here](https://core.telegram.org/api/errors#406-not-acceptable)."""
    ID = "PAYMENT_UNSUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberInvalid(NotAcceptable):
    """The phone number is invalid."""
    ID = "PHONE_NUMBER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhonePasswordFlood(NotAcceptable):
    """You have tried logging in too many times."""
    ID = "PHONE_PASSWORD_FLOOD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumCurrentlyUnavailable(NotAcceptable):
    """You cannot currently purchase a Premium subscription."""
    ID = "PREMIUM_CURRENTLY_UNAVAILABLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PreviousChatImportActiveWaitMin(NotAcceptable):
    """Import for this chat is already in progress, wait {value} minutes before starting a new one."""
    ID = "PREVIOUS_CHAT_IMPORT_ACTIVE_WAIT_XMIN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrivacyPremiumRequired(NotAcceptable):
    """You need a [Telegram Premium subscription](https://core.telegram.org/api/premium) to send a message to this user."""
    ID = "PRIVACY_PREMIUM_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendCodeUnavailable(NotAcceptable):
    """Returned when all available options for this type of number were already used (e.g. flash-call, then SMS, then this error might be returned to trigger a second resend)."""
    ID = "SEND_CODE_UNAVAILABLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StargiftExportInProgress(NotAcceptable):
    """Gift export in progress."""
    ID = "STARGIFT_EXPORT_IN_PROGRESS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickersetInvalid(NotAcceptable):
    """The provided sticker set is invalid."""
    ID = "STICKERSET_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickersetOwnerAnonymous(NotAcceptable):
    """Provided stickerset can't be installed as group stickerset to prevent admin deanonymization."""
    ID = "STICKERSET_OWNER_ANONYMOUS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicClosed(NotAcceptable):
    """This topic was closed, you can't send messages to it anymore."""
    ID = "TOPIC_CLOSED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicDeleted(NotAcceptable):
    """The specified topic was deleted."""
    ID = "TOPIC_DELETED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UpdateAppToLogin(NotAcceptable):
    """Please update your client to login."""
    ID = "UPDATE_APP_TO_LOGIN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserpicPrivacyRequired(NotAcceptable):
    """You need to disable privacy settings for your profile picture in order to make your geolocation public."""
    ID = "USERPIC_PRIVACY_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserpicUploadRequired(NotAcceptable):
    """You must have a profile picture to publish your geolocation."""
    ID = "USERPIC_UPLOAD_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserRestricted(NotAcceptable):
    """You're spamreported, you can't create channels or chats."""
    ID = "USER_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


