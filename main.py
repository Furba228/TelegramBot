import random
import telebot
import sqlite3
import requests
import datetime
from telebot import types
from string import ascii_uppercase, ascii_lowercase, digits
from config import weather_token, telebot_token

answers = ['Бесспорно', 'Предрешено', 'Никаких сомнений', 'Определённо да', 'Можешь быть уверен(а) в этом',
           'Мне кажется - да', 'Вероятнее всего', 'Хорошие перспективы', 'Знаки говорят - да', 'Да',
           'Пока неясно, попробуй снова', 'Спроси позже', 'Лучше не рассказывать', 'Сейчас нельзя предсказать',
           'Сконцентрируйся и спроси опять',
           'Даже не думай', 'Мой ответ - нет', 'По моим данным - нет', 'Перспективы не очень хорошие',
           'Весьма сомнительно']

bot = telebot.TeleBot(telebot_token)


@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет,  <b>{message.from_user.first_name} {message.from_user.last_name}</b> ' \
           f'\nНажми /menu, чтобы увидеть Меню'
    sticker = open('static/sticker(hello).webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(commands=['youtube'])
def get_youtube(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти на Youtube', url='https://www.youtube.com/'))
    bot.send_message(message.chat.id, 'Перейти на Youtube', reply_markup=markup)


@bot.message_handler(commands=['predictions'])
def get_prediction(message):
    bot.send_message(message.chat.id, f'<b>Привет {message.from_user.first_name} {message.from_user.last_name}</b>',
                     parse_mode='html')
    bot.send_message(message.chat.id, '<b>Я магический шар, и я знаю ответ на любой твой вопрос.</b>',
                     parse_mode='html')


@bot.message_handler(commands=['passwordgenerator'])
def password_gen(message):
    bot.send_message(message.chat.id, '<b>Какой пароль сгенерировать?</b>',
                     parse_mode='html')
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('EASY', callback_data='easy')
    item1 = types.InlineKeyboardButton('COMPLEX', callback_data='complex')
    item2 = types.InlineKeyboardButton('NO', callback_data='No Thanks')
    markup.add(item, item1, item2)
    bot.send_message(message.chat.id, '<b>Выберите вариант</b>', reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_password(call):
    password = ''
    chars = ''
    try:
        if call.data == 'easy':
            length = 6
            bot.send_message(call.message.chat.id, '<b>Ваш Пароль</b>', parse_mode='html')
            chars += ascii_lowercase
            chars += digits
            chars += ascii_uppercase
            for i in range(length):
                password += random.choice(chars)
            bot.send_message(call.message.chat.id, password)
        elif call.data == 'complex':
            length = 10
            bot.send_message(call.message.chat.id, '<b>Ваш Пароль</b>', parse_mode='html')
            chars += ascii_lowercase
            chars += digits
            chars += ascii_uppercase
            for i in range(length):
                password += random.choice(chars)
            bot.send_message(call.message.chat.id, password)
        elif call.data == 'No Thanks':
            bot.send_message(call.message.chat.id, '<b>До встречи</b>', parse_mode='html')

    except Exception as e:
        print(repr(e))


@bot.message_handler(commands=['menu'])
def get_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    youtube = types.KeyboardButton('Youtube')
    start = types.KeyboardButton('Start')
    predictions = types.KeyboardButton('Predictions')
    password = types.KeyboardButton('PasswordGenerator')
    registration = types.KeyboardButton('Registration')
    weather = types.KeyboardButton('Weather')
    markup.add(youtube, start, predictions, password, registration, weather)
    bot.send_message(message.chat.id, '<b>MENU</b>', reply_markup=markup, parse_mode='html')


@bot.message_handler(commands=['registration'])
def registration(message):
    connect = sqlite3.connect('user.db')
    cursor = connect.cursor()

    cursor.execute('CREATE TABLE if not exists users('
                   'id int unsigned,'
                   'first_name varchar(50),'
                   'last_name varchar(50),'
                   'user_name varchar(50))')

    connect.commit()

    people_id = message.chat.id
    cursor.execute(f'select id from users where id = {people_id}')
    data = cursor.fetchone()
    if data is None:
        user_list = [message.chat.id, message.from_user.first_name, message.from_user.last_name,
                     message.from_user.username]
        cursor.execute("insert into users values(?,?,?,?);", user_list)
        bot.send_message(message.chat.id, '<b>Вы успешно зарегестрировались</b>', parse_mode='html')
        connect.commit()
    else:
        bot.send_message(message.chat.id, '<b>Вы уже зарегестрированы</b>', parse_mode='html')


@bot.message_handler(commands=['weather'])
def get_weather(message):
    bot.send_message(message.chat.id, '<b>Введите * потом название города(англ)</b>', parse_mode='html')


@bot.message_handler()
def get_user_text(message):
    if str.upper(message.text) == 'ПРИВЕТ' or str.upper(message.text) == 'HELLO':
        bot.send_message(message.chat.id,
                         f'И тебе привет, {message.from_user.first_name} {message.from_user.last_name}',
                         parse_mode='html')
    elif message.text[0] == '*':
        return get_city(message)
    elif message.text == 'Weather':
        return get_weather(message)
    elif message.text == 'Youtube':
        return get_youtube(message)
    elif message.text == 'Start':
        return start(message)
    elif message.text == 'Predictions':
        return get_prediction(message)
    elif message.text == 'PasswordGenerator':
        return password_gen(message)
    elif message.text == 'Registration':
        return registration(message)
    elif str.upper(message.text) == 'ID':
        bot.send_message(message.chat.id, f'Твой id {message.from_user.id}', parse_mode='html')
    elif str.upper(message.text) == 'PHOTO' or str.upper(message.text) == 'ФОТО':
        photo = open('static/photo.jpg', 'rb')
        bot.send_photo(message.chat.id, photo)
    elif '?' in message.text:
        bot.send_message(message.chat.id, f'<b>{random.choice(answers)}</b>', parse_mode='html')
    elif message.text == 'info':
        bot.send_message(message.chat.id, message, parse_mode='html')
    else:
        bot.send_message(message.chat.id, '<b>Я тебя не понимаю</b>', parse_mode='html')


@bot.message_handler()
def get_city(message):
    try:
        if message.text[0] == '*':
            r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q='
                             f'{message.text[1::]}&appid={weather_token}&units=metric')
            data = r.json()

            city = data['name']
            temp = data['main']['temp']
            pressure = data['main']['pressure']
            sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
            sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
            humidity = data['main']['humidity']
            mess = (f'Погода в {city}:\n Температура = {temp} C\n Давление = {pressure}\n Влажность = {humidity}%'
                    f'\n Рассвет будет в {sunrise}\n Закат будет в {sunset}')
            bot.send_message(message.chat.id, mess, parse_mode='html')

    except Exception as ex:
        print(repr(ex))
        bot.send_message(message.chat.id, '<b>Неправильное название города</b>', parse_mode='html')


bot.polling(none_stop=True)
