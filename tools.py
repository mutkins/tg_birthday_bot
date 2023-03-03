import os
import random


def get_random_imgpath_from_folder():
    images_list = os.listdir("img")
    r = random.randrange(0, images_list.__len__())
    return "img/" + images_list[r]


def get_random_wishpath_from_folder():
    wishes_list = os.listdir("wishes")
    r = random.randrange(0, wishes_list.__len__())
    return "wishes/" + wishes_list[r]

