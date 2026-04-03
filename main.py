from Bot import Bot
from Db.DataLoader import DataLoader
from dotenv import load_dotenv
import asyncio
import logging

logger = logging.getLogger(__name__)

async def main():
    logger.debug("load_dotenv")
    load_dotenv()

    # logger.debug("database init")
    # await DataLoader.init_db()
    # logger.debug("database init done")
    # logger.debug("database truncate")
    # await DataLoader.truncate_db()
    # logger.debug("database done")
    # logger.debug("load data")
    # await DataLoader.load_data("videos.json")
    # logger.debug("load data done")
    logger.debug("database ready")
    await Bot.main()

if __name__ == "__main__":
    logger.debug("starting bot")
    asyncio.run(main())
