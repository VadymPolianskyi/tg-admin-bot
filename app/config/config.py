import os

BOT_API_KEY = os.environ.get("BOT_API_KEY")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = os.environ.get("DB_NAME")
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DB_TABLE_STRIKE = os.environ.get("DB_TABLE_STRIKE")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

MAX_STRIKES_COUNT = int(os.environ.get("MAX_STRIKES_COUNT"))

SERVER_HOST = os.environ.get('HOST', "0.0.0.0")
SERVER_PORT = int(os.environ.get('PORT', 5000))

CHAT_URL = os.environ.get('CHAT_URL')
CHAT_ID = int(os.environ.get('CHAT_ID'))

ADMIN_BOT_USERNAME = 'ChatAdminDMBot'
BAN_PERIOD_IN_DAYS = int(os.environ.get("BAN_PERIOD_IN_DAYS"))
