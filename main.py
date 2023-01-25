#подключение библиотек
from settings import *
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router, html
from aiogram.fsm.context import FSMContext
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
#конец инициализации переменных---------------------------


@form_router.message()
async def start(message: types.Message, state: FSMContext):
    if message.text=="/start" and str(message.from_user.id) in user:
            await message.answer("Инициализация системы проведена!")#





async def main():
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())