from Bot import Bot
from Db.DataLoader import DataLoader
from dotenv import load_dotenv
import asyncio

load_dotenv()

asyncio.run(DataLoader.init_db())
asyncio.run(DataLoader.trancate_db())
asyncio.run(DataLoader.load_data("videos.json"))
asyncio.run(Bot.main())