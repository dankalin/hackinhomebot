import logging
import telebot
import datetime
import os
import psycopg2
import requests
from telebot import types
from requests import get
import pandas as pd
from flask import Flask, request

TOKEN_DEV = '5204051376:AAH94zpZg12D7cO-bJ5qQflNL84WD_PvqxQ'
bot = telebot.TeleBot(TOKEN_DEV)
APP_URL = f'https://tgbotstankinn.herokuapp.com//{TOKEN_DEV}'
logger = telebot.logger
logger.setLevel(logging.DEBUG)
server = Flask(__name__)
connection = psycopg2.connect(user="rwgxiplwjymghb",
                              password="55a394213bf3b89536f1da066cc178be3f84d91a1243a8fdeb2271f12c33ccbb",
                              host="ec2-176-34-215-248.eu-west-1.compute.amazonaws.com",
                              port="5432",
                              database="d7o6e6fqi9kmir")
cursor = connection.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id,
                           f'Привет! Давай знакомиться, Я бот-СТАНКИН 🤖. А ты наверное @{message.from_user.username}, если так, то приятно познакомиться 🤝!\nАвторизуйся пожалуйста 🔑, чтобы быть всегда на связи со мной!\nДля авторизации введи свой пин код ниже: ')
    bot.send_sticker(chat_id=message.from_user.id,
                     sticker="CAACAgIAAxkBAAEEoR9icv56nRbYv0q6ebUZjyMRm_dXnQACSxYAAqllmEsCG4_D7LmPfSQE")
    bot.register_next_step_handler(msg, askPin)


def askPin(message):
    user_id = message.chat.id
    cursor.execute(f"""SELECT tg_id from USERS where tg_id = '{str(user_id)}'""")
    proverka_tg_id = cursor.fetchone()
    if not proverka_tg_id:
        global entering_pin
        chat_id = message.chat.id
        entering_pin = message.text
        cursor.execute(f"""SELECT pin from USERS where pin = '{str(entering_pin)}'""")
        result_pin = cursor.fetchone()
        if result_pin:
            cursor.execute(f"""SELECT role_id from USERS where pin = '{str(entering_pin)}'""")
            role = cursor.fetchone()[0]
            if role == '1' or role == '0':
                cursor.execute(f"""SELECT fullname, groupp from USERS where pin = '{str(entering_pin)}'""")
                full_name_group = ', '.join(cursor.fetchone())
                start_keyboard = types.InlineKeyboardMarkup()
                Yes_answer = types.InlineKeyboardButton(text='Да', callback_data='Yes')
                No_answer = types.InlineKeyboardButton(text='Нет', callback_data='No')
                start_keyboard.add(Yes_answer, No_answer)
                bot.send_message(message.chat.id,
                                 f'А вы точно {full_name_group} 🤨 ? В наше время кибер-безопасность очень важна, поэтому я должен убедиться, что это имеено вы 😊',
                                 reply_markup=start_keyboard)
            else:
                cursor.execute(f"""SELECT fullname from USERS where pin = '{str(entering_pin)}'""")
                full_name = cursor.fetchone()[0]
                start_keyboard = types.InlineKeyboardMarkup()
                Yes_answer = types.InlineKeyboardButton(text='Да', callback_data='Yes')
                No_answer = types.InlineKeyboardButton(text='Нет', callback_data='No')
                start_keyboard.add(Yes_answer, No_answer)
                bot.send_message(message.chat.id,
                                 f'А вы точно {full_name} 🤨 ? В наше время кибер-безопасность очень важна, поэтому я должен убедиться, что это имеено вы 😊',
                                 reply_markup=start_keyboard)

        else:
            msg = bot.send_message(chat_id, "Ваш пин-код неверный ❌ ! Пожалуйста введите верный пин-код")
            bot.send_sticker(chat_id=message.from_user.id,
                             sticker="CAACAgIAAxkBAAEEoSFicv6UqHg9efjKpeS5LkC4INvaJQAC9RoAArm3mUto-qCXoivVtiQE")
            bot.register_next_step_handler(msg, askPin)
    else:
        bot.send_message(message.chat.id, "Вы уже авторизованны ✅!")
        help_button(message)


@bot.message_handler(commands=['help'])
def help_button(message):
    cursor.execute(f"""SELECT role_id from USERS where tg_id = '{message.chat.id}'""")
    role = cursor.fetchone()[0]
    if role == '1':
        bot.send_message(message.chat.id, "Смотри что я могу 🌚:\n"
                                          "🔍 Help - показать информацию о все доступных кнопках\n"
                                          "🗺 Расписание - показать расписание \n"
                                          "📙 Модульный журнал - ссылка на модульный журнал\n"
                                          "📖 Получение модуля - список того, что нужно сдать для получения модуля и быть успешным!\n"
                                          "🖥 ЭОС - ссылка на ЭОС\n"
                                          "👩🏻 Инструмент старосты  - объявление для своей группы\n"
                                          "👶 Инструкции для первокурсника - полезная информация для первокурсника")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        item8 = types.KeyboardButton("🔍 Help")
        item2 = types.KeyboardButton("🗺 Расписание")
        item3 = types.KeyboardButton("📙 Модульный журнал")
        item4 = types.KeyboardButton("📞 Контакты преподавателей")
        item5 = types.KeyboardButton("📖 Получение модуля")
        item6 = types.KeyboardButton("🖥 ЭОС")
        item7 = types.KeyboardButton("👩🏻 Инструмент старосты")
        item1 = types.KeyboardButton("👶 Инструкции для первокурсника")
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
    elif role == '0':
        bot.send_message(message.chat.id, "Смотри что я могу 🌚:\n"
                                          "🔍 Help - показать информацию о все доступных кнопках\n"
                                          "🗺 Расписание - показать расписание \n"
                                          "📙 Модульный журнал - ссылка на модульный журнал\n"
                                          "📞 Контакты преподавателей - почта, телефон и ссылка на профиль преподавателя в ЭОС\n"
                                          "📖 Получение модуля - список того, что нужно сдать для получения модуля и быть успешным!\n"
                                          "🖥 ЭОС - ссылка на ЭОС\n"
                                          "👶 Инструкции для первокурсника - полезная информация для первокурсника")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        item1 = types.KeyboardButton("🔍 Help")
        item2 = types.KeyboardButton("🗺 Расписание")
        item3 = types.KeyboardButton("📙 Модульный журнал")
        item4 = types.KeyboardButton("📞 Контакты преподавателей")
        item5 = types.KeyboardButton("📖 Получение модуля")
        item6 = types.KeyboardButton("🖥 ЭОС")
        item7 = types.KeyboardButton("👶 Инструкции для первокурсника")
        markup.add(item7, item2, item3, item4, item5, item6, item1)
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Смотри что я могу 🌚:\n"
                                          "🔍 Help - показать информацию о все доступных кнопках\n"
                                          "📖 Объявление для группы - сделать объявление для группы!")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton("🔍 Help")
        item2 = types.KeyboardButton("Объявление для группы")
        markup.add(item2, item1)
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data)
def enter_pin(callback):
    if callback.data == 'Yes':  # если нажата кнопка Да, после вопроса о подтверждении личности, то
        bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id, reply_markup=0)  # удаляем кнопку
        bot.delete_message(chat_id=callback.message.chat.id,
                           message_id=callback.message.message_id)  # удаляем сообщение
        msg = bot.send_message(callback.message.chat.id, 'Вы успешно авторизовались ✅')  # отправляем сообщение
        user_id = callback.message.chat.id  # присваиваем id пользователя переменной
        cursor.execute(f"""UPDATE users SET tg_id = '{user_id}' where pin = '{str(entering_pin)}'""")  # вносим id в БД
        connection.commit()
        help_button(msg)

    elif callback.data == 'No':  # если нажата кнопка Нет, после вопроса о подтверждении личности, то
        bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id, reply_markup=0)  # удаляем кнопку
        bot.delete_message(chat_id=callback.message.chat.id,
                           message_id=callback.message.message_id)  # удаляем сообщение
        msg = bot.send_message(callback.message.chat.id, 'Введите пин повторно ⚠')  # отправляем сообщение
        bot.register_next_step_handler(msg, askPin)  # запускаем функцию askPin заново
        return

    elif callback.data == '0605':
        bot.send_message(callback.message.chat.id,
                         '1️⃣ Подойдите ко входу в новый корпус.\n'
                         '2️⃣ Поверните налево и пройдите через турникет\n'
                         '3️⃣ Пройдите к лифту\n'
                         '4️⃣ Поднимитесь на 6 этаж\n'
                         '5️⃣ Пройдите прямо и поверните налево\n'
                         '6️⃣ Кабинет 0605 будет в конце коридора справа от вас')
        bot.send_photo(callback.message.chat.id,
                       bot.send_photo(callback.message.chat.id, photo=open('photo_2022-05-29_00-20-49.jpg', 'rb')))
    elif callback.data == '0609':
        bot.send_message(callback.message.chat.id,
                         '1️⃣ Подойдите ко входу в новый корпус\n'
                         '2️⃣ Поверните налево и пройдите через турникет\n'
                         '3️⃣ Пройдите к лифту\n'
                         '4️⃣ Поднимитесь на 6 этаж\n'
                         '5️⃣ Пройдите прямо и поверните направо\n'
                         '6️⃣ Кабинет 0609 на фото')
        bot.send_photo(callback.message.chat.id,
                       bot.send_photo(callback.message.chat.id, photo=open('photo_2022-05-29_00-20-444.jpg', 'rb')))
    elif callback.data == '233':
        bot.send_message(callback.message.chat.id,
                         '1️⃣ Подойдите ко входу в старый корпус и пройдите через турникет\n'
                         '2️⃣ Идите правее к лестнице\n'
                         '3️⃣ После того как подниметесь по лестнице, поверните направо\n'
                         '4️⃣ Двигайтесь прямо до двери Единого деканата, в конце коридора\n'
                         )
        bot.send_photo(callback.message.chat.id,
                       bot.send_photo(callback.message.chat.id, photo=open('photo_2022-05-29_00-20-388.jpg', 'rb')))
    elif callback.data == '0732':
        bot.send_message(callback.message.chat.id,
                         '1️⃣ Подойдите ко входу в новый корпус\n'
                         '2️⃣ Поверните налево и пройдите через турникет\n'
                         '3️⃣ Пройдите к лифту\n'
                         '4️⃣ Поднимитесь на 7 этаж\n'
                         '5️⃣ Пройдите прямо и сразу поверните налево\n'
                         '6️⃣ Пройдите прямо и справа будет отдел по расчетам со студентами(0732)\n')
        bot.send_photo(callback.message.chat.id,
                       bot.send_photo(callback.message.chat.id, photo=open('photo_2022-05-29_00-20-499.jpg', 'rb')))
    else:
        res = requests.get(f'https://rinh-api.kovalev.team/employee/dto/{callback.data}')
        res = res.json()
        text = "👨‍🏫 ФИО: " + res['employee']['fullName']
        text += f"\n 📖 КАФЕДРА: {res['department']['name']}"
        text += f"\n 🏫 ИНСТИТУТ: {res['institute']['name']}"
        text += f"\n 📧 ПОЧТА: {res['employee']['email']}"
        text += f"\n 📱 ТЕЛЕФОН: {res['employee']['phone']}"
        text += f"\n 💻 ПРОФИЛЬ 'СТАНКИН': {res['employee']['authorUrlProfile']}"
        bot.send_photo(callback.message.chat.id, res['employee']["avatarUrl"])
        bot.send_message(callback.message.chat.id, text)
        bot.send_message()


@bot.message_handler(func=lambda message: message.text == '🔍 Help')
def Help(message):
   help_button(message)


@bot.message_handler(func=lambda message: message.text == '🗺 Расписание')
def askGr(message):
    chat_id = message.chat.id
    cursor.execute(f"""SELECT groupp from USERS where tg_id = '{chat_id}'""")
    gr = cursor.fetchone()
    result_gr = ''.join(gr)
    bot.send_message(message.chat.id,
                     f'https://edu.stankin.ru/pluginfile.php/426734/mod_folder/content/0/{result_gr}.pdf')


@bot.message_handler(func=lambda message: message.text == '👩🏻 Инструмент старосты')
def starosta(message):
    chat_id = message.chat.id
    cursor.execute(f"""SELECT role_id from users where tg_id='{chat_id}' and role_id='1'""")
    proverka_starosta = cursor.fetchone()
    if proverka_starosta:
        bot.send_message(message.chat.id,
                         "Этот инструмент для старост здесь вы можете:\n🛎 1.Сделать объявление.\nℹ 2.Добавить информацию для получения модулей.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item1 = types.KeyboardButton("🛎 Объявление")
        item2 = types.KeyboardButton("ℹ Заполнение информации о модулях")
        item3 = types.KeyboardButton("↩Нaзaд")
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)



@bot.message_handler(func=lambda message: message.text == '👶 Инструкции для первокурсника')
def pervak_main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("❓ Часто задаваемые вопросы")
    item2 = types.KeyboardButton("🏢 Адреса корпусов")
    item3 = types.KeyboardButton("📲 Полезные ссылки для первокурсника")
    item4 = types.KeyboardButton("👩‍💼 Контакты куратора")
    item5 = types.KeyboardButton("↩Нaзaд")
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "🤖 Выбери что тебя интересует!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '👩‍💼 Контакты куратора')
def kontakti_kuratora(message):
    xl = pd.ExcelFile("111.xlsx")
    df_pandas = xl.parse('Лист1')
    chat_id = message.chat.id
    cursor.execute(f"""SELECT groupp from USERS where tg_id = '{chat_id}'""")
    gr = ''.join(cursor.fetchone())
    for i in df_pandas.values.tolist():
        if i[0] == gr:
            if (i[4] != '-'):
                if (i[1] == 'Артемьева Мария Сергеевна'):
                    bot.send_photo(message.chat.id, photo=open('Артемьева Мария Сергеевна.jpg', 'rb'))
                elif (i[1] == 'Горбачева Лариса Петровна'):
                    bot.send_photo(message.chat.id, photo=open('Горбачева Лариса Петровна.jpg', 'rb'))
                elif (i[1] == 'Носовицкий Вадим Борисович'):
                    bot.send_photo(message.chat.id, photo=open('Носовицкий Вадим Борисович.jpg', 'rb'))
                elif (i[1] == 'Шибаева Анна Николаевна'):
                    bot.send_photo(message.chat.id, photo=open('Шибаева Анна Николаевна.jpg', 'rb'))
                bot.send_message(message.chat.id,
                                 f"👱‍♂️👱 Куратор {i[1]},{i[2]}.\n📞 Номер {i[3]},доп.номер {i[4]}.")
            else:
                if (i[1] == 'Артемьева Мария Сергеевна'):
                    bot.send_photo(message.chat.id, photo=open('Артемьева Мария Сергеевна.jpg', 'rb'))
                elif (i[1] == 'Горбачева Лариса Петровна'):
                    bot.send_photo(message.chat.id, photo=open('Горбачева Лариса Петровна.jpg', 'rb'))
                elif (i[1] == 'Носовицкий Вадим Борисович'):
                    bot.send_photo(message.chat.id, photo=open('Носовицкий Вадим Борисович.jpg', 'rb'))
                elif (i[1] == 'Шибаева Анна Николаевна'):
                    bot.send_photo(message.chat.id, photo=open('Шибаева Анна Николаевна.jpg', 'rb'))
                bot.send_message(message.chat.id,
                                 f"👱‍♂️👱 Куратор {i[1]},{i[2]}.\n📞 Номер {i[3]}.")
            break


@bot.message_handler(func=lambda message: message.text == '🏢 Адреса корпусов')
def adress_corpus(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("❤ Станкин (новый корпус)")
    item2 = types.KeyboardButton("❤‍🩹 Станкин (старый корпус)")
    item3 = types.KeyboardButton("🛠️ Фрезер")
    item4 = types.KeyboardButton("↩️Назад")
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id, "Выбери какой адрес тебе нужен", reply_markup=markup)
    bot.register_next_step_handler(message, infa_adress_corpus)


def infa_adress_corpus(message):
    if (message.text == '❤ Станкин (новый корпус)'):
        bot.send_photo(message.chat.id, get("http://photos.wikimapia.org/p/00/07/42/31/47_big.jpg").content)
        bot.send_location(message.from_user.id, 55.789732, 37.594987)  # Станкин
        bot.send_message(message.chat.id, "📍 Россия, Москва, Вадковский переулок, 3А, стр. 1 📍")

        bot.register_next_step_handler(message, infa_adress_corpus)

    elif (message.text == '❤‍🩹 Станкин (старый корпус)'):
        bot.send_photo(message.chat.id,
                       get("https://avatars.mds.yandex.net/get-altay/1551063/2a000001678a395261aeabd6a0f47adac3b6/XXL").content)
        bot.send_location(message.from_user.id, 55.789732, 37.594987)  # Станкин
        bot.send_message(message.chat.id, "📍 Россия, Москва, Вадковский переулок, 3А, стр. 1 📍")
        bot.register_next_step_handler(message, infa_adress_corpus)

    elif (message.text == '🛠️ Фрезер'):
        bot.send_photo(message.chat.id,
                       get("https://rblogger.ru/img3/2019/gorod-na-pamyat-482-iz-sela-karacharovo-v-selo-perovo/41.-Karacharovo.-shosse-Frezer.10.-Stankin.-21.06.19.01..jpg").content)
        bot.send_location(message.from_user.id, 55.736194, 37.733592)  # Фрезер(не знаю как сделать яндекс карту)
        bot.send_message(message.chat.id, "📍 Москва, Фрезер шоссе, дом 10, здание МГТУ Станкин. 📍")
        bot.register_next_step_handler(message, infa_adress_corpus)
    elif (message.text == '↩️Назад'):
        pervak_main(message)


@bot.message_handler(func=lambda message: message.text == '↩Нaзaд')
def back_pervak(message):
    help_button(message)

@bot.message_handler(func=lambda message: message.text == '📲 Полезные ссылки для первокурсника')
def ssilki_pervak(message):
    bot.send_sticker(chat_id=message.from_user.id,
                     sticker="CAACAgIAAxkBAAEEoR9icv56nRbYv0q6ebUZjyMRm_dXnQACSxYAAqllmEsCG4_D7LmPfSQE")
    bot.send_message(message.chat.id, "🌐 Сайт СТАНКИН: https://stankin.ru/\n"
                                      "📐 ЭОС: https://edu.stankin.ru/\n"
                                      "Группа в ВК МГТУ «СТАНКИН»: https://vk.com/msut_stankin\n"
                                      "Группа в ВК 'Подслушано МГТУ СТАНКИН': https://vk.com/podslstankin\n"
                                      "Группа в ВК 'В Станкине. Будь в курсе': https://vk.com/vstankine\n")


@bot.message_handler(func=lambda message: message.text == '❓ Часто задаваемые вопросы')
def chasto_zad_voprosi(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton("👨‍🎓1")
    item2 = types.KeyboardButton("⏰2")
    item3 = types.KeyboardButton("👨‍✈️3")
    item4 = types.KeyboardButton("💰4")
    item5 = types.KeyboardButton("💳5")
    item6 = types.KeyboardButton("💻6")
    item8 = types.KeyboardButton("↩️Назад")
    markup.add(item1, item2, item3, item4, item5, item6, item8)
    bot.send_sticker(chat_id=message.from_user.id,
                     sticker="CAACAgIAAxkBAAEE1zxikhVq6K9Gnem3It8mpBfTQjSlJQACKB0AAhAoiEgGCmFVG52zViQE")
    bot.send_message(message.chat.id, "👨‍🎓1.Я хочу получить справку о том что, человек является студентом вуза" +
                     "\n⏰2.Справка о периоде обучения или об обучении (с оценками об успеваемости)\n👨‍✈️3.Справка для военкомата\n💰4.Справка о размере и наличии стипендии\n💳5.При утере пропуска" +
                     "\n💻6.При проблемах с доступом к электронному модульному журналу",
                     reply_markup=markup)
    bot.register_next_step_handler(message, knopki_pervaki_voprosi)


def knopki_pervaki_voprosi(message):
    if (message.text == '👨‍🎓1'):
        markup = types.InlineKeyboardMarkup()
        btn_0609 = types.InlineKeyboardButton(text='Как пройти в 0609❓', callback_data='0609')
        markup.add(btn_0609)
        bot.send_message(message.chat.id, 'Отдел: Управление персоналом\n'
                                          'Кабинет: 0609 (новый корпус)\n'
                                          'Тел. для связи: +7(499)972-95-13', reply_markup=markup)
        bot.register_next_step_handler(message, knopki_pervaki_voprosi)
    elif (message.text == '⏰2'):
        markup = types.InlineKeyboardMarkup()
        btn_233 = types.InlineKeyboardButton(text='Как пройти в единый деканат❓', callback_data='233')
        markup.add(btn_233)
        bot.send_message(message.chat.id, 'Отдел: Единый деканат\n'
                                          'Кабинет: 233 (старый корпус)\n'
                                          'Тел. для связи: +7(499)973-38-34', reply_markup=markup)
        bot.register_next_step_handler(message, knopki_pervaki_voprosi)
    elif (message.text == '👨‍✈️3'):
        markup = types.InlineKeyboardMarkup()
        btn_0605 = types.InlineKeyboardButton(text='Как пройти в 0605❓', callback_data='0605')
        markup.add(btn_0605)
        bot.send_message(message.chat.id, 'Отдел: Второй отдел\n'
                                          'Кабинет: 0605 (новый корпус)\n'
                                          'Тел. для связи: +7(499)972-94-24', reply_markup=markup)
        bot.register_next_step_handler(message, knopki_pervaki_voprosi)
    elif (message.text == '💰4'):
        markup = types.InlineKeyboardMarkup()
        btn_0732 = types.InlineKeyboardButton(text='Как пройти в бухгалтерию❓', callback_data='0732')
        markup.add(btn_0732)
        bot.send_message(message.chat.id, 'Отдел: Бухгалтерия\n'
                                          'Кабинет: 0732 (новый корпус)\n'
                                          'Тел. для связи: +7(499)-972-94-55', reply_markup=markup)
        bot.register_next_step_handler(message, knopki_pervaki_voprosi)
    elif (message.text == '💳5'):
        markup = types.InlineKeyboardMarkup()
        btn_0732 = types.InlineKeyboardButton(text='Как пройти в единый деканат❓', callback_data='233')
        markup.add(btn_0732)
        bot.send_message(message.chat.id, 'Отдел: Единый деканат\n'
                                          'Кабинет: 233 (старый корпус)\n'
                                          'Тел. для связи: +7(499)973-38-34', reply_markup=markup)
        bot.register_next_step_handler(message, knopki_pervaki_voprosi)
    elif (message.text == '💻6'):
        markup = types.InlineKeyboardMarkup()
        btn_233 = types.InlineKeyboardButton(text='Как пройти в единый деканат❓', callback_data='233')
        markup.add(btn_233)
        bot.send_message(message.chat.id, 'Отдел: Единый деканат\n'
                                          'Кабинет: 233 (старый корпус)\n'
                                          'Тел. для связи: +7(499)973-38-34', reply_markup=markup)
        bot.register_next_step_handler(message, knopki_pervaki_voprosi)
    elif (message.text == '↩️Назад'):
        pervak_main(message)


@bot.message_handler(func=lambda message: message.text == '🛎 Объявление')
def Obyavlenie_starosta(message):
    if (message.text == '↩Нaзaд'):
        help_button(message)
    else:
        msg_1 = bot.send_message(message.chat.id,
                                 "📗Введите предмет с хештешгом и объявление, которое хотите сделать. \nПример:\n#Математика\nЗавтра тест!")
        global sub
        sub = message.text
        bot.register_next_step_handler(msg_1, advertisement)


def advertisement(message):
    if (message.text[0] == '#'):
        global group_chat_id
        chat_id = message.chat.id
        cursor.execute(f"""SELECT groupp from users where tg_id='{chat_id}'""")
        group_num = cursor.fetchone()[0]
        cursor.execute(f"""SELECT tg_id from users where groupp='{group_num}' and tg_id IS NOT NULL""")
        group_chat_id = cursor.fetchall()
        chat_id = message.chat.id
        msg_id = message.id
        for row in group_chat_id:
            row1 = str(row)
            row2 = row1[2:-3]
            bot.forward_message(
                chat_id=row2,  # chat_id чата в которое необходимо переслать сообщение
                from_chat_id=chat_id,  # chat_id из которого необходимо переслать сообщение
                message_id=msg_id
            )
    else:
        bot.send_sticker(chat_id=message.from_user.id,
                         sticker="CAACAgIAAxkBAAEEoSFicv6UqHg9efjKpeS5LkC4INvaJQAC9RoAArm3mUto-qCXoivVtiQE")
        bot.send_message(message.chat.id, "❌ Вы начали своё сообщение не с «#»\n"
                                          "Нажмите заново кнопку «🛎 Объявление»")


@bot.message_handler(func=lambda message: message.text == 'ℹ Заполнение информации о модулях')
def prepod_buttons(message):
    chat_id = message.chat.id
    cursor.execute(f"""SELECT role_id from users where tg_id='{chat_id}' and role_id='1'""")
    proverka_starosta = cursor.fetchone()
    if proverka_starosta:
        cursor.execute(f"""SELECT groupp from users where tg_id='{chat_id}'""")
        group_number = ', '.join(cursor.fetchone())
        cursor.execute(f"""SELECT doc_url from structura where group_code='{group_number}'""")
        url = cursor.fetchall()[0][0]
        bot.send_sticker(chat_id=message.from_user.id,
                         sticker="CAACAgIAAxkBAAEE1zhikhVl2osC7WOqJ2mZVfADNCo3xwACjR0AAlv1iUiN17KaMibyYyQE")
        bot.send_message(message.chat.id, "📃 Таблица с информацией о получении модулей. Пожалуйста заполните её, чтобы у группы была актуальная информация.\n" + url)
        bot.send_message(message.chat.id, "✅ Пример заполнения:\nhttps://docs.google.com/spreadsheets/d/1htUack7-iRy2yw0KArJKWKCQM75Rz3YfMEVfCULj8XE/edit#gid=0")

@bot.message_handler(func=lambda message: message.text == '📙 Модульный журнал')
def modul_journal(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='Модульный журнал', url='https://lk.stankin.ru/#!login')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "👇 Нажми на кнопку и перейди в модульный журнал. 👇 ", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📞 Контакты преподавателей')
def contacts(message):
    msg = bot.send_message(message.chat.id, "📝 Введите фамилию преподавателя:")
    bot.register_next_step_handler(msg, fio_request)


def fio_request(message):
    last_name = message.text
    response = requests.get(f'https://rinh-api.kovalev.team/employee/surname/{last_name}')
    response = response.json()
    if len(response) != 0:
        family_keyboard = types.InlineKeyboardMarkup()
        for i in range(len(response)):
            family_keyboard.add(
                types.InlineKeyboardButton(text=f"{response[i]['fullName']}", callback_data=response[i]['id']))
        bot.send_message(message.chat.id, '📂 Выберите что вам надо', reply_markup=family_keyboard)
    else:
        bot.send_sticker(chat_id=message.from_user.id,
                         sticker="CAACAgIAAxkBAAEEoSFicv6UqHg9efjKpeS5LkC4INvaJQAC9RoAArm3mUto-qCXoivVtiQE")
        bot.send_message(message.chat.id, '❌ Такого нет ❌')
        contacts(message)

@bot.message_handler(func=lambda message: message.text == '📖 Получение модуля')
def get_modul(message):
    chat_id = message.chat.id
    cursor.execute(f"""SELECT groupp from users where tg_id='{chat_id}'""")
    group_number = ', '.join(cursor.fetchone())
    cursor.execute(f"""SELECT doc_url from structura where group_code='{group_number}'""")
    url = cursor.fetchall()[0][0]
    bot.send_sticker(chat_id=message.from_user.id,
                     sticker="CAACAgIAAxkBAAEE1zhikhVl2osC7WOqJ2mZVfADNCo3xwACjR0AAlv1iUiN17KaMibyYyQE")
    bot.send_message(message.chat.id, "Ссылка на таблицу с требованиями получения модулей\n\n"+url)

@bot.message_handler(func=lambda message: message.text == '🖥 ЭОС')
def eos(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='ЭОС', url='https://edu.stankin.ru/login/index.php')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "👇 Нажми на кнопку и перейди в ЭОС. 👇", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Объявление для группы')
def Institute_choice(message):
    chat_id = message.chat.id
    cursor.execute(f"""SELECT role_id from users where tg_id='{chat_id}' and role_id='3'""")
    proverka_dekanat = cursor.fetchone()
    if proverka_dekanat:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('ИИТ')
        item2 = types.KeyboardButton('ИПТИ')
        item3 = types.KeyboardButton('ИСТМ')
        item4 = types.KeyboardButton('ИЦИС')
        item5 = types.KeyboardButton('Назад')
        markup.add(item1, item2, item3, item4,item5)
        msg = bot.send_message(message.chat.id, 'Выберите институт', reply_markup=markup)
        bot.register_next_step_handler(msg, choice)


def iit_napravlenie_choice(message):
    # if(message.text == 'ИИТ'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.row('Информатика и вычислительная техника')
    markup.row('Информационные системы и технологии')
    markup.row('Прикладная информатика')
    markup.row('Программная инженерия')
    markup.row('Назад')
    msg_2 = bot.send_message(message.chat.id, 'Выберите направление', reply_markup=markup)
    bot.register_next_step_handler(msg_2, IIT_group_choice)


def ipti_napravlenie_choice(message):
    # if(message.text == 'ИПТИ'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.row('Машиностроение')
    markup.row('Технологические машины и оборудование')
    markup.row('Конструкторско-технологическое обеспечение машиностроительных производств')
    markup.row('Проектирование технологических машин и комплексов')
    markup.row('Материаловедение и технология материалов')
    markup.row('Назад')
    msg_2 = bot.send_message(message.chat.id, 'Выберите направление', reply_markup=markup)
    bot.register_next_step_handler(msg_2, IPTI_group_choice)


def istm_napravlenie_choice(message):
    # if(message.text == 'ИСТМ'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.row('Техносферная безопасность')
    markup.row('Управление качеством')
    markup.row('Управление в технических системах')
    markup.row('Экономика')
    markup.row('Менеджмент')
    markup.row('Управление персоналом')
    markup.row('Назад')
    msg_2 = bot.send_message(message.chat.id, 'Выберите направление', reply_markup=markup)
    bot.register_next_step_handler(msg_2, ISTM_group_choice)


def icis_napravlenie_choice(message):
    # if(message.text == 'ИЦИС'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.row('Приборостроение')
    markup.row('Автоматизация технологических процессов и производств')
    markup.row('Мехатроника и робототехника')
    markup.row('Стандартизация и метрология')
    markup.row('Назад')
    msg_2 = bot.send_message(message.chat.id, 'Выберите направление', reply_markup=markup)
    bot.register_next_step_handler(msg_2, ICIS_group_choice)


def choice(message):
    if (message.text == 'ИИТ'):
        iit_napravlenie_choice(message)
    if (message.text == 'ИПТИ'):
        ipti_napravlenie_choice(message)
    if (message.text == 'ИСТМ'):
        istm_napravlenie_choice(message)
    if (message.text == 'ИЦИС'):
        icis_napravlenie_choice(message)
    if (message.text == 'Назад'):
        help_button(message)


def IIT_group_choice(message):
    if (message.text == 'Информатика и вычислительная техника'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('ИИС-18-01')
        markup.row('ИИС-18-02')
        markup.row('ИИС-18-03')
        markup.row('ИИС-18-04')
        markup.row('ИИС-19-01')
        markup.row('ИИС-19-02')
        markup.row('ИИС-19-03')
        markup.row('ИИС-19-04')
        markup.row('ИИС-20-01')
        markup.row('ИИС-20-02')
        markup.row('ИИС-20-03')
        markup.row('ИИС-20-04')
        markup.row('Назад')
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IIT_enter_announcement)

    elif (message.text == 'Информационные системы и технологии'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('ИИК-18-01')
        markup.row('ИИК-18-02')
        markup.row('ИИК-18-03')
        markup.row('ИИК-18-04')
        markup.row('ИИК-19-01')
        markup.row('ИИК-19-02')
        markup.row('ИИК-19-03')
        markup.row('ИИК-19-04')
        markup.row('ИИК-20-01')
        markup.row('ИИК-20-02')
        markup.row('ИИК-20-03')
        markup.row('ИИК-20-04')
        markup.row('ИИК-21-01')
        markup.row('ИИК-21-02')
        markup.row('ИИК-21-03')
        markup.row('ИИК-21-04')
        markup.row('Назад')
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IIT_enter_announcement)

    elif (message.text == 'Прикладная информатика'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('ИИМ-18-01')
        markup.row('ИИМ-18-02')
        markup.row('ИИМ-18-03')
        markup.row('ИИМ-18-04')
        markup.row('ИИМ-19-01')
        markup.row('ИИМ-19-02')
        markup.row('ИИМ-19-03')
        markup.row('ИИМ-19-04')
        markup.row('ИИМ-20-01')
        markup.row('ИИМ-20-02')
        markup.row('ИИМ-20-03')
        markup.row('ИИМ-20-04')
        markup.row('ИИМ-21-01')
        markup.row('ИИМ-21-02')
        markup.row('ИИМ-21-03')
        markup.row('ИИМ-21-04')
        markup.row('Назад')
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IIT_enter_announcement)
    elif (message.text == 'Программная инженерия'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('ИИЛ-18-01')
        markup.row('ИИЛ-18-02')
        markup.row('ИИЛ-18-03')
        markup.row('ИИЛ-18-04')
        markup.row('ИИЛ-19-01')
        markup.row('ИИЛ-19-02')
        markup.row('ИИЛ-19-03')
        markup.row('ИИЛ-19-04')
        markup.row('ИИЛ-20-01')
        markup.row('ИИЛ-20-02')
        markup.row('ИИЛ-20-03')
        markup.row('ИИЛ-20-04')
        markup.row('ИИЛ-21-01')
        markup.row('ИИЛ-21-02')
        markup.row('ИИЛ-21-03')
        markup.row('ИИЛ-21-04')
        markup.row('Назад')
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IIT_enter_announcement)
    elif (message.text == 'Назад'):
        Institute_choice(message)


def IPTI_group_choice(message):
    if (message.text == 'Машиностроение'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('МДБ-18-01')
        markup.row('МДБ-18-02')
        markup.row('МДБ-18-03')
        markup.row('МДБ-18-04')
        markup.row('МДБ-19-01')
        markup.row('МДБ-19-02')
        markup.row('МДБ-19-03')
        markup.row('МДБ-19-04')
        markup.row('МДБ-20-01')
        markup.row('МДБ-20-02')
        markup.row('МДБ-20-03')
        markup.row('МДБ-20-04')
        markup.row('МДБ-21-01')
        markup.row('МДБ-21-02')
        markup.row('МДБ-21-03')
        markup.row('МДБ-21-04')
        markup.row('Назад')
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IPTI_enter_announcement)
    elif (message.text == 'Технологические машины и оборудование'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('МДТ-18-01')
        markup.row('МДТ-18-02')
        item3 = types.KeyboardButton('МДТ-18-03')
        item4 = types.KeyboardButton('МДТ-18-04')
        item5 = types.KeyboardButton('МДТ-19-01')
        item6 = types.KeyboardButton('МДТ-19-02')
        item7 = types.KeyboardButton('МДТ-19-03')
        item8 = types.KeyboardButton('МДТ-19-04')
        item9 = types.KeyboardButton('МДТ-20-01')
        item10 = types.KeyboardButton('МДТ-20-02')
        item11 = types.KeyboardButton('МДТ-20-03')
        item12 = types.KeyboardButton('МДТ-20-04')
        item13 = types.KeyboardButton('МДТ-21-01')
        item14 = types.KeyboardButton('МДТ-21-02')
        item15 = types.KeyboardButton('МДТ-21-03')
        item16 = types.KeyboardButton('МДТ-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IPTI_enter_announcement)
    elif (message.text == 'Конструкторско-технологическое обеспечение машиностроительных производств'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('КТО-18-01')
        item2 = types.KeyboardButton('КТО-18-02')
        item3 = types.KeyboardButton('КТО-18-03')
        item4 = types.KeyboardButton('КТО-18-04')
        item5 = types.KeyboardButton('КТО-19-01')
        item6 = types.KeyboardButton('КТО-19-02')
        item7 = types.KeyboardButton('КТО-19-03')
        item8 = types.KeyboardButton('КТО-19-04')
        item9 = types.KeyboardButton('КТО-20-01')
        item10 = types.KeyboardButton('КТО-20-02')
        item11 = types.KeyboardButton('КТО-20-03')
        item12 = types.KeyboardButton('КТО-20-04')
        item13 = types.KeyboardButton('КТО-21-01')
        item14 = types.KeyboardButton('КТО-21-02')
        item15 = types.KeyboardButton('КТО-21-03')
        item16 = types.KeyboardButton('КТО-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IPTI_enter_announcement)
    elif (message.text == 'Проектирование технологических машин и комплексов'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('ПТМ-18-01')
        item2 = types.KeyboardButton('ПТМ-18-02')
        item3 = types.KeyboardButton('ПТМ-18-03')
        item4 = types.KeyboardButton('ПТМ-18-04')
        item5 = types.KeyboardButton('ПТМ-19-01')
        item6 = types.KeyboardButton('ПТМ-19-02')
        item7 = types.KeyboardButton('ПТМ-19-03')
        item8 = types.KeyboardButton('ПТМ-19-04')
        item9 = types.KeyboardButton('ПТМ-20-01')
        item10 = types.KeyboardButton('ПТМ-20-02')
        item11 = types.KeyboardButton('ПТМ-20-03')
        item12 = types.KeyboardButton('ПТМ-20-04')
        item13 = types.KeyboardButton('ПТМ-21-01')
        item14 = types.KeyboardButton('ПТМ-21-02')
        item15 = types.KeyboardButton('ПТМ-21-03')
        item16 = types.KeyboardButton('ПТМ-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IPTI_enter_announcement)
    elif (message.text == 'Материаловедение и технология материалов'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('МТМ-18-01')
        item2 = types.KeyboardButton('МТМ-18-02')
        item3 = types.KeyboardButton('МТМ-18-03')
        item4 = types.KeyboardButton('МТМ-18-04')
        item5 = types.KeyboardButton('МТМ-19-01')
        item6 = types.KeyboardButton('МТМ-19-02')
        item7 = types.KeyboardButton('МТМ-19-03')
        item8 = types.KeyboardButton('МТМ-19-04')
        item9 = types.KeyboardButton('МТМ-20-01')
        item10 = types.KeyboardButton('МТМ-20-02')
        item11 = types.KeyboardButton('МТМ-20-03')
        item12 = types.KeyboardButton('МТМ-20-04')
        item13 = types.KeyboardButton('МТМ-21-01')
        item14 = types.KeyboardButton('МТМ-21-02')
        item15 = types.KeyboardButton('МТМ-21-03')
        item16 = types.KeyboardButton('МТМ-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, IPTI_enter_announcement)
    elif (message.text == 'Назад'):
        Institute_choice(message)


def ISTM_group_choice(message):
    if (message.text == 'Техносферная безопасность'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('ТБ-18-01')
        item2 = types.KeyboardButton('ТБ-18-02')
        item3 = types.KeyboardButton('ТБ-18-03')
        item4 = types.KeyboardButton('ТБ-18-04')
        item5 = types.KeyboardButton('ТБ-19-01')
        item6 = types.KeyboardButton('ТБ-19-02')
        item7 = types.KeyboardButton('ТБ-19-03')
        item8 = types.KeyboardButton('ТБ-19-04')
        item9 = types.KeyboardButton('ТБ-20-01')
        item10 = types.KeyboardButton('ТБ-20-02')
        item11 = types.KeyboardButton('ТБ-20-03')
        item12 = types.KeyboardButton('ТБ-20-04')
        item13 = types.KeyboardButton('ТБ-21-01')
        item14 = types.KeyboardButton('ТБ-21-02')
        item15 = types.KeyboardButton('ТБ-21-03')
        item16 = types.KeyboardButton('ТБ-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, ISTM_enter_announcement)
    elif (message.text == 'Управление качеством'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('УК-18-01')
        item2 = types.KeyboardButton('УК-18-02')
        item3 = types.KeyboardButton('УК-18-03')
        item4 = types.KeyboardButton('УК-18-04')
        item5 = types.KeyboardButton('УК-19-01')
        item6 = types.KeyboardButton('УК-19-02')
        item7 = types.KeyboardButton('УК-19-03')
        item8 = types.KeyboardButton('УК-19-04')
        item9 = types.KeyboardButton('УК-20-01')
        item10 = types.KeyboardButton('УК-20-02')
        item11 = types.KeyboardButton('УК-20-03')
        item12 = types.KeyboardButton('УК-20-04')
        item13 = types.KeyboardButton('УК-21-01')
        item14 = types.KeyboardButton('УК-21-02')
        item15 = types.KeyboardButton('УК-21-03')
        item16 = types.KeyboardButton('УК-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, ISTM_enter_announcement)

    elif (message.text == 'Управление в технических системах'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('УТС-18-01')
        item2 = types.KeyboardButton('УТС-18-02')
        item3 = types.KeyboardButton('УТС-18-03')
        item4 = types.KeyboardButton('УТС-18-04')
        item5 = types.KeyboardButton('УТС-19-01')
        item6 = types.KeyboardButton('УТС-19-02')
        item7 = types.KeyboardButton('УТС-19-03')
        item8 = types.KeyboardButton('УТС-19-04')
        item9 = types.KeyboardButton('УТС-20-01')
        item10 = types.KeyboardButton('УТС-20-02')
        item11 = types.KeyboardButton('УТС-20-03')
        item12 = types.KeyboardButton('УТС-20-04')
        item13 = types.KeyboardButton('УТС-21-01')
        item14 = types.KeyboardButton('УТС-21-02')
        item15 = types.KeyboardButton('УТС-21-03')
        item16 = types.KeyboardButton('УТС-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, ISTM_enter_announcement)

    elif (message.text == 'Экономика'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('ЭК-18-01')
        item2 = types.KeyboardButton('ЭК-18-02')
        item3 = types.KeyboardButton('ЭК-18-03')
        item4 = types.KeyboardButton('ЭК-18-04')
        item5 = types.KeyboardButton('ЭК-19-01')
        item6 = types.KeyboardButton('ЭК-19-02')
        item7 = types.KeyboardButton('ЭК-19-03')
        item8 = types.KeyboardButton('ЭК-19-04')
        item9 = types.KeyboardButton('ЭК-20-01')
        item10 = types.KeyboardButton('ЭК-20-02')
        item11 = types.KeyboardButton('ЭК-20-03')
        item12 = types.KeyboardButton('ЭК-20-04')
        item13 = types.KeyboardButton('ЭК-21-01')
        item14 = types.KeyboardButton('ЭК-21-02')
        item15 = types.KeyboardButton('ЭК-21-03')
        item16 = types.KeyboardButton('ЭК-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, ISTM_enter_announcement)
    elif (message.text == 'Менеджмент'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('ММ-18-01')
        item2 = types.KeyboardButton('ММ-18-02')
        item3 = types.KeyboardButton('ММ-18-03')
        item4 = types.KeyboardButton('ММ-18-04')
        item5 = types.KeyboardButton('ММ-19-01')
        item6 = types.KeyboardButton('ММ-19-02')
        item7 = types.KeyboardButton('ММ-19-03')
        item8 = types.KeyboardButton('ММ-19-04')
        item9 = types.KeyboardButton('ММ-20-01')
        item10 = types.KeyboardButton('ММ-20-02')
        item11 = types.KeyboardButton('ММ-20-03')
        item12 = types.KeyboardButton('ММ-20-04')
        item13 = types.KeyboardButton('ММ-21-01')
        item14 = types.KeyboardButton('ММ-21-02')
        item15 = types.KeyboardButton('ММ-21-03')
        item16 = types.KeyboardButton('ММ-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, ISTM_enter_announcement)

    elif (message.text == 'Управление персоналом'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('УП-18-01')
        item2 = types.KeyboardButton('УП-18-02')
        item3 = types.KeyboardButton('УП-18-03')
        item4 = types.KeyboardButton('УП-18-04')
        item5 = types.KeyboardButton('УП-19-01')
        item6 = types.KeyboardButton('УП-19-02')
        item7 = types.KeyboardButton('УП-19-03')
        item8 = types.KeyboardButton('УП-19-04')
        item9 = types.KeyboardButton('УП-20-01')
        item10 = types.KeyboardButton('УП-20-02')
        item11 = types.KeyboardButton('УП-20-03')
        item12 = types.KeyboardButton('УП-20-04')
        item13 = types.KeyboardButton('УП-21-01')
        item14 = types.KeyboardButton('УП-21-02')
        item15 = types.KeyboardButton('УП-21-03')
        item16 = types.KeyboardButton('УП-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, ISTM_enter_announcement)
    elif (message.text == 'Назад'):
        Institute_choice(message)


def ICIS_group_choice(message):
    if (message.text == 'Приборостроение'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('ПС-18-01')
        item2 = types.KeyboardButton('ПС-18-02')
        item3 = types.KeyboardButton('ПС-18-03')
        item4 = types.KeyboardButton('ПС-18-04')
        item5 = types.KeyboardButton('ПС-19-01')
        item6 = types.KeyboardButton('ПС-19-02')
        item7 = types.KeyboardButton('ПС-19-03')
        item8 = types.KeyboardButton('ПС-19-04')
        item9 = types.KeyboardButton('ПС-20-01')
        item10 = types.KeyboardButton('ПС-20-02')
        item11 = types.KeyboardButton('ПС-20-03')
        item12 = types.KeyboardButton('ПС-20-04')
        item13 = types.KeyboardButton('ПС-21-01')
        item14 = types.KeyboardButton('ПС-21-02')
        item15 = types.KeyboardButton('ПС-21-03')
        item16 = types.KeyboardButton('ПС-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, icis_enter_announcement)
    elif (message.text == 'Автоматизация технологических процессов и производств'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('АДБ-18-01')
        item2 = types.KeyboardButton('АДБ-18-02')
        item3 = types.KeyboardButton('АДБ-18-03')
        item4 = types.KeyboardButton('АДБ-18-04')
        item5 = types.KeyboardButton('АДБ-19-01')
        item6 = types.KeyboardButton('АДБ-19-02')
        item7 = types.KeyboardButton('АДБ-19-03')
        item8 = types.KeyboardButton('АДБ-19-04')
        item9 = types.KeyboardButton('АДБ-19-05')
        item10 = types.KeyboardButton('АДБ-19-06')
        item11 = types.KeyboardButton('АДБ-20-01')
        item12 = types.KeyboardButton('АДБ-20-02')
        item13 = types.KeyboardButton('АДБ-20-03')
        item14 = types.KeyboardButton('АДБ-20-04')
        item15 = types.KeyboardButton('АДБ-21-01')
        item16 = types.KeyboardButton('АДБ-21-02')
        item17 = types.KeyboardButton('АДБ-21-03')
        item18 = types.KeyboardButton('АДБ-21-04')
        item19 = types.KeyboardButton('Назад')
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13,
                   item14, item15,
                   item16, item17, item18, item19)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, icis_enter_announcement)
    elif (message.text == 'Мехатроника и робототехника'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('МР-18-01')
        item2 = types.KeyboardButton('МР-18-02')
        item3 = types.KeyboardButton('МР-18-03')
        item4 = types.KeyboardButton('МР-18-04')
        item5 = types.KeyboardButton('МР-19-01')
        item6 = types.KeyboardButton('МР-19-02')
        item7 = types.KeyboardButton('МР-19-03')
        item8 = types.KeyboardButton('МР-19-04')
        item9 = types.KeyboardButton('МР-20-01')
        item10 = types.KeyboardButton('МР-20-02')
        item11 = types.KeyboardButton('МР-20-03')
        item12 = types.KeyboardButton('МР-20-04')
        item13 = types.KeyboardButton('МР-21-01')
        item14 = types.KeyboardButton('МР-21-02')
        item15 = types.KeyboardButton('МР-21-03')
        item16 = types.KeyboardButton('МР-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, icis_enter_announcement)
    elif (message.text == 'Стандартизация и метрология'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        item1 = types.KeyboardButton('СМ-18-01')
        item2 = types.KeyboardButton('СМ-18-02')
        item3 = types.KeyboardButton('СМ-18-03')
        item4 = types.KeyboardButton('СМ-18-04')
        item5 = types.KeyboardButton('СМ-19-01')
        item6 = types.KeyboardButton('СМ-19-02')
        item7 = types.KeyboardButton('СМ-19-03')
        item8 = types.KeyboardButton('СМ-19-04')
        item9 = types.KeyboardButton('СМ-20-01')
        item10 = types.KeyboardButton('СМ-20-02')
        item11 = types.KeyboardButton('СМ-20-03')
        item12 = types.KeyboardButton('СМ-20-04')
        item13 = types.KeyboardButton('СМ-21-01')
        item14 = types.KeyboardButton('СМ-21-02')
        item15 = types.KeyboardButton('СМ-21-03')
        item16 = types.KeyboardButton('СМ-21-04')
        item17 = types.KeyboardButton('Назад')
        markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                   item16, item17)
        msg_3 = bot.send_message(message.chat.id, 'Выберите группу', reply_markup=markup)
        bot.register_next_step_handler(msg_3, icis_enter_announcement)
    elif (message.text == 'Назад'):
        Institute_choice(message)


def IIT_enter_announcement(message):
    if (message.text == 'Назад'):
        iit_napravlenie_choice(message)
    else:
        global forward_chat_id
        choice_group = message.text
        cursor.execute(f"""SELECT tg_id from users where groupp = '{str(choice_group)}' and tg_id IS NOT NULL""")
        forward_chat_id = cursor.fetchall()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('Назад')
        msg = bot.send_message(message.chat.id, '📋 Напишите объявление', reply_markup=markup)
        bot.register_next_step_handler(msg, iit_forward_announcement)


def IPTI_enter_announcement(message):
    if (message.text == 'Назад'):
        ipti_napravlenie_choice(message)
    else:
        global forward_chat_id
        choice_group = message.text
        cursor.execute(f"""SELECT tg_id from users where groupp = '{str(choice_group)}' and tg_id IS NOT NULL""")
        forward_chat_id = cursor.fetchall()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('Назад')
        msg = bot.send_message(message.chat.id, '📋 Напишите объявление', reply_markup=markup)
        bot.register_next_step_handler(msg, ipti_forward_announcement)


def ISTM_enter_announcement(message):
    if (message.text == 'Назад'):
        istm_napravlenie_choice(message)
    else:
        global forward_chat_id
        choice_group = message.text
        cursor.execute(f"""SELECT tg_id from users where groupp = '{str(choice_group)}' and tg_id IS NOT NULL""")
        forward_chat_id = cursor.fetchall()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('Назад')
        msg = bot.send_message(message.chat.id, '📋 Напишите объявление', reply_markup=markup)
        bot.register_next_step_handler(msg, istm_forward_announcement)


def icis_enter_announcement(message):
    if (message.text == 'Назад'):
        icis_napravlenie_choice(message)
    else:
        global forward_chat_id
        choice_group = message.text
        cursor.execute(f"""SELECT tg_id from users where groupp = '{str(choice_group)}' and tg_id IS NOT NULL""")
        forward_chat_id = cursor.fetchall()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
        markup.row('Назад')
        msg = bot.send_message(message.chat.id, '📋 Напишите объявление', reply_markup=markup)
        bot.register_next_step_handler(msg, icis_forward_announcement)


def iit_forward_announcement(message):
    if message.text == 'Назад':
        iit_napravlenie_choice(message)
    else:
        help_button(message)
        chat_id = message.chat.id
        msg_id = message.id
        for row in forward_chat_id:
            row1 = str(row)
            row2 = row1[2:-3]
            bot.forward_message(
                chat_id=row2,  # chat_id чата в которое необходимо переслать сообщение
                from_chat_id=chat_id,  # chat_id из которого необходимо переслать сообщение
                message_id=msg_id  # message_id которое необходимо переслать
            )


def ipti_forward_announcement(message):
    if message.text == 'Назад':
        ipti_napravlenie_choice(message)
    else:
        help_button(message)
        chat_id = message.chat.id
        msg_id = message.id
        for row in forward_chat_id:
            row1 = str(row)
            row2 = row1[2:-3]
            bot.forward_message(
                chat_id=row2,  # chat_id чата в которое необходимо переслать сообщение
                from_chat_id=chat_id,  # chat_id из которого необходимо переслать сообщение
                message_id=msg_id  # message_id которое необходимо переслать
            )


def istm_forward_announcement(message):
    if message.text == 'Назад':
        istm_napravlenie_choice(message)
    else:
        help_button(message)
        chat_id = message.chat.id
        msg_id = message.id
        for row in forward_chat_id:
            row1 = str(row)
            row2 = row1[2:-3]
            bot.forward_message(
                chat_id=row2,  # chat_id чата в которое необходимо переслать сообщение
                from_chat_id=chat_id,  # chat_id из которого необходимо переслать сообщение
                message_id=msg_id  # message_id которое необходимо переслать
            )


def icis_forward_announcement(message):
    if message.text == 'Назад':
        icis_napravlenie_choice(message)
    else:
        help_button(message)
        chat_id = message.chat.id
        msg_id = message.id
        for row in forward_chat_id:
            row1 = str(row)
            row2 = row1[2:-3]
            bot.forward_message(
                chat_id=row2,  # chat_id чата в которое необходимо переслать сообщение
                from_chat_id=chat_id,  # chat_id из которого необходимо переслать сообщение
                message_id=msg_id  # message_id которое необходимо переслать
            )


@server.route('/' + TOKEN_DEV, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

