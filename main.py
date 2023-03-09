#подключение библиотек
from decouple import config
import sys
import asyncio
import logging
import sqlite3
import time
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
    noti1 = State()
    times = State()
    times1 = State()
    id = State()
    delete = State()
    delete1 = State()
    edit = State()
    edit1 = State()

#конец инициализации переменных---------------------------
async def save_msg(id,msg):
    await bot.delete_message(id, msg)

async def del_msg(id,msg,sec):
    await asyncio.sleep(sec)
    await bot.delete_message(id, msg)


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
        msg = await callback.message.answer(f'Через сколько напомнить о "{callback.data.split("-")[2]}" ? ("1"-мин, "1 ч"-час, "1 д"-день, "г"-год)')
        await state.update_data(times1=[msg.chat.id, msg.message_id])

    if callback.data == "отменить":
        await state.clear()
        await callback.message.edit_text(f"Отменено!")
        await del_msg(callback.message.chat.id, callback.message.message_id, 10)

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
    msg_data = await state.get_data()
    await state.clear()
    await save_msg(msg_data["times1"][0], msg_data["times1"][1])
    


@form_router.message(Form.noti)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await state.update_data(noti=message.text)
    if "-" in message.text:
        text_noti = ""
        add_noty = []
        for i in message.text.split("\n"):
            add_noty.append(i.replace(" - ","-").replace("- ","-").replace(" -","-").split("-"))
        for i in add_noty:
            mass = func.learn_notify(i)
            func.query_for_db(f'INSERT INTO notify(user_id, data_add, what, whens, statuses, repeater) VALUES ("{message.from_user.id}","{datetime.now().strftime("%d.%m.%Y %H:%M")}","{i[0]}","{mass[0]}",0,"{mass[1]}");')
            text_noti+=i[0]+" - "+i[1]+"\n"
        await save_msg(message.chat.id, message.message_id)
        msg_data = await state.get_data()
        await state.clear()
        await save_msg(msg_data["noti1"][0], msg_data["noti1"][1])
        await message.answer(f"{text_noti} \nВыполним точно в срок!")
        #await bot.edit_message_text(f"{text_noti} \nВыполним точно в срок!", chat_id=msg_data["noti1"][0], message_id=msg_data["noti1"][1])
    else:
        await message.delete()
        msg = await message.answer(f"Неправильный формат ввода! Обрати внимание на образец!")
        await del_msg(msg.chat.id,msg.message_id,10)

    
        

@form_router.message(Form.delete)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await save_msg(message.chat.id, message.message_id)
    del_message = ""
    for i in message.text.split(" "):
        conn = sqlite3.connect(name_db)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM notify WHERE id = {int(i)};")
        one_result = cur.fetchall()
        if one_result!=[]:
            func.query_for_db(f'DELETE FROM notify WHERE id = {int(i)};')
            del_message+=(i+" - Удалена \n")
        else:
            del_message+=(i+" - Нет такой задачи\n")
        cur.close() 
    msg = await message.answer(f"Удаление проведено! Результат: \n{del_message}")
    await del_msg(msg.chat.id,msg.message_id,300)
    msg_data = await state.get_data()
    await state.clear()
    await save_msg(msg_data["delete1"][0], msg_data["delete1"][1])


@form_router.message(Form.edit)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await save_msg(message.chat.id, message.message_id)
    new_text=message.text.replace(" - ","-").replace("- ","-").replace(" -","-")
    conn = sqlite3.connect(name_db)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM notify WHERE id={int(new_text.split("-")[0])};')
    one_result = cur.fetchall()
    cur.close()
    if one_result!=[]:
        func.query_for_db(f'UPDATE notify SET what="{new_text.split("-")[1]}", whens="{new_text.split("-")[2]}", statuses=0 WHERE id={int(new_text.split("-")[0])};')
        await message.answer(f"Готово! Задача\n{message.text} \nотредактирована!")
        msg_data = await state.get_data()
        await save_msg(msg_data["edit1"][0], msg_data["edit1"][1])
        await state.clear()
    else:
        msg = await message.answer("Такой задачи нет или что-то пошло не так! Попробуйте еще раз!")
        await del_msg(msg.chat.id,msg.message_id,10)
    


@form_router.message()
async def start(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in config('users',default=''):
        if message.text=="/start":
            await message.answer("Для начала вам необходимо добавить задачу!",reply_markup=kb)
            

        if message.text == btn1:
            await state.set_state(Form.noti)
            buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data="отменить"),]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            await save_msg(message.chat.id, message.message_id)
            msg = await message.answer(f"""Введите в формате:\nЗАДАЧА - КОГДА_ВЫПОЛНИТЬ\n\nВарианты для напоминания: \nДД.ММ.ГГГГ ЧЧ:ММ \nДД.ММ.ГГГГ \nежедневно в ЧЧ:ММ \nдр ДД.ММ \nв ЧЧ:ММ \nкаждую/-ый/-ое ДН \nДН \nДН в ЧЧ:ММ \nзавтра \nпослезавтра \nчерез неделю \nзавтра в ЧЧ:ММ \n\n\n ДН - день недели в формате пн или вт или ср...""", reply_markup=keyboard)
            await state.update_data(noti1=[msg.chat.id, msg.message_id])
            
        if message.text == btn2:
            conn = sqlite3.connect(name_db)
            cur = conn.cursor()
            cur.execute("SELECT * FROM notify;")
            one_result = cur.fetchall()
            await save_msg(message.chat.id, message.message_id)
            sms = "Формат вывода:\nид - задача - когда - выполнение - повторение\n\n"
            #one_result = sorted(one_result, key=lambda x: x[4] if datetime.strptime(x[4],"%d.%m.%Y %H:%M") else (x[4] if datetime.strptime(x[4],"%H:%M") else (x[4] if datetime.strptime(x[4],"%d.%m.%Y") else (x[4] if datetime.strptime(x[4],"%d.%m %H:%M") else (x[4] if datetime.strptime(x[4],"%H:%M %A") else "")))))
            for i in one_result:
                sms+=f'''{i[0]} - {i[3]} - {i[4]} - {i[5]} - {i[6]}\n'''
            if sms != "Формат вывода:\nид - задача - когда - выполнение - повторение\n\n":
               msg = await message.answer(sms)
               await del_msg(msg.chat.id,msg.message_id,300)
            else:
               msg = await message.answer("Нет задач!")
               await del_msg(msg.chat.id,msg.message_id,30)


        if message.text == btn3:
            await state.set_state(Form.delete)
            await save_msg(message.chat.id, message.message_id)
            buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data="отменить"),]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            msg = await message.answer(f"Указать ид задачи через пробел: 1 13 20 ...", reply_markup=keyboard)
            await state.update_data(delete1=[msg.chat.id, msg.message_id])
            
        if message.text == btn4:
            await state.set_state(Form.edit)
            await save_msg(message.chat.id, message.message_id)
            buttons = [[types.InlineKeyboardButton(text="Отмена", callback_data="отменить"),]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            msg = await message.answer(f"Форма ввода: ид-задача-когда", reply_markup=keyboard)
            await state.update_data(edit1=[msg.chat.id, msg.message_id])
                
            

async def main():
    scheduler.add_job(func.check_notify, "interval", seconds=60)
    scheduler.start()
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


