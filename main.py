from Db.DataLoader import DataLoader
from Api.DeepSeekClient import get_sql_from_promt
from dotenv import load_dotenv
import asyncio

load_dotenv()

prompt = "На сколько просмотров в сумме выросли все видео 28 ноября 2025?"
sql = asyncio.run(get_sql_from_promt(prompt))
print(sql)
result = asyncio.run(DataLoader.fetch(sql))
print(result[0])
