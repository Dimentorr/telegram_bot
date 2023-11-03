import os
import dotenv

import telebot
from telebot import types

dotenv.load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN', 'your token'))


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


def city_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
    order_data['city'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, env_name='DISTRICTS')
    bot.send_message(message.from_user.id, text='Выберите район:', reply_markup=keyboard)
    bot.register_next_step_handler(message, district_step, order_data=order_data)


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


def operator_step(message, order_data):
    if message.text == 'В начало':
        start_menu(message)
        return
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
    key_back = types.InlineKeyboardButton(text='В начало', callback_data='start')
    keyboard.add(key_back)
    if env_name != '':
        for i in os.getenv(env_name, 'default').split(','):
            key = types.KeyboardButton(text=f'{i}')
            keyboard.add(key)


def send_image(message, name_img):
    photo = open(f'img/{name_img}', 'rb')
    bot.send_photo(message.from_user.id, photo)
    photo.close()


def help_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    construction_keyboard_product(keyboard, '')
    bot.send_message(message.from_user.id, text=f'''
Возможные пути связи
Ответы на общие вопросы
''', reply_markup=keyboard)



def start_menu(message):
    # bot.send_message(message.chat.id, f'Chat id = {message.chat.id}')
    # send_image(message, name_img='name')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_help = types.InlineKeyboardButton(text='Помощь', callback_data='')
    keyboard.add(key_help)
    key_back = types.InlineKeyboardButton(text='Сделать заказ', callback_data='start_order')
    keyboard.add(key_back)
    bot.send_message(message.from_user.id,
                     f'''Привет, я бот''', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def callback_inline(call):
    if call.text == 'В начало' or call.text == '/start':
        start_menu(call)
    elif call.text == 'Сделать заказ':
        id_order = os.getenv('NUM_ORDER')
        order_data = {'id': id_order}
        os.environ['NUM_ORDER'] = str(int(id_order) + 1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        construction_keyboard_product(keyboard, env_name='CITIES')
        bot.send_message(call.from_user.id, text='Выберите город:', reply_markup=keyboard)
        bot.register_next_step_handler(call, city_step, order_data=order_data)
    elif call.text == 'Помощь':
        help_menu(call)


bot.polling(none_stop=True, interval=0)
