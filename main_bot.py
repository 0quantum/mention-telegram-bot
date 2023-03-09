import sqlite3
import logging

from config import settings

import aiogram
from aiogram import Bot, Dispatcher, executor, types, filters

logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings['token'])
dp = Dispatcher(bot)

conn = sqlite3.connect('db/usersAndChats.db', check_same_thread=False)
cur = conn.cursor()

def addToDb(user_name,user_id,username,chat_id):
    cur.execute('INSERT OR REPLACE INTO users (id, name, username, chat_id) VALUES (?, ?, ?, ?)', (user_id, user_name, username, chat_id))
    conn.commit()

async def is_bot_admin(chat_id):
    # Отримуємо об'єкт ChatMember про бота в чаті
    bot_member = await bot.get_chat_member(chat_id, bot.id)
    # Перевіряємо, чи має бот адміністративні права
    return bot_member.is_chat_admin()



@dp.message_handler(commands=['what'])
async def what(message: types.Message):
    await bot.send_message(message.chat.id, f'''Коротко поясню. Бот створений для того, щоб тегати юзерів.

🤨 *Команди:*
/call - Покликати усіх!

/reg - Вийти з заклику
/unreg - Зайти в заклик''', parse_mode="Markdown")

@dp.message_handler(commands=['unreg'])
async def unreg(message: types.Message):
    cur.execute(f"UPDATE users SET unreg = 1 WHERE chat_id = '{message.chat.id}' AND id = {message.from_user.id}")
    conn.commit()

    await bot.send_message(message.chat.id, f'Ви вийшли зі строю...', parse_mode="Markdown")

@dp.message_handler(commands=['reg'])
async def unreg(message: types.Message):
    cur.execute(f"UPDATE users SET unreg = 0 WHERE chat_id = '{message.chat.id}' AND id = {message.from_user.id}")
    conn.commit()

    await bot.send_message(message.chat.id, f'Ви у строю!', parse_mode="Markdown")

@dp.message_handler(commands=['call'])
async def call(message: types.Message):
    if await is_bot_admin(message.chat.id):
        results = cur.execute(f"SELECT id FROM users WHERE chat_id = '{message.chat.id}' AND unreg != 1").fetchall()
        user_ids = [result[0] for result in results]

        while user_ids:
            current_users = user_ids[:4]
            user_ids = user_ids[4:]
            try:
                message_text = message.text.split('/call ')[1]+' '
            except:
                message_text = 'У СТРІЙ! '
            for user_id in current_users:
                message_text += f'[😎](tg://user?id={user_id}) '
            await bot.send_message(message.chat.id, f'{message_text}', parse_mode="Markdown")
    else:
        await bot.send_message(message.chat.id, f'дайте ботику адмінку, бо плакати буде', parse_mode="Markdown")


@dp.message_handler(content_types=['text'])
async def chatCheck(message):
    try:
        user = cur.execute(f"SELECT id FROM users WHERE chat_id = '{message.chat.id}' AND id = {message.from_user.id}").fetchone()
        if user == None:
            addToDb(message.from_user.first_name,message.from_user.id,message.from_user.username,message.chat.id)
        else:
            return
    except:
        addToDb(message.from_user.first_name,message.from_user.id,message.from_user.username,message.chat.id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
