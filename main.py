import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
import aioschedule
import asyncio
import database
import re
import tools
import configparser

# Read config file
config = configparser.ConfigParser()
config.read("settings.ini")

load_dotenv()
API_TOKEN = os.environ.get('test_tgBot_id')

# Configure logging
logging.basicConfig(filename="main.log", level=logging.ERROR, filemode="w",
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
                        "Например, /add @mikhail_utkins 19.10, @ivan_pupkins 22.11\n"
                        "<i>/del</i> - удалить участника. Например, /del @mikhail_utkins\n", parse_mode="HTML")


@dp.message_handler(commands=['add'])
async def add_members(message: types.Message):
    """
    This handler will be called when user sends `/add`
    """
    member_dict = dict()
    member_dict['members'] = list()
    # If there are many members in a string, put it into the dict and analyse each one
    members_string = str.split(message.get_args(), ',')
    report_string = ""
    is_success = True
    for item in members_string:
        # try to parse user's string
        nick_and_bday = tools.get_nickname_and_birthday_by_regex(item)
        # if we can parse user's string, create object for new member
        if nick_and_bday:
            new_member = database.Members(*nick_and_bday, message.chat.id)
            # send the dict to a database and get response
            res = new_member.add_member()
            # If method returns something - something went wrong
            if res:
                await message.reply("Внутренняя ошибка, попробуйте позже")
                raise Exception
            # Else - send response to user
            report_string += f"{new_member.get_nickname()}\n"

        else:
            await message.reply("Используй /help")
            log.info(f"User sent {message.get_args()}, it was not be able to parse it")
            is_success = False

    if is_success:
        await message.reply(report_string + "Будут поздравлены")


@dp.message_handler(commands=['list'])
async def send_list(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    members_list = database.get_members_of_chat(chat_id=message.chat.id)
    await message.reply(members_list)


@dp.message_handler(commands=['del'])
async def delete_member(message: types.Message):
    """
    This handler will be called when user sends `/del` command
    """
    nickname = tools.get_nickname_by_regex(message.get_args())
    if nickname:
        res = database.delete_member(nickname=nickname, chat_id=message.chat.id)
        if res:
            await message.reply(res)
        else:
            await message.reply(f"Участник {message.get_args()} удален")
    else:
        await message.reply("Используй /help")
        log.info(f"User sent {message.get_args()}, it was not be able to parse it")


async def send_wishes():
    members_list = database.get_members_who_have_birthday_today()
    for member in members_list:
        try:
            # Get wish path and photo path. It needs to delete wish and photo later
            wish_text_path = tools.get_random_wishpath_from_folder()
            photo_path = tools.get_random_imgpath_from_folder()

            # Get wish and photo from files
            with open(wish_text_path, 'r', encoding='cp1251') as f:
                wish_text = f.read()
            photo = InputFile(photo_path)

            # Send message to chat in async format
            if not database.is_member_wished(member):
                await bot.send_photo(
                    chat_id=member.get_chat_id(), photo=photo, caption=member.get_nickname() + " " + wish_text)
                # mark the wish the member to exclude case repeated wish (cause the error or something)
                database.mark_wished_member(member)
            else:
                log.error(f"The member with nickname = {member.nickname} and chat_id = {member.chat_id} "
                          f"is already wished in this year. May be something went wrong")
            # os.remove(photo_path)
            # os.remove(wish_text_path)
        except Exception as e:
            log.error(e)
            raise Exception


async def scheduler():
    aioschedule.every().day.at(config["General"]["time_to_send_wish"]).do(send_wishes)
    # aioschedule.every(5).seconds.do(send_wishes)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
