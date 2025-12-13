from dotenv import load_dotenv
from Api.DeepSeekClient import get_sql_from_prompt
from Db.DataLoader import DataLoader
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = """
        Привет! Я бот Clymm_testbot. Принимаю запросы к бд в свободной форме на русском языке, исполняю его и возвращаю результат! 
    """
    await message.answer(welcome_text)

@dp.message()
async def handle_text(message: Message):
    user_quary = message.text
    
    try:
        sql = await get_sql_from_prompt(user_quary)
        result = await DataLoader.fetch(sql)
        print(f"Запрос:\n{sql}\nОтвет:\n{result[0]}")
        await message.answer(str(result[0]))
        
        
    except Exception as e:
        print(e)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

