from datetime import timedelta
from typing import Optional

from telethon import TelegramClient
from telethon.tl.types import User

from app.db import StrikeDao, Strike


class StrikeService:
    def __init__(self):
        print("Create StrikeService")
        self.dao = StrikeDao()

    def strike(self, reported_user_id: int, from_user_id: int, reason: str) -> int:
        print(f'Strike User({reported_user_id}) from User({from_user_id}) with the Reason({reason})')
        self.create(reported_user_id, from_user_id, reason)
        strikes_count = len(self.show_all(reported_user_id))
        print(f'User({reported_user_id}) has already {strikes_count} strikes')
        return strikes_count

    def create(self, reported_user_id: int, from_user_id: int, reason: str) -> Strike:
        print(f"Create strike(reported={reported_user_id}, from={from_user_id}, reason='{reason}')")

        a = Strike(reported_user_id=reported_user_id, from_user_id=from_user_id, reason=reason)
        self.dao.save(a)
        return a

    def find_already_reported(self, reported_user_id: int, from_user_id: int) -> Optional[Strike]:
        return self.dao.find_by_user_ids(reported_user_id=reported_user_id, from_user_id=from_user_id)

    def delete(self, reported_user_id: int, from_user_id: int):
        print(f"Delete all strike for User({reported_user_id}), from User({from_user_id})")
        self.dao.delete(reported_user_id, from_user_id)

    def show_all(self, reported_user_id: int) -> list:
        print(f"Show all strikes for User({reported_user_id})")
        return self.dao.find_all_by_reported_user_id(reported_user_id)

    def show_all_reasons(self, reported_user_id: int) -> list:
        print(f"Show all strike reasons for User({reported_user_id})")
        return [s.reason for s in self.show_all(reported_user_id)]


class ChatService:
    def __init__(self, bot: TelegramClient, chat_url: str):
        print(f"Create ChatService with chat_url = '{chat_url}'")
        self.bot: TelegramClient = bot
        self.chat_url: str = chat_url

    async def find_member(self, user_name: str) -> Optional[User]:
        print(f'Search for User({user_name}) in Chat({self.chat_url})')

        chat = await self.bot.get_entity(self.chat_url)
        print(f'Chat({chat.id})')

        user_name = user_name \
            .strip('@') \
            .replace(' ', '') \
            .lower()

        async for user in self.bot.iter_participants(chat):
            username = user.username.lower() if user.username else ''
            first_name = user.first_name.lower() if user.first_name else ''
            last_name = user.last_name.lower() if user.last_name else ''
            if username == user_name \
                    or (first_name + last_name).replace(' ', '') == user_name \
                    or (last_name + first_name).replace(' ', '') == user_name:
                print(f'Found User({user.id}) in Chat({chat.id})')
                return user

        print(f'NOT Found User({user_name}) in Chat({chat.id})')
        return None

    async def find_member_by_id(self, user_id: int) -> Optional[User]:
        print(f'Search for User({user_id}) in Chat({self.chat_url})')

        chat = await self.bot.get_entity(self.chat_url)
        print(f'Chat({chat.id})')

        async for user in self.bot.iter_participants(chat):
            if user.id == user_id:
                print(f'Found User({user_id}) in Chat({chat.id})')
                return user

        print(f'NOT Found User({user_id}) in Chat({chat.id})')
        return None

    async def ban_user_in_chat(self, user_id: int, days):
        print(f'Ban User({user_id})')
        chat = await self.bot.get_entity(self.chat_url)
        print(f'Chat({chat.id})')

        await self.bot.edit_permissions(
            chat.id,
            user_id,
            timedelta(days=days + 1),
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_polls=False,
            send_inline=False,
            embed_link_previews=False
        )

        print(f'User({user_id}) is banned in Chat({chat.id}) for {days} minutes')
