from telebot.types import User
from telethon import TelegramClient
from telethon.events import CallbackQuery
from telethon.tl.custom import Conversation

from app.config import msg, config
from app.handler.general import TelegramCallbackHandler
from app.service import ChatService, StrikeService


class StrikeCallbackHandler(TelegramCallbackHandler):
    MARKER = 's'

    __confirmation_words = ('да', 'нет')

    def __init__(self, bot: TelegramClient, chat_service: ChatService, strike_service: StrikeService):
        print('Creating StrikeCallbackHandler...')
        self.bot = bot
        self.chat_service = chat_service
        self.strike_service = strike_service

    async def handle_(self, call: CallbackQuery.Event):
        print(f'User({call.chat_id}) has started strike process')
        async with self.bot.conversation(call.chat, timeout=300) as conv:
            print(f'Started conversation with User({call.chat_id})')

            # Bot ask to write username
            await conv.send_message(msg.STRIKE_1)

            # User writes the username
            reported_user = await self.__report_user_input_loop(
                conv=conv,
                from_user_id=call.chat_id
            )

            # Bot ask to write the reason of report
            await conv.send_message(msg.STRIKE_3)
            print(f'Asked User({call.chat_id}) to write the reason for striking User({reported_user.id})')

            # User writes the reason of report
            reason_resp = await conv.get_response()
            reason: str = reason_resp.raw_text
            print(f"User({call.chat_id}) has written the reason: '{reason}'")

            user_nick = '@' + reported_user.username if reported_user.username \
                else '`' + reported_user.last_name + reported_user.first_name + '`'

            # Bot write everything and ask a confirmation
            print(f'Asked User({call.chat_id}) to confirm the Strike(user={reported_user.id}, reason={reason})')
            await conv.send_message(msg.STRIKE_4_1.format(user_nick, reason))
            await conv.send_message(msg.STRIKE_4_2)

            # User writes the confirmation
            confirmation: str = await self.__confirm_strike_loop(conv, call.chat_id)
            print(f'User({call.chat_id}) confirmation: {confirmation}')

            # User confirmed report
            if confirmation.lower() == self.__confirmation_words[0]:
                print(f'Confirmed strike for User({reported_user.id})...')
                strikes_count = self.strike_service.strike(reported_user.id, from_user_id=call.chat_id, reason=reason)

                print(f'Current strikes count for User({reported_user.id}): {strikes_count}')
                if strikes_count >= config.MAX_STRIKES_COUNT:
                    print(f'Ban User({reported_user.id})')
                    await self.chat_service.ban_user_in_chat(reported_user.id, config.BAN_PERIOD_IN_DAYS)

                await conv.send_message(msg.STRIKE_5)

            # User canceled report
            else:
                print(f'Canceled strike for User({reported_user.id})...')
                await conv.send_message(msg.STRIKE_6)

        print(f'User({call.chat_id}) has finished strike process')

    async def __report_user_input_loop(self, conv: Conversation, from_user_id: int) -> User:
        reported_user_name, reported_user = await self.__report_user_input(conv=conv, from_user_id=from_user_id)

        while not reported_user:
            # Bot cant't find user in chat
            print(f'Asked User({from_user_id}) to write the user username for strike (in loop)')
            await conv.send_message(msg.STRIKE_2)
            reported_user_name, reported_user = await self.__report_user_input(conv=conv, from_user_id=from_user_id)

        return reported_user

    async def __report_user_input(self, conv: Conversation, from_user_id: int) -> tuple:
        # User writes username
        reported_user_name_loop_rsp = await conv.get_response()
        reported_user_name: str = reported_user_name_loop_rsp.raw_text
        print(f'User({from_user_id}) reported User({reported_user_name})')

        # Search user in chat
        reported_user: User = await self.chat_service.find_member(reported_user_name)
        if reported_user:
            if reported_user.username == config.ADMIN_BOT_USERNAME:
                print(f'User({from_user_id}) tried to strike the ADMIN BOT')
                await conv.send_message(msg.STRIKE_2_1)
                reported_user = None
            elif self.strike_service.find_already_reported(
                    reported_user_id=reported_user.id,
                    from_user_id=from_user_id):
                print(f'User({from_user_id}) tried to strike the User({reported_user.id}) '
                      f'that he already reported (in loop)')

                await conv.send_message(msg.STRIKE_2_2.format(reported_user_name))
                reported_user = None

        return reported_user_name, reported_user

    async def __confirm_strike_loop(self, conv: Conversation, from_user_id: int) -> str:
        confirmation: str = await self.__confirm_strike(conv, from_user_id)
        while confirmation.lower() not in self.__confirmation_words:
            # Bot can't recognize the confirmation and ask to write it again
            print(f'Asked User({from_user_id}) to confirm strike again...')
            await conv.send_message(msg.STRIKE_4_2)
            confirmation: str = await self.__confirm_strike(conv, from_user_id)

        return confirmation

    async def __confirm_strike(self, conv: Conversation, from_user_id: int) -> str:
        # User writes the confirmation
        confirmation_resp = await conv.get_response()
        confirmation: str = confirmation_resp.raw_text
        print(f'User({from_user_id}) confirmation: {confirmation}')
        return confirmation
