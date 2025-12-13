from Models import Video
import aiofiles
import ijson

class AsyncJSONParser:
    @staticmethod
    async def parse_file(file_path: str):
        async with aiofiles.open(file_path, 'rb') as f:
            async for video in AsyncJSONParser.parse_videos(f):
                yield video

    @staticmethod
    async def parse_videos(file_obj):
        """Парсинг массива videos"""
        parser = ijson.parse_async(file_obj)
        
        cur_video = None
        cur_snapshot = None

        is_in_snapshot = False
        
        async for prefix, event, value in parser:
            # начало видео
            if prefix == "videos.item" and event == "start_map":
                cur_video = {}
            # конец видео, выдать видео
            elif prefix == "videos.item" and event == "end_map":
                yield cur_video
            # добавить поля видео
            elif not is_in_snapshot and prefix.startswith("videos.item.") and event in ["boolean", "integer", "double", "number", "string"]:
                cur_video[prefix[prefix.rfind(".")+1:]] = value
            # начало массива снапшотов
            elif prefix == "videos.item.snapshots" and event == "start_array":
                cur_video["snapshots"] = []
            
            elif is_in_snapshot and event in ("integer", "number", "string"):
                cur_snapshot[prefix[prefix.rfind(".")+1:]] = value

            elif prefix == "videos.item.snapshots.item" and event == "start_map":
                is_in_snapshot = True
                cur_snapshot = {}
            # добавить снапшот в видео
            elif prefix == "videos.item.snapshots.item" and event == "end_map":
                cur_video["snapshots"].append(cur_snapshot)
                cur_snapshot = None
                is_in_snapshot = False

    @staticmethod
    async def stream_json_pydantic(file_path: str):
        import aiofiles
        import ijson
        
        async with aiofiles.open(file_path, 'rb') as f:
            videos = ijson.items_async(f, 'videos.item')
            
            async for video_data in videos:
                # Автоматическая десериализация в Pydantic объект
                video = Video(**video_data)
                yield video