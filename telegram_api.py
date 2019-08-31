from time import sleep

import telebot
import pandas as pd
from telebot import types
from consts import MENU_MESSAGE, HEADERS
from mehir_api_client import MehirLameshtakenApi

bot = telebot.TeleBot("855617392:AAFpE8qd-SIwN5cLRbfMWsQIAxn80Df3KAI")
markup = types.ReplyKeyboardRemove(selective=False)
misteken_cls = MehirLameshtakenApi()
misteken_cls.fetch_query()
results = misteken_cls.get_results()
results_df = pd.DataFrame(results)
all_cites = results_df["יישוב"].unique()
all_permits = results_df["מצב היתר"].unique()
all_neighborhoods = results_df["שכונה"].unique()
project_status = results_df["מצב פרויקט"].unique()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "היי אני דויד ואני יעזור לך למצוא הגרלה במחיר למשתכן \U000026C4",
                     reply_markup=markup)
    bot.send_message(message.chat.id, MENU_MESSAGE, reply_markup=markup)


def create_menu(message, message_list, menu_list):
    markup_menu = types.ReplyKeyboardMarkup(row_width=8)
    items = [types.KeyboardButton(i) for i in menu_list]
    markup_menu.add(*items)
    for message_row in message_list[:-1]:
        bot.send_message(message.chat.id, message_row)

    bot.send_message(message.chat.id, message_list[-1], reply_markup=markup_menu)


def handle_menu_repaly(msg, key):
    headers = HEADERS
    new_results = list(filter(lambda x: x[key] == msg.text, results))
    if len(new_results) != 0:
        index = 0
        for row in new_results:
            output_string = ""
            for col in headers:
                output_string += "{}: {}\n".format(col, row[col])

            if index == 30:
                bot.send_message(msg.chat.id, "מנוחה קצרה וחוזרים להפציץ :)", reply_markup=markup)
                sleep(40)

                index = 0

            index += 1
            bot.send_message(msg.chat.id, output_string, reply_markup=markup)
    else:
        bot.send_message(msg.chat.id, "סורי אין לי כרגע תוצאות על חיפוש זה", reply_markup=markup)


# ------------------------------------projects status---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in project_status)
def get_project_status_info(msg):
    key = "מצב פרויקט"
    handle_menu_repaly(msg, key)


@bot.message_handler(commands=['project_status'])
def show_project_status_menu(message):
    create_menu(
        message,
        ["עכשיו יוצגו בפניך כל סוגי מצבי הפרוייקט", "בחר סטטוס בבקשה"],
        project_status
    )


# -------------------------------------neighborhoods---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in all_neighborhoods)
def get_neighborhoods_info(msg):
    key = "שכונה"
    handle_menu_repaly(msg, key)


@bot.message_handler(commands=['neighborhoods'])
def show_neighborhoods_menu(message):
    create_menu(
        message,
        ["עכשיו יוצגו בפניך כל השכונות", "בחר שכונה בבקשה"],
        all_neighborhoods
    )


# -------------------------------------PERMITS---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in all_permits)
def get_permits_info(msg):
    key = "מצב היתר"
    handle_menu_repaly(msg, key)


@bot.message_handler(commands=['permit_status'])
def show_permit_menu(message):
    create_menu(
        message,
        ["עכשיו יוצגו בפניך את כל סוגי מצב היתר", "בחר מצב היתר בבקשה"],
        all_permits
    )


# -------------------------------------CITYS---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in all_cites)
def get_city_info(msg):
    key = "יישוב"
    handle_menu_repaly(msg, key)


@bot.message_handler(commands=['city'])
def show_menu(message):
    create_menu(
        message,
        ["עכשיו יוצגו בפניך את כל הערים שקיימות כרגע בהגרלות שרלוונטיות", "בחר עיר בבקשה"],
        all_cites
    )


if __name__ == "__main__":
    bot.polling()
