from telethon import Button
from telethon.client import ButtonMethods
from telethon.events import NewMessage

from app.config import msg
from app.handler.general import TelegramMessageHandler
from app.handler.strike import StrikeCallbackHandler
from app.service import ChatService


class StartHandler(TelegramMessageHandler):
    MARK = 'cmd'

    def __init__(self, chat_service: ChatService):
        print('Creating StartHandler...')
        self.chat_service = chat_service

    async def handle_(self, event: NewMessage.Event, *args):
        member = await self.chat_service.find_member_by_id(event.chat_id)

        if not member:
            print(f"Not found member User({event.chat_id})")
            await event.respond(msg.NOT_MEMBER)
        else:
            print(f"Menu for User({event.chat_id})")

            markup = ButtonMethods.build_reply_markup(buttons=[
                [Button.inline('Пожаловаться', StrikeCallbackHandler.MARKER)]
                # [Button.inline('Отменить жалобу', 'c')],
                # [Button.inline('Проверить жалобы на меня', 'ch')]
            ], inline_only=True)
            await event.respond(msg.START, buttons=markup)
