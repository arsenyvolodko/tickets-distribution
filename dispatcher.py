import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    exit("No token provided")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
