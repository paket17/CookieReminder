import asyncio
import os.path
import datetime
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from api_token import token
from settings import text, working_days, hour, minute, time_sleep


def create_connect():
    if not os.path.exists('users.db'):
        db = sqlite3.connect("users.db")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                        user_id INTEGER)
                       """)
    else:
        db = sqlite3.connect("users.db")
    return db


db = create_connect()
cursor = db.cursor()

bot = Bot(token=token)
dp = Dispatcher()

cursor.execute("SELECT user_id FROM users")
user_ids = cursor.fetchall()


@dp.message(Command("start"))
async def command_start_handler(message: types.Message):
    cursor.execute(f"""SELECT user_id FROM users
                       WHERE user_id = {message.chat.id}""")
    if len(cursor.fetchall()) > 0:
        await message.answer("Hello you are already on the mailing list.\n"
                             "To unsubscribe from the mailing list type /stop")
    else:
        global user_ids
        await message.answer("Hello, you have been added to the mailing list.\n"
                             "To unsubscribe from the mailing list type /stop")
        cursor.execute(f"INSERT INTO users (user_id) VALUES ({message.chat.id})")
        db.commit()
        cursor.execute("SELECT user_id FROM users")
        user_ids = cursor.fetchall()


@dp.message(Command("stop"))
async def command_start_handler(message: types.Message):
    cursor.execute(f"""SELECT user_id FROM users
                       WHERE user_id = {message.chat.id}""")
    if len(cursor.fetchall()) > 0:
        global user_ids
        await message.answer("Hello, you have been removed from the mailing list.\n"
                             "To subscribe to the mailing list type /start")
        cursor.execute(f"DELETE FROM users WHERE user_id = ({message.chat.id})")
        db.commit()
        cursor.execute("SELECT user_id FROM users")
        user_ids = cursor.fetchall()
    else:
        await message.answer("Hello, you are not subscribed to the mailing list\n"
                             "To subscribe to the mailing list type /start")


@dp.message(Command("help"))
async def command_start_handler(message: types.Message):
    await message.answer("Hello, I'm a bot that reminds me to go for cookies🍪")


async def send_noti():
    while True:
        time_now = datetime.datetime.now()
        if time_now.weekday() in working_days and time_now.hour == hour and time_now.minute == minute:
            for user_id in user_ids:
                await bot.send_message(user_id[0], text)
        await asyncio.sleep(time_sleep)


async def start():
    try:
        print("Bot is running")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    tasks = [loop.create_task(start()), loop.create_task(send_noti())]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
