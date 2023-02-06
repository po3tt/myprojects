#подключение библиотек
from settings import *
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
import datetime
import func
#конец библиотек-----------------------------------------
#создание таблиц БД
db = []



'''
connect = sqlite3.connect('noty.db')
current = connect.cursor()
current.execute("CREATE TABLE IF NOT EXISTS notify(data_add DATE, what TEXT, when DATE, status TEXT, repeat_after DATE);")
connect.commit()
current.close()
'''
# конец создание таблиц БД--------------------------------
#инициализация переменных
bot = Bot(token=my_token, parse_mode="HTML")
form_router = Router()
#кнопки
btn1 = "Добавить"
btn2 = "Удалить"
btn3 = "Тест"
kb = [[types.KeyboardButton(text=btn1),types.KeyboardButton(text=btn2)],[types.KeyboardButton(text=btn3)]]
kb = types.ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True,input_field_placeholder="Выберите что-либо =)")


#события
class Form(StatesGroup):
    noti = State()
#конец инициализации переменных---------------------------



@form_router.message(Form.noti)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await state.update_data(noti=message.text)
    if "-" in message.text:
        add_noty = [i.split("-") for i in message.text.split("\n")]
        for i in add_noty:
            db.append([datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),i[0],str(func.learn_notify(i)),"",""])
        print(db)
        await message.answer(f"Задачи добавлены!")
        await state.clear()
    else:
        await message.answer(f"Неправильный формат ввода!")

@form_router.message()
async def start(message: types.Message, state: FSMContext):
    print(message.from_user.id)
    if str(message.from_user.id) in users:
        if message.text=="/start":
            await message.answer("Меню",reply_markup=kb)

        if message.text == btn1:
            await state.set_state(Form.noti)
            await message.answer(f"Введите задачу и когда напомнить в формате: задача-когда/ДД.ММ.ГГГГ НН:ММ", reply_markup=kb)
            


async def main():
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
