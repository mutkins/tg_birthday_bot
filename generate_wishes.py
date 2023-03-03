import openai
import time
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get('openai.api_key')


def write_wish(data):
    filename = f'wishes/{format(int(time.time()*1000))}.txt'
    with open(filename, 'a') as file:
        file.write(data)


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


if __name__ == '__main__':
    for i in range(500):
        # Get wish from openai
        wish = get_wish_from_openai()
        # write wish to file in folder
        write_wish(wish)


