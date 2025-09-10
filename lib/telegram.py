import asyncio
import datetime

import logging
import time
from lib.flat_manager import getNewFlats
from aiogram import Bot, Dispatcher, types

TOKEN = "8319490186:AAEWuadg3Ld5p1dfx7addtHkhKXnarfwxHY"

users = set()

# Глобальная переменная для контроля задачи поиска

async def start_polling():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    search_task = None

    @dp.message()
    async def message_handler(msg: types.Message):
        user_id = msg.from_user.id
        print (user_id)
        users.add(user_id)
        await msg.answer("Вы подписаны на получение новых объявлений.")

        nonlocal search_task
        if search_task is None or search_task.done():
            search_task = asyncio.create_task(search_flat(bot))

    #543510374
    # Start polling
    await dp.start_polling(bot)
    
async def search_flat(bot):
        global users  # Declare users as global
        while True:
            async with asyncio.Lock():
                if users:  # Проверяем, что есть пользователи для отправки
                    flats = getNewFlats()
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{current_time} - {len(flats)} flats")
                    for user_id in users.copy():  # Делаем копию множества пользователей
                        for flat in flats:
                            await bot.send_message(user_id, flat)
                            print(f"{current_time} - {flat}")
                        #if(len(flats) == 0):
                        #    await bot.send_message(user_id, 'ыыыыыыыыы!!!')

            await asyncio.sleep(10 * 60)

async def start():
    logging.basicConfig(level=logging.INFO)
    await start_polling()
