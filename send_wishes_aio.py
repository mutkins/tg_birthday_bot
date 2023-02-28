import openai
import os
import logging
from dotenv import load_dotenv
import requests
import database
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import aioschedule

load_dotenv()
openai.api_key = os.environ.get('openai.api_key')
bot_URL = os.environ.get('bot_URL')
API_TOKEN = os.environ.get('bot_token')

# Configure logging
logging.basicConfig(filename="send_wishes_aio.log", level=logging.DEBUG, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def noon_print():
    print("It's noon!")


async def scheduler():
    aioschedule.every(5).seconds.do(noon_print)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)