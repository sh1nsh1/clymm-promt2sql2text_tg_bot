from Bot import Bot
from Db.DataLoader import DataLoader
from dotenv import load_dotenv
import asyncio

async def main():
    load_dotenv()

    await DataLoader.init_db()
    await DataLoader.truncate_db()
    await DataLoader.load_data("videos.json")
    await Bot.main()

if __name__ == "__main__":
    asyncio.run(main())
