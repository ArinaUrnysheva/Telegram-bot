import telebot
import requests
import json
from telebot import types

bot = telebot.TeleBot('7801328708:AAE1NG1GzI_s3KulnUesAnhSj-h4Zel_1RQ')
API = '50113b4ed6b2191f58449850655c7267'

# команда \start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Введите название города, в котором Вы бы хотели узнать погоду.')

# картинка кота (команда \maxwell)
@bot.message_handler(commands=['maxwell'])
def maxwell(message):
    file = open('D:/telegrambot/tgbot/photo.jpeg', 'rb')
    bot.send_photo(message.chat.id, file)

# обработка запроса, создание кнопок с датами
@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
    if res.status_code != 200:  # Если статус код не 200, это означает, что город не найден
        bot.send_message(message.chat.id, 'Ошибка: Введите название существующего города.')
        return
    data = json.loads(res.text)
    cur_date = data["list"][0]["dt_txt"].split(' ')[0].split('-')[2]
    cur_month = data["list"][0]["dt_txt"].split(' ')[0].split('-')[1]
    cur_year = data["list"][0]["dt_txt"].split(' ')[0].split('-')[0]
    btns = []
    markup = types.InlineKeyboardMarkup()
    if int(cur_month) == 2 and (int(cur_year) % 4 != 0 or int(cur_year) % 100 == 0 and int(cur_year) % 400 != 0): # невисокосный год
        a = int(cur_date)
        for i in range(5):
            if a > 28:
                btns.append(types.InlineKeyboardButton(f'{(a % 28):02}.{(int(cur_month) + 1):02}', callback_data=f'day{i},{city}'))
            else:
                btns.append(types.InlineKeyboardButton(f'{(a):02}.{(int(cur_month)):02}', callback_data=f'day{i},{city}'))
            a += 1

    elif int(cur_month) == 2 and (int(cur_year) % 4 == 0 and int(cur_year) % 100 != 0 or int(cur_year) & 400): # високосный год
        a = int(cur_date)
        for i in range(5):
            if a > 29:
                btns.append(types.InlineKeyboardButton(f'{(a % 29):02}.{(int(cur_month) + 1):02}', callback_data=f'day{i},{city}'))
            else:
                btns.append(types.InlineKeyboardButton(f'{(a):02}.{(int(cur_month)):02}', callback_data=f'day{i},{city}'))
            a += 1

    elif int(cur_month) in [1, 3, 5, 7, 8, 10]: # в месяце 31 день (кроме декабря)
        a = int(cur_date)
        for i in range(5):
            if a > 31:
                btns.append(types.InlineKeyboardButton(f'{(a % 31):02}.{(int(cur_month) + 1):02}', callback_data=f'day{i},{city}'))
            else:
                btns.append(types.InlineKeyboardButton(f'{(a):02}.{(int(cur_month)):02}', callback_data=f'day{i},{city}'))
            a += 1

    elif int(cur_month) == 12: # декабрь
        a = int(cur_date)
        for i in range(5):
            if a > 31:
                btns.append(types.InlineKeyboardButton(f'{(a % 31):02}.{(int(cur_month) + 1):02}', callback_data=f'day{i},{city}'))
            else:
                btns.append(types.InlineKeyboardButton(f'{(a):02}.{(int(cur_month)):02}', callback_data=f'day{i},{city}'))
            a += 1

    elif int(cur_month) in [4, 6, 9, 11]: # в месяце 30 дней
        a = int(cur_date)
        for i in range(5):
            if a > 30:
                btns.append(types.InlineKeyboardButton(f'{a - 30}.{int(cur_month) + 1}', callback_data=f'day{i},{city}'))
            else:
                btns.append(types.InlineKeyboardButton(f'{a}.{int(cur_month)}', callback_data=f'day{i},{city}'))
            a += 1
    markup.row(btns[0])
    for i in range(2, len(btns), 2):
        markup.row(btns[i - 1], btns[i])
    bot.send_message(message.chat.id, "На какую дату Вы бы хотели узнать прогноз?", reply_markup=markup)

# описание функций кнопок даты - создание кнопок с временем
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    #day = callback.data.split(',')[0]
    city = callback.data.split(',')[-1]
    res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
    data = json.loads(res.text)
    cur_time = data["list"][0]["dt_txt"].split(' ')[1].split(':')[0]
    cur_date = data["list"][0]["dt_txt"].split(' ')[0].split('-')[2]
    cur_month = data["list"][0]["dt_txt"].split(' ')[0].split('-')[1]
    cur_year = data["list"][0]["dt_txt"].split(' ')[0].split('-')[0]

    btns_time = []
    markup = types.InlineKeyboardMarkup()
    if callback.data.split(',')[0] == 'day0':
        for j in range(0, 22 - int(cur_time), 3):
            btns_time.append(
                types.InlineKeyboardButton(f'{(int(cur_time) + j):02}:00', callback_data=f'time{int(cur_time) + j},day0,{city}'))
        for k in range(0, len(btns_time), 2):
            if k + 1 < len(btns_time):
                markup.row(btns_time[k], btns_time[k + 1 ])
            else:
                markup.row(btns_time[k])
        bot.send_message(callback.message.chat.id, 'На какое время Вы бы хотели узнать прогноз?', reply_markup=markup)
        
    elif callback.data.split(',')[0] in ['day1', 'day2', 'day3', 'day4', 'day5']:
        for x in range(1, 5):
            if callback.data.split(',')[0] == f'day{x}':
                for j in range(0, 22, 3):
                    btns_time.append(
                        types.InlineKeyboardButton(f'{(j):02}:00', callback_data=f'time{j},day{x},{city}'))
                for k in range(0, len(btns_time), 2):
                    if k + 1 < len(btns_time):
                        markup.row(btns_time[k], btns_time[k + 1 ])
                    else:
                        markup.row(btns_time[k])
                bot.send_message(callback.message.chat.id, 'На какое время Вы бы хотели узнать прогноз?', reply_markup=markup)
                
    elif callback.data.split(',')[0] in ['time0', 'time3', 'time6', 'time9', 'time12', 'time15', 'time18', 'time21']:
        for i in range(5):
            if callback.data.split(',')[1] == f'day{i}':
                new_date = int(cur_date) + i

        for j in range(0, 22, 3):
            if callback.data.split(',')[0] == f'time{j}':
                time = j

        new_month = int(cur_month)
        new_year = int(cur_year)
        if int(cur_month) == 2 and int(cur_year) % 4 != 0 or int(cur_year) % 4 == 0 and int(cur_year) % 100 == 0 and int(cur_year) % 400 != 0:
            if new_date > 28:
                new_date -= 28
                new_month += 1

        elif int(cur_month) == 2 and int(cur_month) % 4 == 0 and (int(cur_month) % 100 != 0 or int(cur_month) % 400 == 0):
            if new_date > 29:
                new_date -= 29
                new_month += 1

        elif int(cur_month) in [1, 3, 5, 7, 8, 10]:
            if new_date > 31:
                new_date -= 31
                new_month += 1

        elif int(cur_month) in [4, 6, 9, 11]:
            if new_date > 30:
                new_date -= 30
                new_month += 1

        elif int(cur_month) == 12:
            if new_date > 31:
                new_date -= 31
                new_month = 1
                new_year += 1

        formatted_date = f'{new_year}-{(new_month):02}-{(new_date):02} {(time):02}:00:00'
        for j in range(len(data["list"])):
             if data["list"][j]["dt_txt"] == formatted_date:
                 weather_description = ['clear', 'clouds', 'rain', 'drizzle', 'thunderstorm', 'snow', 'mist', 'fog',
                                        'dust', 'sand', 'ash', 'squall', 'tornado']
                 emoji = ['☀', '☁', '☔️💦', '🌧💧', '🌩', '🌨☃️', '🌫', '🌫', ' ', ' ', '🌋', '💨', '🌪']

                 for i in range(len(weather_description)):
                     if data["list"][j]["weather"][0]["main"].lower() == weather_description[i]:
                         bot.send_message(callback.message.chat.id,
                                          f'Температура воздуха {int(round(data["list"][j]["main"]["temp"], 0))}°C\nОщущается как {round(data["list"][j]["main"]["feels_like"], 0)}°C'
                                          f'\nАтмосферное давление {round(int(data["list"][j]["main"]["pressure"]) / 133.32 * 100, 0)} мм.рт.ст'
                                          f'\nВлажность воздуха {data["list"][j]["main"]["humidity"]}%'
                                          f'\n{data["list"][j]["weather"][0]["description"].title()}{emoji[i]}')

bot.polling(none_stop=True)