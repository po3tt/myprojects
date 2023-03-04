#подключение библиотек
from decouple import config
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
name_db = "noty.db"
#конец библиотек-----------------------------------------
#создание таблиц БД
connect = sqlite3.connect(name_db)
current = connect.cursor()
current.execute("CREATE TABLE IF NOT EXISTS notify(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT, data_add TEXT, what TEXT, whens TEXT, statuses BOOLEAN, repeater TEXT);")
connect.commit()
current.close()

# конец создание таблиц БД--------------------------------
#инициализация переменных
bot = Bot(token=config('my_token',default=''), parse_mode="HTML")
form_router = Router()
scheduler = AsyncIOScheduler()
#кнопки
btn1 = "Добавить"
btn2 = "Посмотреть БД"
btn3 = "Удалить задачи"
btn4 = "Редактировать задачу"
kb = [[types.KeyboardButton(text=btn1),types.KeyboardButton(text=btn2)],[types.KeyboardButton(text=btn3),types.KeyboardButton(text=btn4)]]
kb = types.ReplyKeyboardMarkup(keyboard=kb,one_time_keyboard=False, resize_keyboard=True,input_field_placeholder="Выберите что-либо =)")


#события
class Form(StatesGroup):
    noti = State()
    times = State()
    id = State()
    delete = State()
    edit = State()
#конец инициализации переменных---------------------------
            
async def send_notify(text):
    if text[6]!="1":      
        func.query_for_db(f'UPDATE notify SET statuses=1 WHERE id={text[0]};')
        buttons = [[types.InlineKeyboardButton(text="Напомнить через...", callback_data="remind-"+str(text[0])+"-"+str(text[3])),]]
    else:
        buttons = [[types.InlineKeyboardButton(text="Выполнено", callback_data="done-"+str(text[0])+"-"+str(text[3])),]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(str(text[1]), str(text[3]), reply_markup=keyboard)

    
@form_router.callback_query()
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.split("-")[0]=="done":
        func.query_for_db(f'UPDATE notify SET statuses=1 WHERE id={callback.data.split("-")[1]};')
        await callback.message.edit_text(f'"{callback.data.split("-")[2]}" \n\n Задача выполнена!')
    elif callback.data.split("-")[0]=="remind":
        await state.set_state(Form.times)
        await state.update_data(id=callback.data.split("-")[1])
        await callback.message.answer(f'Через сколько напомнить о "{callback.data.split("-")[2]}" ? ("1"-мин, "1 ч"-час, "1 д"-день, "г"-год)')
    if callback.data == "отменить":
        await state.clear()
        await callback.message.edit_text(f"Отменено!")

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
    await message.delete()
    await message.answer(f"Отлично! Напомню {new_time}!")
    await state.clear()
    


@form_router.message(Form.noti)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await state.update_data(noti=message.text)
    if "-" in message.text:
        text_noti = ""
        add_noty = []
        for i in message.text.split("\n"):
            add_noty.append(i.replace(" - ","-").replace("- ","-").replace(" -","-").split("-"))
        for i in add_noty:
            text_noti+=i[0]+"\n"
            mass = func.learn_notify(i)
            func.query_for_db(f'INSERT INTO notify(user_id, data_add, what, whens, statuses, repeater) VALUES ("{message.from_user.id}","{datetime.now().strftime("%d.%m.%Y %H:%M")}","{i[0]}","{mass[0]}",0,"{mass[1]}");')
        await message.answer(f"{text_noti} \nВыполним точно в срок!")
        await state.clear()
    else:
        await message.delete()
        await message.edit_text(f"Неправильный формат ввода! Обрати внимание на образец!")
        
        

@form_router.message(Form.delete)
async def process_name(message: types.Message, state: FSMContext)-> None:
    for i in message.text.split(" "):
        func.query_for_db(f'DELETE FROM notify WHERE id = {int(i)};')
    await state.clear()
    await message.answer("Готово! Задачи удалены!")

@form_router.message(Form.edit)
async def process_name(message: types.Message, state: FSMContext)-> None:
    new_text=message.text.replace(" - ","-").replace("- ","-").replace(" -","-")
    conn = sqlite3.connect(name_db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM notify;")
    one_result = cur.fetchall()
    print(one_result)
    if one_result!=[]:
        func.query_for_db(f'UPDATE notify SET what="{new_text.split("-")[1]}", whens="{new_text.split("-")[2]}", statuses=0 WHERE id={int(new_text.split("-")[0])};')
        await message.answer("Готово! Задача отредактирована!")
    else:
        await message.edit_text("Нечего редактировать!")
    await state.clear()
    


@form_router.message()
async def start(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in config('users',default=''):
        if message.text=="/start":
            await message.answer("Для начала вам необходимо добавить задачу",reply_markup=kb)

        if message.text == btn1:
            
            await state.set_state(Form.noti)
            buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data="отменить"),]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(
            f"""Введите в формате:\nзадача-ДД.ММ.ГГГГ ЧЧ:ММ | ДД.ММ.ГГГГ | ежедневно в ЧЧ:ММ | др ДД.ММ | в ЧЧ:ММ | каждую пт | вс | пт в ЧЧ:ММ)""", reply_markup=keyboard)
        
        if message.text == btn2:
            conn = sqlite3.connect(name_db)
            cur = conn.cursor()
            cur.execute("SELECT * FROM notify;")
            one_result = cur.fetchall()
            sms = "Формат вывода:\nид - задача - когда - выполнение - повторение\n\n"
            one_result = sorted(one_result, key=lambda x: x[4])
            for i in one_result:
                sms+=f'''{i[0]} - {i[3]} - {i[4]} - {i[5]} - {i[6]}\n'''
            if sms != "Формат вывода:\nид - задача - когда - выполнение - повторение\n\n":
               await message.answer(sms)
            else:
                await message.answer("Нет задач!")


        if message.text == btn3:

            await state.set_state(Form.delete)
            buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data="отменить"),]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(f"Указать ид задачи через пробел: 1 13 20 ...", reply_markup=keyboard)

        if message.text == btn4:
            await state.set_state(Form.edit)
            buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data="отменить"),]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(f"Форма ввода: ид-задача-когда", reply_markup=keyboard)
                
            

async def main():
    scheduler.add_job(func.check_notify, "interval", seconds=60)
    scheduler.start()
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


