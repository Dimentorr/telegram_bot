import os
import dotenv

import telebot
from telebot import types
import requests

import random


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

bot = telebot.TeleBot(os.getenv('TOKEN', 'your token'))

tag = ''


#
def update_env(key, new_value):
    os.environ[f'{key}'] = f'{new_value}'

    dotenv.set_key(dotenv_file, f'{key}', os.environ[f'{key}'])


#
def binance_rub(rub):
    binanceTick1 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB")
    rub_in_btc = binanceTick1.json()['price']
    return (rub * 100) / round(float(rub_in_btc), 8)


#
def order_step(message):
    if message.text == 'В начало':
        start_menu(message)
        return
    id_order = os.getenv('NUM_ORDER')
    order_data = {'id': id_order}
    os.environ['NUM_ORDER'] = str(int(id_order) + 1)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='CITIES')
    bot.send_message(message.from_user.id, text='Выберите город:', reply_markup=keyboard)
    bot.register_next_step_handler(message, city_step, order_data=order_data)


#
def city_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['city'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='DISTRICTS')
    bot.send_message(message.from_user.id, text='Выберите район:', reply_markup=keyboard)
    bot.register_next_step_handler(message, district_step, order_data=order_data)


#
def district_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['district'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='PRODUCTS')
    bot.send_message(message.from_user.id, text='Выберите товар:', reply_markup=keyboard)
    bot.register_next_step_handler(message, product_step, order_data=order_data)


def product_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['product'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='COUNT')
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
    construction_keyboard_product(keyboard, env_name='GET_PRODUCT')
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
    construction_keyboard_product(keyboard, env_name='')
    price = os.getenv('PRICE')

    currency = os.getenv('CURRENCY').split('/')
    order_data['get'] = message.text
    bot.send_message(
        message.from_user.id,
        text=f'''
Id заказа - {order_data['id']}
Город - {order_data['city']}
Район - {order_data['district']}
Заказ - {order_data['count']} {order_data['product']}
Способ получение - {order_data['get']}
Стоимость - {float(price) * float(order_data['count'])} {currency[0]}/{binance_rub(float(price)) * float(order_data['count'])} {currency[1]}
Ожидайте ответа оператора
            ''',
        reply_markup=keyboard
    )
    bot.send_message(os.getenv('OPERATORS_CHAT'), f'''
Id заказа - {order_data['id']}
Город - {order_data['city']}
Район - {order_data['district']}
Заказ - {order_data['count']} {order_data['product']}
Способ получение - {order_data['get']}
Стоимость - {float(price) * float(order_data['count'])} {currency[0]}/{binance_rub(float(price)) * float(order_data['count'])} {currency[1]}
Логин пользователя - @{message.from_user.username}
            ''')


#
def construction_keyboard_product(keyboard, env_name):
    key_back = types.InlineKeyboardButton(text='В начало', callback_data='start')
    keyboard.add(key_back)
    if env_name != '':
        for i in os.getenv(env_name, 'default').split(','):
            key = types.KeyboardButton(text=f'{i}')
            keyboard.add(key)


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
    if message.text == os.getenv('PASSWORD') or password:
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
    update_env(data_name, message.text)
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
        bot.send_message(message.from_user.id, f'''Доступные товары {os.getenv("PRODUCTS")}''')

    bot.send_message(message.from_user.id,
                     f'''Текущее значение переменной {data_name}: {os.getenv(data_name)}
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
        bot.send_message(message.from_user.id, f'''Доступные товары {os.getenv("PRODUCTS")}''')
        bot.register_next_step_handler(message, update_step, data_name='PRICE')
    elif message.text == 'Товар':
        bot.register_next_step_handler(message, update_step, data_name='PRODUCTS')
    elif message.text == 'Город':
        bot.register_next_step_handler(message, update_step, data_name='CITIES')
    elif message.text == 'Район':
        bot.register_next_step_handler(message, update_step, data_name='DISTRICTS')
    elif message.text == 'Количество':
        bot.register_next_step_handler(message, update_step, data_name='COUNT')


#
@bot.message_handler(content_types=['text'])
def callback_inline(call):
    if call.text == 'В начало' or call.text == '/start':
        start_menu(call)
    elif call.text == 'Сделать заказ':
        id_order = random.randint(100000, 1000000)
        order_data = {'id': id_order}
        os.environ['NUM_ORDER'] = str(int(id_order) + 1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        construction_keyboard_product(keyboard, env_name='CITIES')
        bot.send_message(call.from_user.id, text='Выберите город:', reply_markup=keyboard)
        bot.register_next_step_handler(call, city_step, order_data=order_data)
    elif call.text == 'Помощь':
        help_menu(call)
    elif call.text == '/ID':
        bot.send_message(call.chat.id, f'Chat id = {call.chat.id}')
    elif call.text == '/admin':
        password_before_admin_menu(call)


bot.polling(none_stop=True, interval=0)
