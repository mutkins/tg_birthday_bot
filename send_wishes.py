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
def get_wish():
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
def get_image(wish_text):
    response = openai.Image.create(
        prompt=f"Забавная открытка {wish_text}",
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']


# sending wish-message
def sendMessage(chat_id, text="OK", image_url=""):
    url = bot_URL + "sendPhoto"
    answer = {'chat_id': chat_id, 'photo': image_url, 'parse_mode': 'HTML', 'caption': f"<b>{text}</b>"}
    log.debug(f"MESSAGE TO SEND {url}, {answer}")
    requests.post(url, json=answer)


for member in database.get_birthday_boys():

    wishText = member.nickname + get_wish()
    wishImage = get_image(wish_text=wishText)
    sendMessage(chat_id=member.chat_id, text=wishText, image_url=wishImage)

print('')



