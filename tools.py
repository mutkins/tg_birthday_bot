import os
import random
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="main.log", level=logging.INFO, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")


def get_random_imgpath_from_folder():
    images_list = os.listdir("img")
    r = random.randrange(0, images_list.__len__())
    return "img/" + images_list[r]


def get_random_wishpath_from_folder():
    wishes_list = os.listdir("wishes")
    r = random.randrange(0, wishes_list.__len__())
    return "wishes/" + wishes_list[r]


def get_nickname_and_birthday_by_regex(raw_string):
    # just in case check a string for this format: "@ivan_pumpkin 22.11"
    result = re.search(r'(?i)@\S+\s[0-9][0-9].[0-9][0-9]', raw_string)
    if result:
        # If everything is ok, separate nickname and birthday
        nickname = re.search(r'(?i)@\S+', result.group(0))
        birthday = re.search(r'[0-9][0-9].[0-9][0-9]', result.group(0))
        if is_date_format_ok(birthday.group(0)):
            return nickname.group(0), birthday.group(0)
        else:
            return None
    else:
        return None


def get_nickname_by_regex(raw_string):
    nickname = re.search(r'(?i)@\S+', raw_string)
    if nickname:
        return nickname.group(0)
    else:
        return None


def is_date_format_ok(date_str):
    try:
        date_object = datetime.strptime(date_str, "%d.%m")
        return True
    except Exception as e:
        log.error(e)
        return False
