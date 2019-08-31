import sys
import logging
import telebot
import pandas as pd
from time import sleep
from telebot import types
from consts import MENU_MESSAGE, HEADERS
from mehir_api_client import MehirLameshtakenApi
from tools import retry, sort_list_of_dict_by_key

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

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


def log_user_actions(function_name, user_first_name, user_last_name, user_id, msg_text):
    """
    :param function_name - string:
    :param user_first_name - string:
    :param user_last_name - string:
    :param user_id - string:
    :param msg_text- string:
    """
    root.info("{function_name} - {first_name} - {last_name} - {user_id}- {msg_text}".format(
        function_name=function_name,
        first_name=user_first_name,
        last_name=user_last_name,
        user_id=user_id,
        msg_text=msg_text
    ))


def post_info(msg, this_function_name):
    log_user_actions(this_function_name, msg.chat.first_name, msg.chat.last_name, msg.chat.id, msg.text)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    """
    trigger by user input ['start', 'hello']
    :param message:
    :return string of menus actions:
    """
    bot.send_message(message.chat.id, "היי אני דויד ואני יעזור לך למצוא הגרלה במחיר למשתכן \U000026C4",
                     reply_markup=markup)
    bot.send_message(message.chat.id, MENU_MESSAGE, reply_markup=markup)


def _create_menu(message, message_list, menu_list):
    markup_menu = types.ReplyKeyboardMarkup(row_width=8)
    items = [types.KeyboardButton(i) for i in menu_list]
    markup_menu.add(*items)
    for message_row in message_list[:-1]:
        bot.send_message(message.chat.id, message_row)

    bot.send_message(message.chat.id, message_list[-1], reply_markup=markup_menu)


@retry(ExceptionToCheck=Exception, logger=root)
def _handle_menu_repaly(msg, key):
    headers = HEADERS
    new_results = list(filter(lambda x: x[key] == msg.text, results))
    sorted_new_results = sort_list_of_dict_by_key(new_results, "תאריך ביצוע הגרלה")
    if len(sorted_new_results) != 0:
        break_index = 0
        end_of_response_index = 0
        for row in sorted_new_results:
            output_string = ""
            for col in headers:
                output_string += "{}: {}\n".format(col, row[col])

            if break_index == 30:
                bot.send_message(msg.chat.id, "מנוחה קצרה וחוזרים להפציץ :)", reply_markup=markup)
                sleep(40)
                break_index = 0
            if end_of_response_index == 45:
                root.info("message of stops because to mush response")
                return

            break_index += 1
            end_of_response_index += 1
            bot.send_message(msg.chat.id, output_string, reply_markup=markup)
    else:
        bot.send_message(msg.chat.id, "סורי אין לי כרגע תוצאות על חיפוש זה", reply_markup=markup)


# ------------------------------------projects status---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in project_status)
def get_project_status_info(msg):
    """
    trigger by user input of all unique list of project_status
    :param msg - Message object:
    :return response action:
    """
    key = "מצב פרויקט"
    this_function_name = sys._getframe().f_code.co_name
    post_info(msg, this_function_name)
    _handle_menu_repaly(msg, key)


@bot.message_handler(commands=['project_status'])
def show_project_status_menu(message):
    """
    triggered by user action /project_status
    :param message - Message object:
    :return menu action:
    """
    _create_menu(
        message,
        ["עכשיו יוצגו בפניך כל סוגי מצבי הפרוייקט", "בחר סטטוס בבקשה"],
        project_status
    )


# -------------------------------------neighborhoods---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in all_neighborhoods)
def get_neighborhoods_info(msg):
    """
    trigger by user input of all unique list of all_neighborhoods
    :param msg - Message object:
    :return menu action:
    """
    key = "שכונה"
    this_function_name = sys._getframe().f_code.co_name
    post_info(msg, this_function_name)
    _handle_menu_repaly(msg, key)


@bot.message_handler(commands=['neighborhoods'])
def show_neighborhoods_menu(message):
    """
    triggered by user action /neighborhoods
    :param message - Message object:
    :return menu action:
    """
    _create_menu(
        message,
        ["עכשיו יוצגו בפניך כל השכונות", "בחר שכונה בבקשה"],
        all_neighborhoods
    )


# -------------------------------------PERMITS---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in all_permits)
def get_permits_info(msg):
    """
    trigger by user input of all unique list of all_permits
    :param msg - Message object:
    :return menu action:
    """
    key = "מצב היתר"
    this_function_name = sys._getframe().f_code.co_name
    post_info(msg, this_function_name)
    _handle_menu_repaly(msg, key)


@bot.message_handler(commands=['permit_status'])
def show_permit_menu(message):
    """
    triggered by user action /permit_status
    :param message - Message object:
    :return menu action:
    """
    _create_menu(
        message,
        ["עכשיו יוצגו בפניך את כל סוגי מצב היתר", "בחר מצב היתר בבקשה"],
        all_permits
    )


# -------------------------------------CITYS---------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text in all_cites)
def get_city_info(msg):
    """
    trigger by user input of all unique list of all_cites
    :param msg - Message object:
    :return menu action:
    """
    key = "יישוב"
    this_function_name = sys._getframe().f_code.co_name
    post_info(msg, this_function_name)
    _handle_menu_repaly(msg, key)


@bot.message_handler(commands=['city'])
def show_menu(message):
    """
    triggered by user action /city
    :param message - Message object:
    :return menu action:
    """
    _create_menu(
        message,
        ["עכשיו יוצגו בפניך את כל הערים שקיימות כרגע בהגרלות שרלוונטיות", "בחר עיר בבקשה"],
        all_cites
    )


if __name__ == "__main__":
    bot.polling()
