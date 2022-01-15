from telethon.events import NewMessage, CallbackQuery

from app.config import msg


class TelegramMessageHandler:

    async def handle(self, event: NewMessage.Event, *args):
        print(f"Message '{event.message.message}' in chat({event.chat_id}) at '{event.message.date}'." +
              f"Args: {','.join(args)}" if len(args) > 0 else "")
        try:

            await self.handle_(event, *args)
        except Exception as e:
            print(e)
            await event.respond(msg.ERROR_BASIC)

    async def handle_(self, event: NewMessage.Event, *args):
        """Response to NewMessage.Event"""
        pass


class TelegramCallbackHandler:

    async def handle(self, call: CallbackQuery.Event):
        print(f"Callback in chat({call.original_update.user_id})")

        try:
            await call.delete()
            await self.handle_(call)
        except Exception as e:
            print(e)
            await call.respond(msg.ERROR_BASIC)

    async def handle_(self, callback: CallbackQuery.Event):
        """Response to CallbackQuery.Event"""
        pass
