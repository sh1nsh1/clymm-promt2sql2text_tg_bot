import os
from typing import Dict, Any
import aiohttp
import asyncio

class __DeepSeekClient:
    system_message = """
Ты получаешь некоторый запрос на русском языке в свободной форме.
А возвращаешь голый sql-запрос, отвечайющий требованиям запроса, и без Markdown-форматирования.

В базе данных две следующие таблицы:
    CREATE TABLE IF NOT EXISTS videos (
        id UUID PRIMARY KEY,
        
        video_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
        views_count INTEGER NOT NULL DEFAULT 0,
        likes_count INTEGER NOT NULL DEFAULT 0,
        reports_count INTEGER NOT NULL DEFAULT 0,
        comments_count INTEGER NOT NULL DEFAULT 0,
        
        creator_id VARCHAR(64) NOT NULL,
        
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    )
    CREATE TABLE IF NOT EXISTS video_snapshots (
        id VARCHAR(64) PRIMARY KEY,
        
        video_id UUID NOT NULL,
        
        views_count INTEGER NOT NULL DEFAULT 0,
        likes_count INTEGER NOT NULL DEFAULT 0,
        reports_count INTEGER NOT NULL DEFAULT 0,
        comments_count INTEGER NOT NULL DEFAULT 0,
        
        delta_views_count INTEGER NOT NULL DEFAULT 0,
        delta_likes_count INTEGER NOT NULL DEFAULT 0,
        delta_reports_count INTEGER NOT NULL DEFAULT 0,
        delta_comments_count INTEGER NOT NULL DEFAULT 0,
        
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT fk_video_snapshots_video 
            FOREIGN KEY (video_id) 
            REFERENCES videos(id) 
            ON DELETE CASCADE,
    );

Если запрос пользователя не относится к базе данных или из него невозможно составить sql-запрос, верни следующи запрос:
    select -1;
"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.timeout = aiohttp.ClientTimeout(total=None)
        
        if not self.api_key:
            print("⚠️ ВНИМАНИЕ: API ключ не найден!")
            print("Добавьте DEEPSEEK_API_KEY в .env файл или передайте через аргументы")
    
    async def send_request(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        system_message: str = system_message,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "success": False,
                "error": "API ключ не настроен"
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=data
                ) as response:
                    
                    if response.status == 200:
                        if stream:
                            return await self._handle_stream_response(response)
                        else:
                            result = await response.json()
                            return self._parse_response(result)
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
            except aiohttp.ClientError as e:
                return {
                    "success": False,
                    "error": f"Ошибка сети: {str(e)}"
                }
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": "Таймаут запроса"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Неизвестная ошибка: {str(e)}"
                }

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if "choices" in data and data["choices"]:
                response_text = data["choices"][0]["message"]["content"]
                
                result = {
                    "success": True,
                    "response": response_text,
                    "model": data.get("model", "unknown"),
                    "usage": data.get("usage", {}),
                    "created": data.get("created"),
                    "id": data.get("id")
                }
                
                if "usage" in data:
                    result["tokens"] = {
                        "prompt": data["usage"].get("prompt_tokens", 0),
                        "completion": data["usage"].get("completion_tokens", 0),
                        "total": data["usage"].get("total_tokens", 0)
                    }
                
                return result
            else:
                return {
                    "success": False,
                    "error": "Некорректный ответ от API",
                    "raw_data": data
                }
                
        except KeyError as e:
            return {
                "success": False,
                "error": f"Ошибка парсинга ответа: {str(e)}",
                "raw_data": data
            }



async def get_sql_from_prompt(prompt):
    api_key = dict(os.environ)["DEEPSEEK_API_KEY"]
    client = __DeepSeekClient(api_key)
    result = await client.send_request(
                prompt=prompt,
                model="deepseek-chat"
            )
    if result["success"]:
        return result["response"].replace("```", "-- ```")
    else:
        print(f"Ошибка: {result['error']}")



