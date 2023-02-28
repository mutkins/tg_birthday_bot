import openai
import os
import logging
from dotenv import load_dotenv
import requests
import database

logging.basicConfig(filename="send_wishes.log", level=logging.DEBUG, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

load_dotenv()
openai.api_key = os.environ.get('openai.api_key')
bot_URL = os.environ.get('bot_URL')


# Making a birthday wish
def get_wish_from_openai():
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Напиши короткое забавное поздравление с днем рождения",
        temperature=0.9,
        max_tokens=256,
        top_p=0.8,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response['choices'][0]['text']


# making image for the wish
def get_image_from_openai(wish_text):
    response = openai.Image.create(
        prompt=f"Забавная открытка {wish_text}",
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']


# sending wish-message
def send_message(chat_id, text="OK", image_url=""):
    url = bot_URL + "sendPhoto"
    # answer = {'chat_id': chat_id, 'photo': image_url, 'parse_mode': 'HTML', 'caption': f"<b>{text}</b>"}
    answer = {'chat_id': chat_id, 'parse_mode': 'HTML', 'caption': f"<b>{text}</b>"}

    multipart_form_data = {
    'upload': ('custom_file_name.zip', image_url),
    'action': (None, 'store'),
    'path': (None, '/path1')
    }
    files1 = [('files', open('00000-30_k_euler_292211283_funny-image-happy-birthday-cute-a.png', 'rb'))]
    log.debug(f"MESSAGE TO SEND {url}, {answer}")
    requests.post(url, json=answer, files=files1)


# Getting the members list who was born today
membersList = database.get_birthday_boys()
for member in membersList:
    try:
        # for each member generate wish text and image and send it to chat
        # wishText = member.nickname + get_wish_from_openai()
        # wishImage = get_image_from_openai(wish_text=wishText)
        wishText = member.nickname + "Happy birthday!"
        wishImage = open('00000-30_k_euler_292211283_funny-image-happy-birthday-cute-a.png', 'rb')
        send_message(chat_id=member.chat_id, text=wishText, image_url=wishImage)
    except Exception as e:
        log.error(e)
        raise Exception




