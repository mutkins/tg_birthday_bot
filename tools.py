import os
import random


def get_random_image_from_folder():
    imagesList = os.listdir("img")
    r = random.randrange(0, imagesList.__len__())
    return "img/" + imagesList[r]
