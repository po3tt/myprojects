#подключение библиотек
from settings import *
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
#конец библиотек-----------------------------------------
#создание таблиц БД
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
btn11 = "Еще"
btn22 = "Хватит"
kb1 = [[types.KeyboardButton(text=btn1),types.KeyboardButton(text=btn2)]]
kb1 = types.ReplyKeyboardMarkup(keyboard=kb1,resize_keyboard=True,input_field_placeholder="Выберите что-либо =)")

#события
class Form(StatesGroup):
    noti = State()
#конец инициализации переменных---------------------------



@form_router.message()
async def start(message: types.Message, state: FSMContext):
    print(message.from_user.id)
    if str(message.from_user.id) in users:
        if message.text=="/start":
            await message.answer("Меню",reply_markup=kb)

        if message.text == btn1 or message.text == btn11:
            print("eeee")
            await state.set_state(Form.noti)


@form_router.message(Form.noti)
async def process_name(message: types.Message, state: FSMContext)-> None:
    await state.update_data(noti=message.text)
    await message.answer(f"Еще?",reply_markup=kb1)



async def main():
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
