#подключение библиотек
from settings import *
import sys
import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
from datetime import timedelta, datetime, date, time
import func
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types, F, Router, html
from aiogram.utils.keyboard import InlineKeyboardBuilder
#конец библиотек-----------------------------------------
#создание таблиц БД
connect = sqlite3.connect(name_db)
current = connect.cursor()
current.execute("CREATE TABLE IF NOT EXISTS notify(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT, data_add TEXT, what TEXT, whens TEXT, statuses BOOLEAN, repeater TEXT);")
connect.commit()
current.close()

# конец создание таблиц БД--------------------------------
#инициализация переменных
bot = Bot(token=my_token, parse_mode="HTML")
form_router = Router()
scheduler = AsyncIOScheduler()
#кнопки
btn1 = "Добавить"
btn2 = "Посмотреть БД"
btn3 = "Тест"
kb = [[types.KeyboardButton(text=btn1),types.KeyboardButton(text=btn2)],[types.KeyboardButton(text=btn3)]]
kb = types.ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True,input_field_placeholder="Выберите что-либо =)")


#события
class Form(StatesGroup):
    noti = State()
    times = State()
    id = State()
#конец инициализации переменных---------------------------
            
global itog
itog = 10

async def send_notify(text):         
    buttons = [[types.InlineKeyboardButton(text="Выполнено", callback_data="done-"+str(text[0])+"-"+str(text[3])),],
              [types.InlineKeyboardButton(text="Напомнить через...", callback_data="remind-"+str(text[0])),]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(str(text[1]), str(text[3]), reply_markup=keyboard)
    if len(text[4])<6:
        func.query_for_db(f'UPDATE notify SET whens="{(datetime.strptime(text[4], "%H:%M")+timedelta(minutes=func.interval_alarm)).strftime("%H:%M")}" WHERE id={str(text[0])};')
    else:
        func.query_for_db(f'UPDATE notify SET whens="{(datetime.strptime(text[4], "%d.%m.%Y %H:%M")+timedelta(minutes=func.interval_alarm)).strftime("%d.%m.%Y %H:%M")}" WHERE id={str(text[0])};')

    
@form_router.callback_query()
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    print(callback.data)
    if callback.data.split("-")[0]=="done":
        func.query_for_db(f'UPDATE notify SET statuses=1 WHERE id={callback.data.split("-")[1]};')
        await callback.message.answer(f'"{callback.data.split("-")[2]}" \n\n Задача выполнена!')
    elif callback.data.split("-")[0]=="remind":
        await state.set_state(Form.times)
        await state.update_data(id=callback.data.split("-")[1])
        await callback.message.answer(f"Через сколько напомнить? ('1'-мин, '1 ч'-час, '1 д'-день, 'г'-год)")
            

@form_router.message(Form.times)
async def process_name1(message: types.Message, state: FSMContext)-> None: #функция для кнопки "Напомнить через....", отрабатывает сообщение от пользователя чтобы перенести на заданный интервал
    new_time = datetime.now()
    if message.text == "г":
        new_time = (datetime.now()+timedelta(days=365)).strftime("%d.%m.%Y 07:00")
    elif "д" in message.text:
        new_time = (datetime.now()+timedelta(days=int(message.text.split(" ")[0]))).strftime("%d.%m.%Y 07:00")
    elif "ч" in message.text:
        new_time = (datetime.now()+timedelta(hours=int(message.text.split(" ")[0]))).strftime("%d.%m.%Y %H:%M")
    else:
        new_time = (datetime.now()+timedelta(minutes=int(message.text.split(" ")[0]))).strftime("%d.%m.%Y %H:%M")
    await state.update_data(times=message.text)
    user_data = await state.get_data()
    func.query_for_db(f'UPDATE notify SET whens="{new_time}" WHERE id={user_data["id"]};')
    await message.answer(f"Отлично! Напомню {new_time}!")
    await state.clear()
    


@form_router.message(Form.noti)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await state.update_data(noti=message.text)
    if "-" in message.text:
        add_noty = [i.split("-") for i in message.text.split("\n")]
        for i in add_noty:
            func.query_for_db(f'INSERT INTO notify(user_id, data_add, what, whens, statuses) VALUES ("{message.from_user.id}","{datetime.now().strftime("%d.%m.%Y %H:%M")}","{i[0]}","{func.learn_notify(i)}",0);')
        await message.answer(f"Задачи добавлены!")
        await state.clear()
    else:
        await message.answer(f"Неправильный формат ввода!")

@form_router.message()
async def start(message: types.Message, state: FSMContext):
    print(message.text)
    if str(message.from_user.id) in users:
        if message.text=="/start":
            await message.answer("Меню",reply_markup=kb)

        if message.text == btn1:
            await state.set_state(Form.noti)
            await message.answer(f"Введите задачу и когда напомнить в формате: задача-когда/ДД.ММ.ГГГГ НН:ММ/ДД.ММ.ГГГГ/НН:ММ", reply_markup=kb)
            
        if message.text == btn2:
            conn = sqlite3.connect(name_db)
            cur = conn.cursor()
            cur.execute("SELECT * FROM notify WHERE statuses!=1;")
            one_result = cur.fetchall()
            #notify(id,user_id, data_add, what, whens, statuses, repeater)
            sms = ""
            one_result = sorted(one_result, key=lambda x: x[4])
            for i in one_result:
                sms+=f'{i[3]} - {i[4]}\n'
            await message.answer(sms)

async def main():
    scheduler.add_job(func.check_notify, "interval", seconds=10)
    scheduler.start()
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
