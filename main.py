import os
import dotenv

import telebot
from telebot import types

dotenv.load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN', 'your token'))


def city_step(message, order_data):
    order_data['city'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='DISTRICTS')
    bot.send_message(message.from_user.id, text='Выберите район:', reply_markup=keyboard)
    bot.register_next_step_handler(message, district_step, order_data=order_data)


def district_step(message, order_data):
    order_data['district'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='PRODUCTS')
    bot.send_message(message.from_user.id, text='Выберите товар:', reply_markup=keyboard)
    bot.register_next_step_handler(message, product_step, order_data=order_data)


def product_step(message, order_data):
    order_data['product'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='COUNT')
    bot.send_message(message.from_user.id,
                     text=f'Выберите количество {order_data["product"]}:',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, count_step, order_data=order_data)


def count_step(message, order_data):
    order_data['count'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='GET_PRODUCT')
    bot.send_message(message.from_user.id,
                     text='Выберите способ получения:',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, operator_step, order_data=order_data)


def operator_step(message, order_data):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='')
    price = os.getenv('PRICE').split('/')
    order_data['get'] = message.text
    bot.send_message(
        message.from_user.id,
        text=f'''
Id заказа - {order_data['id']}
Город - {order_data['city']}
Район - {order_data['district']}
Заказ - {order_data['count']} {order_data['product']}
Способ получение - {order_data['get']}
Стоимость - {float(price[0]) * float(order_data['count'])}/{float(price[1]) * float(order_data['count'])}
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
Стоимость - {float(price[0]) * float(order_data['count'])}/{float(price[1]) * float(order_data['count'])}
Логин пользователя - @{message.from_user.username}
            ''')


def construction_keyboard_product(keyboard, env_name):
    key_back = types.InlineKeyboardButton(text='Вернуться', callback_data='start')
    keyboard.add(key_back)
    if env_name != '':
        for i in os.getenv(env_name, 'default').split(','):
            key = types.KeyboardButton(text=f'{i}')
            keyboard.add(key)


def send_image(message, name_img):
    photo = open(f'img/{name_img}', 'rb')
    bot.send_photo(message.from_user.id, photo)
    photo.close()


@bot.message_handler(commands=['help'])
def help_com(message):
    bot.send_message(message.from_user.id, 'Помощь')


@bot.message_handler(commands=['start'])
def start(message):
    # bot.send_message(message.chat.id, f'Chat id = {message.chat.id}')
    id_order = os.getenv('NUM_ORDER')
    order_data = {'id': id_order}
    os.environ['NUM_ORDER'] = str(int(id_order)+1)
    # send_image(message, name_img='name')
    bot.send_message(message.from_user.id,
                     f'''Привет, я бот''')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='CITIES')
    bot.send_message(message.from_user.id, text='Выберите город:', reply_markup=keyboard)
    bot.register_next_step_handler(message, city_step, order_data=order_data)


bot.polling(none_stop=True, interval=0)