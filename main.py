import os
import json
import time

import telebot
from telebot import types
import requests

import asyncio

import random


def json_load(name: str):
    with open(f'{name}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def update_json(data: dict, new_value: str, key: str, second_key='', name='data.json'):
    if second_key != '':
        data[key][second_key] = new_value
    else:
        data[key] = new_value
    with open(f'{name}', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=3)


json_data = json_load('data.json')

bot = telebot.TeleBot(json_data['TOKEN'])


#
def binance_btc(rub):
    binanceTick1 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB")
    rub_in_btc = binanceTick1.json()['price']
    return rub / round(float(rub_in_btc), 8)


def binance_usdt(rub):
    binanceTick1 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB")
    rub_in_usdt = binanceTick1.json()['price']
    return rub / round(float(rub_in_usdt), 8)


#
def order_step(message):
    if message.text == 'В начало':
        start_menu(message)
        return
    id_order = json_data['NUM_ORDER']
    order_data = {'id': id_order}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='CITIES', order_data=order_data)
    bot.send_message(message.from_user.id, text='Выберите город:', reply_markup=keyboard)
    bot.register_next_step_handler(message, city_step, order_data=order_data)


#
def city_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['city'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='DISTRICTS', order_data=order_data)
    bot.send_message(message.from_user.id, text='Выберите район:', reply_markup=keyboard)
    bot.register_next_step_handler(message, district_step, order_data=order_data)


#
def district_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['district'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='PRODUCTS', order_data=order_data)
    bot.send_message(message.from_user.id, text='Выберите товар:', reply_markup=keyboard)
    bot.register_next_step_handler(message, product_step, order_data=order_data)


def product_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['product'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='COUNT', order_data=order_data)
    bot.send_message(message.from_user.id,
                     text=f'Выберите количество {order_data["product"]}:',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, count_step, order_data=order_data)


#
def count_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['count'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='GET_PRODUCT', order_data=order_data)
    bot.send_message(message.from_user.id,
                     text='Выберите способ получения:',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, operator_step, order_data=order_data)


#
def operator_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='', order_data=order_data)
    price = json_data['PRICE'][order_data['product']]

    currency = json_data['CURRENCY'].split('/')
    order_data['get'] = message.text
    bot.send_message(
        message.from_user.id,
        text=f'''
Id заказа - {order_data['id']}
Город - {order_data['city']}
Район - {order_data['district']}
Заказ - {order_data['count']} {order_data['product']}
Способ получение - {order_data['get']}
Стоимость - {float(price) * float(order_data['count'])} {currency[0]}/{binance_usdt(float(price)) * float(order_data['count'])} {currency[1]}
            ''',
        reply_markup=keyboard
    )
    bot.send_message(json_data['OPERATORS_CHAT'], f'''
Id заказа - {order_data['id']}
Город - {order_data['city']}
Район - {order_data['district']}
Заказ - {order_data['count']} {order_data['product']}
Способ получение - {order_data['get']}
Стоимость - {float(price) * float(order_data['count'])} {currency[0]}/{binance_usdt(float(price)) * float(order_data['count'])} {currency[1]}
Логин пользователя - @{message.from_user.username}
            ''')
    try:
        Pay(message, order_data)
    except Exception as e:
        bot.send_message(
            message.from_user.id,
            text=f'''Произошла ошибка, попробуте повторить попытку позже''')
        bot.send_message(json_data['OPERATORS_CHAT'], f'''Произошла ошибка {e} с заказом {order_data['id']}
Пользователь: @{message.from_user.username}''')


#
def construction_keyboard_product(keyboard, env_name, order_data=dict):
    key_back = types.InlineKeyboardButton(text='В начало', callback_data='start')
    keyboard.add(key_back)
    if env_name != '':
        try:
            for i in json_data[env_name].split(','):
                key = types.KeyboardButton(text=f'{i}')
                keyboard.add(key)
        except Exception as e:
            # print(order_data)
            # возможная причина возникновения этого исключения пока что только 1
            # если появится больше словарей внутри json ужно будет переписать
            for i in json_data[env_name][order_data['city']].split(','):
                key = types.KeyboardButton(text=f'{i}')
                keyboard.add(key)
            # print(e)


#
def keyboard_admin(keyboard):
    key_back = types.InlineKeyboardButton(text='В начало', callback_data='back')
    keyboard.add(key_back)
    # --------------------------------------------------------------------------------
    key_pass = types.InlineKeyboardButton(text='Пароль', callback_data='pass')
    # keyboard.add(key_pass)
    # --------------------------------------------------------------------------------
    key_city = types.InlineKeyboardButton(text='Город', callback_data='city')
    # keyboard.row(key_city)
    # --------------------------------------------------------------------------------
    key_district = types.InlineKeyboardButton(text='Район', callback_data='district')
    # keyboard.add(key_district)
    # --------------------------------------------------------------------------------
    key_product = types.InlineKeyboardButton(text='Товар', callback_data='product')
    # keyboard.add(key_product)
    # --------------------------------------------------------------------------------
    key_sell = types.InlineKeyboardButton(text='Стоимость', callback_data='sell')
    # keyboard.add(key_sell)
    # --------------------------------------------------------------------------------
    key_count = types.InlineKeyboardButton(text='Количество', callback_data='count')
    # keyboard.add(key_count)
    keyboard.row(key_city, key_district)
    keyboard.row(key_product, key_count, key_sell)
    keyboard.add(key_pass)


#
def keyboard_password_admin(keyboard):
    key_back = types.InlineKeyboardButton(text='В начало', callback_data='back')
    keyboard.add(key_back)


#
def keyboard_admin_update_data(keyboard):
    key_back = types.InlineKeyboardButton(text='В начало', callback_data='start')
    keyboard.add(key_back)
    # --------------------------------------------------------------------------------
    key_back_step = types.InlineKeyboardButton(text='Назад к выбору', callback_data='back')
    keyboard.add(key_back_step)


#
def send_image(message, name_img):
    photo = open(f'img/{name_img}', 'rb')
    bot.send_photo(message.from_user.id, photo)
    photo.close()


#
def help_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, '')
    bot.send_message(message.from_user.id, text=f'''
Возможные пути связи
Ответы на общие вопросы
''', reply_markup=keyboard)


#
def start_menu(message):
    # send_image(message, name_img='name')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_help = types.InlineKeyboardButton(text='Помощь', callback_data='')
    keyboard.add(key_help)
    key_back = types.InlineKeyboardButton(text='Сделать заказ', callback_data='start_order')
    keyboard.add(key_back)
    bot.send_message(message.from_user.id,
                     f'''Привет, я бот''', reply_markup=keyboard)


#
def password_before_admin_menu(message):
    if message.text == 'В начало':
        start_menu(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_password_admin(keyboard)
    bot.send_message(message.from_user.id, f'''Введите пароль:''', reply_markup=keyboard)
    bot.register_next_step_handler(message, admin_menu)


#
def admin_menu(message, password=False):
    if message.text == 'В начало':
        start_menu(message)
        return
    if message.text == json_data['PASSWORD'] or password:
        bot.send_message(message.from_user.id, f'''Админ панель
<-------------------------->''')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_admin(keyboard)

        bot.send_message(message.from_user.id, f'''Выберите необходимый пункт''', reply_markup=keyboard)
        bot.register_next_step_handler(message, intermediate_pass_stape)
    else:
        bot.send_message(message.from_user.id, f'''Неверный пароль''')
        bot.register_next_step_handler(message, password_before_admin_menu)


# сохраняем изменения в .env
def invisible_update_step(message, data_name):
    if message.text == 'В начало':
        start_menu(message)
        return
    elif message.text == 'Назад к выбору':
        admin_menu(message, password=True)
        return
    bot.send_message(message.from_user.id, f'''Изменения применены''')

    if '{' in message.text:
        new_data = eval(message.text)
    else:
        new_data = message.text
        print(new_data)
    update_json(data=json_data, new_value=new_data, key=data_name)
    bot.register_next_step_handler(message, admin_menu)


# data_name - это ключ для .env
def update_step(message, data_name):
    if message.text == 'В начало':
        start_menu(message)
        return
    elif message.text == 'Назад к выбору':
        admin_menu(message, password=True)
        return
    bot.send_message(message.from_user.id, f'''Введите новое значение
<-------------------------->''')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_admin_update_data(keyboard)
    if message.text == 'PRICE':
        bot.send_message(message.from_user.id, f'''Доступные товары {json_data["PRODUCTS"]}''')

    bot.send_message(message.from_user.id,
                     f'''Текущее значение переменной {data_name}: {json_data[data_name]}
При необходимости добавления нескольких пунктов используете "," без использования пробелов
''', reply_markup=keyboard)
    bot.register_next_step_handler(message, invisible_update_step, data_name=data_name)


# Передаём дальше необходимый для работы с .env ключ
def intermediate_pass_stape(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_back = types.InlineKeyboardButton(text='Продолжить', callback_data='next')
    keyboard.add(key_back)
    if message.text == 'В начало':
        start_menu(message)
        return
    bot.send_message(message.from_user.id, f'''Вынужденная пауза
<-------------------------->''', reply_markup=keyboard)
    if message.text == 'Пароль':
        bot.register_next_step_handler(message, update_step, data_name='PASSWORD')
    elif message.text == 'Стоимость':
        bot.send_message(message.from_user.id, f'''Доступные товары {json_data["PRODUCTS"]}''')
        bot.register_next_step_handler(message, update_step, data_name='PRICE')
    elif message.text == 'Товар':
        bot.register_next_step_handler(message, update_step, data_name='PRODUCTS')
    elif message.text == 'Город':
        bot.register_next_step_handler(message, update_step, data_name='CITIES')
    elif message.text == 'Район':
        bot.register_next_step_handler(message, update_step, data_name='DISTRICTS')
    elif message.text == 'Количество':
        bot.register_next_step_handler(message, update_step, data_name='COUNT')


coinpayments_url = 'https://www.coinpayments.net/api.php'
merchant_id = json_data['SHOPID'] # Ваш merchant ID в CoinPayments
private_key = json_data['SECRETKEY_COINPAYMENTS'] # Ваш private key в CoinPayments
server = json_data['SERVER']


async def CheckPay(invoice_id, message, order_data):
    url = 'https://api.cryptocloud.plus/v1/invoice/info'
    api_key = json_data['APIKEY_COINPAYMENTS']

    headers = {'Authorization': f'Token {api_key}'}
    params = {'uuid': f'INV-{invoice_id}'}
    while True:
        # ожидание между запросами к платёжной системе за ответом,
        # при необходимости сделать больше или меньше
        # wait_time - количество секунд между запросами
        wait_time = 15
        time.sleep(wait_time)
        response = requests.get(
            url,
            headers=headers,
            params=params
        )
        invoice = response.json()
        if invoice.get('status_invoice') == 'paid':
            bot.send_message(json_data['OPERATORS_CHAT'], f'''
Заказ: {order_data['id']}
Логин пользователя - @{message.from_user.username}
INV-{invoice_id}
Статус - Оплачен''')
            bot.send_message(message.from_user.id, text=f'''Счёт: INV-{invoice_id} был оплачен!
Ожидайте пока оператор с вами свяжется''')
            break
        elif invoice.get('status_invoice') != 'paid' and invoice.get('status_invoice') != 'created':
            bot.send_message(json_data['OPERATORS_CHAT'], f'''
            Заказ: {order_data['id']}
            Логин пользователя - @{message.from_user.username}
            INV-{invoice_id}
            Статус - Отменён''')

            bot.send_message(message.from_user.id, text=f'''Счёт: INV-{invoice_id} был отменён!''')
            break


async def PayWithAPICryptoCloud(message, order_data):
    api_key = json_data['APIKEY_COINPAYMENTS']
    rub = float(json_data['PRICE'][order_data['product']])
    price = binance_usdt(rub)
    count = float(order_data['count'])

    headers = {
        "Authorization": f"Token {api_key}"
    }

    payload = {
        "shop_id": json_data['SHOPID'],
        'amount': price * count,
        'currency1': json_data['CURRENCY'].split('/')[1],
        'currency2': json_data['CURRENCY'].split('/')[1],
        'item_name': order_data['product'],
    }

    response = requests.post(
        "https://api.cryptocloud.plus/v1/invoice/create",
        headers=headers,
        data=payload
    )

    invoice_info = response.json()
    bot.send_message(message.from_user.id,
                     text=f'''Ссылка на оплату : {invoice_info.get('pay_url', None)}
Id заказа: INV-{invoice_info.get('invoice_id', None)}''')
    bot.send_message(json_data['OPERATORS_CHAT'], f'''
Заказ: {order_data['id']}
Логин пользователя - @{message.from_user.username}
INV-{invoice_info.get('invoice_id', None)}
Статус - В ожидании оплаты''')
    await CheckPay(invoice_info.get('invoice_id', None), message, order_data)


def Pay(message, order_data):
    asyncio.run(PayWithAPICryptoCloud(message, order_data))


#
@bot.message_handler(content_types=['text'])
def callback_inline(call):
    if call.text == 'В начало' or call.text == '/start':
        start_menu(call)
    elif call.text == 'Сделать заказ':
        id_order = random.randint(100000, 1000000)
        order_data = {'id': id_order}
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        construction_keyboard_product(keyboard, env_name='CITIES', order_data=order_data)
        bot.send_message(call.from_user.id, text='Выберите город:', reply_markup=keyboard)
        bot.register_next_step_handler(call, city_step, order_data=order_data)
    elif call.text == 'Помощь':
        help_menu(call)
    elif call.text == '/ID':
        bot.send_message(call.chat.id, f'Chat id = {call.chat.id}')
    elif call.text == '/admin':
        password_before_admin_menu(call)
    else:
        bot.send_message(call.from_user.id, text='Я не знаю данной команды')
        start_menu(call)


bot.polling(none_stop=True, interval=0)
