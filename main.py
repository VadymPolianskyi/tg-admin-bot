from flask import Flask
from telethon import TelegramClient, events

from app.config import config
from app.handler.start import StartHandler
from app.handler.strike import StrikeCallbackHandler
from app.service import StrikeService, ChatService

server = Flask(__name__)

bot = TelegramClient('teamo', config.API_ID, config.API_HASH).start(bot_token=config.BOT_API_KEY)

strike_service = StrikeService()
chat_service = ChatService(bot, "https://t.me/DigitalNomadsComunity")

#### HANDLERS ####
start_handler = StartHandler(chat_service)

#### CALLBACK ####
strike_callback_handler = StrikeCallbackHandler(bot, strike_service=strike_service, chat_service=chat_service)


@bot.on(events.NewMessage(pattern='/start|/help|/menu'))
async def main(message):
    await start_handler.handle(message)


#################################
#       GENERAL CALLBACK        #
#################################

@bot.on(events.CallbackQuery(data=StrikeCallbackHandler.MARKER))
async def strike_handler(call):
    await strike_callback_handler.handle(call)


##############################
#       APP LAUNCHING        #
##############################

@server.route("/")
def webhook():
    print("Bot started...")
    bot.run_until_disconnected()
    return "!", 200


if __name__ == "__main__":
    server.run(host=config.SERVER_HOST, port=config.SERVER_PORT)
