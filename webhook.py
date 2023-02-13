import os
from flask import Flask
from flask_sslify import SSLify
import requests
from flask import request, Response
from flask import jsonify
import json
import logging
import regex_spm
import re
import database
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename="main.log", level=logging.DEBUG, filemode="w", format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

app = Flask(__name__)
# sslify = SSLify(app)

# Getting secrets from environment
bot_URL = os.environ.get('bot_URL')
webhook = os.environ.get('webhook')

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # if request POST - decompose update message
        log.debug(f"NEW MESSAGE FROM BOT {request}")
        r = request.get_json()
        log.debug(f"DECODE MESSAGE {r}")
        # extract chat_id and 'message' block
        chat_id = r.get('message', {}).get('chat', {}).get('id')
        income_message = r.get('message', {}).get('text')
        # if update message doesn't content chat_it or 'message' block - ignore update message
        if chat_id and income_message:
            log.debug(f"SENDING MESSAGE to chat {chat_id}")
            # recognise command. User must send /command then parameters.
            match regex_spm.fullmatch_in(income_message):
                # First step - RegEx checks command at the start of a sentence, and we choose the correct branch

                # User asks help
                case r'(?i)^/help':
                    sendMessage(chat_id, "Нейро-пух поздравляет участников чата с днем рождения\n"
                                     "Команды:\n"
                                     "<i>/list</i> - показать все записанные др\n"
                                     "<i>/add</i> - добавить др участника. Несколько участников пишутся через запятую"
                                         "Например, /add @mikhail_utkins 19.10.1990, @ivan_pupkins 22.11.1999\n")
                    return Response(status=200)

                # User asks list of members
                case r'(?i)^/list.*':
                    membersList = database.get_members_of_chat(chat_id=chat_id)
                    sendMessage(chat_id, membersList)
                    return Response(status=200)

                # User wants to add members to the list
                # This regExp checks this format "/add @mikhail_utkins 19.10.1990, @ivan_pupkins 22.11.1999"
                case r'(?i)^/add\s(@\S+\s[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9]((,(\s)*)|$))+':
                    memberDict = dict()
                    memberDict['members'] = list()
                    # If there are many members in a string, put it into the dict and analyse each
                    membersString = str.split(income_message, ',')
                    for el in membersString:
                        # just in case check a string for this format: "@ivan_pupkins 22.11.1999"
                        result = re.search(r'(?i)@\S+\s[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9]', el)
                        if result:
                            # If everything is ok, separate nickname and birthday
                            nickname = re.search(r'(?i)@\S+', result.group(0))
                            birthday = re.search(r'[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9]', result.group(0))
                            try:
                                nickname = nickname.group(0)
                                # Try to convert birthday string to python date type
                                birthday = datetime.strptime(birthday.group(0), "%d.%m.%Y")
                            except ValueError as e:
                                # If there are any errors with converting, say it to user and finish function
                                log.debug(f"ERROR with decode date format {e}")
                                sendMessage(chat_id, str(e.args) + "\n Используй /help")
                                return Response(status=200)

                            # put nickname and his birthday to a dict
                            memberDict['members'].append({'nickname': nickname, 'birthday': birthday,
                                                          'chat_id': chat_id})

                    # send the dict to a database and get response
                    res = database.add_members(memberDict)
                    # send response to user
                    sendMessage(chat_id, res)
                    return Response(status=200)

                # User sends junk
                case _:
                    sendMessage(chat_id, "Используй /help")
                    return Response(status=200)
        else:
            log.error(f"update message wasn't recognised")
            return Response(status=200)
    else:
        # if method == GET just send text
        return "<h1>HELLO</h1>"


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sendMessage(chat_id, text="OK"):
    url = bot_URL + "sendMessage"

    answer = {'chat_id': chat_id,
              'photo': "",
              'parse_mode': 'HTML',
              'text': text}
    log.debug(f"MESSAGE TO SEND {url}, {answer}")
    requests.post(url, json=answer)


def setWebhook():
    url = bot_URL + "setWebhook?url=" + webhook + "&drop_pending_updates=true"
    requests.get(url)


if __name__ == '__main__':
    setWebhook()
    app.run("0.0.0.0")

