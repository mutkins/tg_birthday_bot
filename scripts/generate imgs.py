import openai
import time
import os
from dotenv import load_dotenv
import requests

load_dotenv()
openai.api_key = os.environ.get('openai.api_key')


def write_img(data):
    filename = f'img/{format(int(time.time() * 1000))}.png'
    with open(filename, 'wb') as file:
        file.write(data)


def get_image_from_openai():
    response = openai.Image.create(
        prompt=f"Забавная открытка с днем рождения",
        n=1,
        size="512x512"
    )
    return response['data'][0]['url']


def get_img_file_from_url(url):
    r = requests.get(url)
    return r.content


if __name__ == '__main__':
    for i in range(10):
        # get image url from openai
        img_url = get_image_from_openai()
        # make a binary object from image url
        img = get_img_file_from_url(img_url)
        # write image to folder
        write_img(img)
