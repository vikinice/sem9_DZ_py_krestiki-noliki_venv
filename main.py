import random
import requests
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import strings as st

def getToken():
    token = ''
    with open(st.PATH, 'r', encoding='utf-8') as file:
        token = file.read()
    
    return token

def isWin(arr, who):
    if (((arr[0] == who) and (arr[4] == who) and (arr[8] == who)) or
            ((arr[2] == who) and (arr[4] == who) and (arr[6] == who)) or
            ((arr[0] == who) and (arr[1] == who) and (arr[2] == who)) or
            ((arr[3] == who) and (arr[4] == who) and (arr[5] == who)) or
            ((arr[6] == who) and (arr[7] == who) and (arr[8] == who)) or
            ((arr[0] == who) and (arr[3] == who) and (arr[6] == who)) or
            ((arr[1] == who) and (arr[4] == who) and (arr[7] == who)) or
            ((arr[2] == who) and (arr[5] == who) and (arr[8] == who))):
        return True
    return False

def countUndefinedCells(cellArray):
    counter = 0
    for i in cellArray:
        if i == st.SYMBOL_UNDEF:
            counter += 1
    return counter

def game(callBackData):
   
    message = st.ANSW_YOUR_TURN  
    alert = None

    buttonNumber = int(callBackData[0])  
    if not buttonNumber == 9:  # цифра 9 передается в первый раз в качестве заглушки. Т.е. если передана цифра 9, то клавиатура для сообщения создается впервые
        charList = list(callBackData)  
        charList.pop(0)  
        if charList[buttonNumber] == st.SYMBOL_UNDEF:  
            charList[buttonNumber] = st.SYMBOL_X  
            if isWin(charList, st.SYMBOL_X):  
                message = st.ANSW_YOU_WIN
            else:  # если крестик не выиграл, то может ходить бот-нолик
                if countUndefinedCells(charList) != 0:  # проверка: есть ли свободные ячейки для хода
                    
                    isCycleContinue = True
                    # запуск бесконечного цикла т.к. необходимо, чтобы бот походил в свободную клетку, а клетка выбирается случайным образом
                    while (isCycleContinue):
                        rand = random.randint(0, 8)  # генерация случайного числа - клетки, для бота
                        if charList[rand] == st.SYMBOL_UNDEF:  
                            charList[rand] = st.SYMBOL_O
                            isCycleContinue = False  # смена значения переменной для остановки цикла
                            if isWin(charList, st.SYMBOL_O):  # проверка: выиграл ли бот после своего кода
                                message = st.ANSW_BOT_WIN

        else:
            alert = st.ALERT_CANNOT_MOVE_TO_THIS_CELL

        if countUndefinedCells(charList) == 0 and message == st.ANSW_YOUR_TURN:
            message = st.ANSW_DRAW

        callBackData = ''
        for c in charList:
            callBackData += c

    if message == st.ANSW_YOU_WIN or message == st.ANSW_BOT_WIN or message == st.ANSW_DRAW:
        message += '\n'
        for i in range(0, 3):
            message += '\n | '
            for j in range(0, 3):
                message += callBackData[j + i * 3] + ' | '
        callBackData = None  # обнуление callBackData
    return message, callBackData, alert

def getKeyboard(callBackData):
    keyboard = [[], [], []] 

    if callBackData != None: 
        for i in range(0, 3):
            for j in range(0, 3):
                keyboard[i].append(InlineKeyboardButton(callBackData[j + i * 3], callback_data=str(j + i * 3) + callBackData))
    
    return keyboard


def newGame(update, _):
    data = ''
    for i in range(0, 9):
        data += st.SYMBOL_UNDEF

    update.message.reply_text(st.ANSW_YOUR_TURN, reply_markup=InlineKeyboardMarkup(getKeyboard(data)))

def button(update, _):
    query = update.callback_query
    callbackData = query.data 

    message, callbackData, alert = game(callbackData) 
    if alert is None:
        query.answer()
        query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(getKeyboard(callbackData)))
    else:
        query.answer(text=alert, show_alert=True)


def start_command(update, _):
    update.message.reply_text(st.ANSW_START)

def help_command(update, _):
    update.message.reply_text(st.ANSW_HELP)

def exception_command(update, _):
    update.message.reply_text(st.ANSW_EXCEPTION)

def image_command(update, _):
    photo_file = update.message.photo[-1].get_file()
    upload = requests.post(st.API_URL_UPLOAD, data=photo_file, verify=False)
    time.sleep(5)
    download = requests.post(st.API_URL_DOWNLOAD, verify=False)
    update.message.reply_photo(photo=download)
  
if __name__ == '__main__':
    updater = Updater(getToken())  # получения токена из файла 'token.txt' и инициализация updater

    # добавление обработчиков
    updater.dispatcher.add_handler(CommandHandler('start', start_command))
    updater.dispatcher.add_handler(CommandHandler('play', newGame))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, image_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, exception_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(button)) 
    

    # Запуск бота
    updater.start_polling()
    updater.idle()