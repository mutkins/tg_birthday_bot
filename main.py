import openai
import os
import logging
from dotenv import load_dotenv
import requests
import database
from aiogram import Bot, Dispatcher, executor, types
import aioschedule
import asyncio
import time
import database
import re

load_dotenv()
openai.api_key = os.environ.get('openai.api_key')
bot_URL = os.environ.get('bot_URL')
API_TOKEN = os.environ.get('bot_token')

# Configure logging
logging.basicConfig(filename="main.log", level=logging.DEBUG, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Нейро-пух поздравляет участников чата с днем рождения\n"
                        "Команды:\n"
                        "<i>/list</i> - показать все записанные др\n"
                        "<i>/add</i> - добавить др участника. Несколько участников пишутся через запятую\n"
                        "Например, /add @mikhail_utkins 19.10, @ivan_pupkins 22.11\n")


@dp.message_handler(commands=['add'])
async def add_members(message: types.Message):
    """
    This handler will be called when user sends `/add`
    """
    # REFACTOR IT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    member_dict = dict()
    member_dict['members'] = list()
    # If there are many members in a string, put it into the dict and analyse each one
    members_string = str.split(message.get_args(), ',')
    for el in members_string:
        # just in case check a string for this format: "@ivan_pupkins 22.11"
        result = re.search(r'(?i)@\S+\s[0-9][0-9].[0-9][0-9]', el)
        if result:
            # If everything is ok, separate nickname and birthday
            nickname = re.search(r'(?i)@\S+', result.group(0))
            birthday = re.search(r'[0-9][0-9].[0-9][0-9]', result.group(0))
            try:
                nickname = nickname.group(0)
                # Try to convert birthday string to python date type
                birthday = birthday.group(0)
            except ValueError as e:
                # If there are any errors with converting, say it to user and finish function
                log.debug(f"ERROR with decode date format {e}")
                await message.reply(str(e.args) + "\n Используй /help")

            # put nickname and his birthday to a dict
            member_dict['members'].append({'nickname': nickname, 'birthday': birthday,
                                           'chat_id': message.chat.id})
    # send the dict to a database and get response
    res = database.add_members(member_dict)
    # send response to user
    await message.reply(res)


@dp.message_handler(commands=['list'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    members_list = database.get_members_of_chat(chat_id=message.chat.id)
    await message.reply(members_list)


async def send_wishes():
    print("SEND")
    url = bot_URL + "sendPhoto"
    # answer = {'chat_id': chat_id, 'photo': image_url, 'parse_mode': 'HTML', 'caption': f"<b>{text}</b>"}
    # answer = {'chat_id': chat_id, 'parse_mode': 'HTML', 'caption': f"<b>{text}</b>"}

    # multipart_form_data = {
    #     'upload': ('custom_file_name.zip', image_url),
    #     'action': (None, 'store'),
    #     'path': (None, '/path1')
    # }
    files1 = [('files', open('00000-30_k_euler_292211283_funny-image-happy-birthday-cute-a.png', 'rb'))]
    # log.debug(f"MESSAGE TO SEND {url}, {answer}")
    await bot.send_photo(chat_id='-879913730', photo='https://wp-s.ru/wallpapers/9/18/438540442363429/izgib-reki-na-fone-zakata.jpg')


async def scheduler():
    aioschedule.every(5).seconds.do(send_wishes)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
