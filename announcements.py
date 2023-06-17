from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

from tg_bot.utils import NotificationTypes
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
from locales.localizer import Localizer
from threading import Thread
from logging import getLogger
import requests
import json
import os
import time


logger = getLogger("FPC.announcements")
localizer = Localizer()
_ = localizer.translate


def get_last_tag() -> str | None:
    """
    Загружает тег последнего объявления из кэша.

    :return: тег последнего объявления или None, если его нет.
    """
    if not os.path.exists("storage/cache/announcement_tag.txt"):
        return None
    with open("storage/cache/announcement_tag.txt", "r", encoding="UTF-8") as f:
        data = f.read()
    return data


REQUESTS_DELAY = 600
LAST_TAG = get_last_tag()


def save_last_tag():
    """
    Сохраняет тег последнего объявления в кэш.
    """
    global LAST_TAG
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")
    with open("storage/cache/announcement_tag.txt", "w", encoding="UTF-8") as f:
        f.write(LAST_TAG)



    


def download_photo(url: str) -> bytes | None:
    """
    Загружает фото по URL.

    :param url: URL фотографии.

    :return: фотографию в виде массива байтов.
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except:
        return None
    return response.content


# Разбор данных объявления
def get_notification_type(data: dict) -> NotificationTypes:
    """
    Находит данные о типе объявления.
    0 - реклама.
    1 - объявление.
    Другое - критическое объявление.

    :param data: данные объявления.

    :return: тип уведомления.
    """
    types = {
        0: NotificationTypes.ad,
        1: NotificationTypes.announcement
    }
    return types[data.get("type")] if data.get("type") in types else NotificationTypes.critical


def get_photo(data: dict) -> bytes | None:
    """
    Загружает фотографию по ссылке, если она есть в данных об объявлении.

    :param data: данные объявления.

    :return: фотографию в виде массива байтов или None, если ссылка на фото не найдена или загрузка не удалась.
    """
    if not (photo := data.get("ph")):
        return None
    return download_photo(u"{}".format(photo))


def get_text(data: dict) -> str | None:
    """
    Находит данные о тексте объявления.

    :param data: данные объявления.

    :return: текст объявления или None, если он не найден.
    """
    if not (text := data.get("text")):
        return None
    return u"{}".format(text)


def get_pin(data: dict) -> bool:
    """
    Получает информацию о том, нужно ли закреплять объявление.

    :param data: данные объявления.

    :return: True / False.
    """
    return bool(data.get("pin"))


def get_keyboard(data: dict) -> K | None:
    """
    Получает информацию о клавиатуре и генерирует ее.
    Пример клавиатуры:

    :param data: данные объявления.

    :return: объект клавиатуры или None, если данные о ней не найдены.
    """
    if not (kb_data := data.get("kb")):
        return None

    kb = K()
    try:
        for row in kb_data:
            buttons = []
            for btn in row:
                btn_args = {u"{}".format(i): u"{}".format(btn[i]) for i in btn}
                buttons.append(B(**btn_args))
            kb.row(*buttons)
    except:
        return None
    return kb


