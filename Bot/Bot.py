import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from Api.DeepSeekClient import get_sql_from_prompt
from Db.DataLoader import DataLoader

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(name)s: %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logger.debug("initiated ")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    logger.debug(f"/start {message.from_user.id}, {message.from_user.first_name}")
    welcome_text = """
        Привет! Я бот Clymm_testbot. Принимаю запросы к бд в свободной форме на русском языке, исполняю его и возвращаю результат!
    """
    await message.answer(welcome_text)


@dp.message()
async def handle_text(message: Message):
    user_query = message.text
    logger.debug(f"Query {message.from_user.id}, {message.from_user.first_name}")
    try:
        logger.debug("get sql from text")
        logger.debug(user_query)
        sql = await get_sql_from_prompt(user_query)
        await message.answer(f"Сгенерированный SQL:\n\n{str(sql)}")
        logger.debug(f"Запрос:\n{sql}")
        logger.debug("get sql from text DONE")
        logger.debug("get result")
        data = await DataLoader.fetch(sql)
        logger.debug("get result DONE")
        logger.debug(f"row count {len(data)}")
        logger.debug(data)
        logger.debug("format result")
        column_names = f"{'№':<5}"
        columns = data[1].keys()
        logger.debug(f"columns count {len(columns)}")
        for col in columns:
            logger.debug(col)
            column_names += f"{col:<{max(len(col) * 2, 10)}}"

        result = [column_names]
        for num, record in data.items():
            logger.debug(f"format row {num}")
            row = f"{num:<5}"
            for name, value in record.items():
                length = max(len(name) * 2, 10)
                row += f"{str(value)[:length]:<{length + 1}}"
            logger.debug(row)
            result.append(row)

        logger.debug("format result DONE")
        logger.debug(f"Ответ:\n{'\n'.join(result)}")
        await message.answer(f"Результат выполнения:\n\n{'\n'.join(result)}")

    except Exception as e:
        logger.error(e)
        raise


async def main():
    logger.debug("Bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
