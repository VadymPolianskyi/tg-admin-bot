import telebot
from flask import Flask, request
from telethon import TelegramClient, events
from telethon.events import ChatAction
from telethon.tl.custom import Message
from telethon.tl.types import PeerChannel, PeerUser

from app.config import config
from app.handler.start import StartHandler
from app.handler.strike import StrikeCallbackHandler
from app.service import StrikeService, ChatService

server = Flask(__name__)

bot = TelegramClient('teamo', config.API_ID, config.API_HASH).start(bot_token=config.BOT_API_KEY)

strike_service = StrikeService()
chat_service = ChatService(bot, config.CHAT_URL)

#### HANDLERS ####
start_handler = StartHandler(chat_service)

#### CALLBACK ####
strike_callback_handler = StrikeCallbackHandler(bot, strike_service=strike_service, chat_service=chat_service)


@bot.on(events.NewMessage(pattern='/start|/help|/menu'))
async def main(message):
    await start_handler.handle(message)


@bot.on(events.CallbackQuery(data=StrikeCallbackHandler.MARKER))
async def strike_handler(call):
    await strike_callback_handler.handle(call)


@bot.on(events.chataction.ChatAction(chats=PeerChannel(channel_id=config.CHAT_ID)))
async def join_requests_handler(event: ChatAction.Event):
    if event.user_joined or event.user_added or event.user_left:
        print(event)
        await event.delete()
        print("Deleted")

    ##############################
    #       APP LAUNCHING        #
    ##############################


bot_ = telebot.TeleBot(config.BOT_API_KEY)


@server.route('/' + config.BOT_API_KEY, methods=['POST'])
def get_message():
    import json
    json_string = request.get_data().decode('utf-8')
    print(f"Webhook data: {json_string}")
    msg: dict = json.load(json_string)
    msg_txt = msg['message']['text']
    if msg_txt == "/menu" or msg_txt == "/start" or msg_txt == "/help":
        from_id = msg['message']['from']['id']
        message_id = msg['message']['id']
        events.NewMessage.Event(Message(id=message_id, peer_id=PeerUser(from_id), from_id=from_id, message=msg_txt))
    bot.run_until_disconnected()
    return "!", 200


@server.route("/")
def webhook():
    print("Bot started...")
    bot_.remove_webhook()
    bot_.set_webhook(url=config.WEBHOOK_URL + config.BOT_API_KEY)
    bot.run_until_disconnected()
    return "!", 200


if __name__ == "__main__":
    server.run(host=config.SERVER_HOST, port=config.SERVER_PORT)
