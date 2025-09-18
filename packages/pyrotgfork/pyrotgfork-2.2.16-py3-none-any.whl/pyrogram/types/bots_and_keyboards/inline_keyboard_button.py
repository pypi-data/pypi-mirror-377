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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types
from ..object import Object


class InlineKeyboardButton(Object):
    """One button of an inline keyboard.

    You must use exactly one of the optional fields.

    Parameters:
        text (``str``):
            Label text on the button.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        user_id (``int``, *optional*):
            User id, for links to the user profile.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the `Web App <https://core.telegram.org/bots/webapps>`_ that will be launched when the user
            presses the button. The Web App will be able to send an arbitrary message on behalf of the user using the
            method :meth:`~pyrogram.Client.answer_web_app_query`. Available only in private chats between a user and the
            bot.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
             An HTTP URL used to automatically authorize the user. Can be used as a replacement for
             the `Telegram Login Widget <https://core.telegram.org/widgets/login>`_.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert
            the bot's username and the specified inline query in the input field. Can be empty, in which case just
            the bot's username will be inserted.Note: This offers an easy way for users to start using your bot in
            inline mode when they are currently in a private chat with it. Especially useful when combined with
            switch_pm… actions – in this case the user will be automatically returned to the chat they switched from,
            skipping the chat selection screen.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username and the specified inline query in the current
            chat's input field. Can be empty, in which case only the bot's username will be inserted.This offers a
            quick way for the user to open your bot in inline mode in the same chat - good for selecting something
            from multiple options.

        switch_inline_query_chosen_chat (:obj:`~pyrogram.types.SwitchInlineQueryChosenChat`, *optional*):
            If set, pressing the button will prompt the user to select one of their chats of the specified type, open that chat and insert the bot's username and the specified inline query in the input field

        copy_text (:obj:`~pyrogram.types.CopyTextButton`, *optional*):
            Description of the button that copies the specified text to the clipboard.

        callback_game (:obj:`~pyrogram.types.CallbackGame`, *optional*):
            Description of the game that will be launched when the user presses the button.

            .. note::

                This type of button **must** always be the first button in the first row.
        
        pay (``bool``, *optional*):
            Specify True, to send a Pay button. Substrings "⭐" and "XTR" in the buttons's text will be replaced with a Telegram Star icon.

            .. note::
            
                This type of button **must** always be the first button in the first row and can only be used in invoice messages.

        callback_data_with_password (``bytes``, *optional*):
            A button that asks for the 2-step verification password of the current user and then sends a callback query to a bot Data to be sent to the bot via a callback query.

    """

    def __init__(
        self,
        text: str, *,
        url: Optional[str] = None,
        user_id: Optional[int] = None,
        callback_data: Optional[Union[str, bytes]] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        login_url: Optional["types.LoginUrl"] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        switch_inline_query_chosen_chat: Optional["types.SwitchInlineQueryChosenChat"] = None,
        copy_text: Optional["types.CopyTextButton"] = None,
        callback_game: Optional["types.CallbackGame"] = None,
        pay: Optional[bool] = None,
        callback_data_with_password: Optional[bytes] = None
    ):
        super().__init__()

        self.text = str(text)
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.login_url = login_url
        self.user_id = user_id
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.switch_inline_query_chosen_chat = switch_inline_query_chosen_chat
        self.callback_game = callback_game
        self.pay = pay
        self.copy_text = copy_text
        self.callback_data_with_password = callback_data_with_password

    @staticmethod
    def read(b: "raw.base.KeyboardButton"):
        if isinstance(b, raw.types.KeyboardButtonCallback):
            # Try decode data to keep it as string, but if fails, fallback to bytes so we don't lose any information,
            # instead of decoding by ignoring/replacing errors.
            try:
                data = b.data.decode()
            except UnicodeDecodeError:
                data = b.data

            if getattr(b, "requires_password", None):
                return InlineKeyboardButton(
                    text=b.text,
                    callback_data_with_password=data
                )

            return InlineKeyboardButton(
                text=b.text,
                callback_data=data
            )

        if isinstance(b, raw.types.KeyboardButtonUrl):
            return InlineKeyboardButton(
                text=b.text,
                url=b.url
            )

        if isinstance(b, raw.types.KeyboardButtonUrlAuth):
            return InlineKeyboardButton(
                text=b.text,
                login_url=types.LoginUrl.read(b)
            )

        if isinstance(b, raw.types.KeyboardButtonUserProfile):
            return InlineKeyboardButton(
                text=b.text,
                user_id=b.user_id
            )

        if isinstance(b, raw.types.KeyboardButtonSwitchInline):
            if b.same_peer:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query_current_chat=b.query
                )
            elif b.peer_types:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat.read(b)
                )
            else:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query=b.query
                )

        if isinstance(b, raw.types.KeyboardButtonGame):
            return InlineKeyboardButton(
                text=b.text,
                callback_game=types.CallbackGame()
            )

        if isinstance(b, raw.types.KeyboardButtonWebView):
            return InlineKeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(
                    url=b.url
                )
            )
        
        if isinstance(b, raw.types.KeyboardButtonBuy):
            return InlineKeyboardButton(
                text=b.text,
                pay=True
            )

        if isinstance(b, raw.types.KeyboardButtonCopy):
            return InlineKeyboardButton(
                text=b.text,
                copy_text=types.CopyTextButton(
                    text=b.copy_text
                )
            )

        if isinstance(b, raw.types.KeyboardButton):
            return InlineKeyboardButton(
                text=b.text
            )

    async def write(self, client: "pyrogram.Client"):
        if self.callback_data_with_password is not None:
            if isinstance(self.callback_data_with_password, str):
                raise ValueError(
                    "This is not supported"
                )
            data = self.callback_data_with_password
            return raw.types.KeyboardButtonCallback(
                text=self.text,
                data=data,
                requires_password=True
            )

        if self.callback_data is not None:
            # Telegram only wants bytes, but we are allowed to pass strings too, for convenience.
            data = bytes(self.callback_data, "utf-8") if isinstance(self.callback_data, str) else self.callback_data

            return raw.types.KeyboardButtonCallback(
                text=self.text,
                data=data
            )

        if self.url is not None:
            return raw.types.KeyboardButtonUrl(
                text=self.text,
                url=self.url
            )

        if self.login_url is not None:
            return self.login_url.write(
                text=self.text,
                bot=await client.resolve_peer(self.login_url.bot_username or "self")
            )

        if self.user_id is not None:
            return raw.types.InputKeyboardButtonUserProfile(
                text=self.text,
                user_id=await client.resolve_peer(self.user_id)
            )

        if self.switch_inline_query is not None:
            return raw.types.KeyboardButtonSwitchInline(
                text=self.text,
                query=self.switch_inline_query
            )

        if self.switch_inline_query_current_chat is not None:
            return raw.types.KeyboardButtonSwitchInline(
                text=self.text,
                query=self.switch_inline_query_current_chat,
                same_peer=True
            )

        if self.switch_inline_query_chosen_chat is not None:
            return self.switch_inline_query_chosen_chat.write(
                text=self.text
            )

        if self.callback_game is not None:
            return raw.types.KeyboardButtonGame(
                text=self.text
            )

        if self.web_app is not None:
            return raw.types.KeyboardButtonWebView(
                text=self.text,
                url=self.web_app.url
            )

        if (
            self.pay is not None and
            self.pay
        ):
            return raw.types.KeyboardButtonBuy(
                text=self.text
            )

        if self.copy_text is not None:
            return raw.types.KeyboardButtonCopy(
                text=self.text,
                copy_text=self.copy_text.text
            )
