## Перед запуском небоходимо в корневой директории создать файл .env следующиего содержания:
```
DEEPSEEK_API_KEY=<api key полученный у DeepSeek>
DATABASE_URL=postgresql://user:password@db:5432/mydatabase
BOT_TOKEN=<токен телеграм бота>
```


## Для запуска нужно перейти в корневую директорию репозитория и запустить:
```
docker-compose up
```

После поднятия контейнера последовательно выполняется:
- инициализация таблиц БД
- очистка таблиц (актуально для повторных запусков)
- заполнение таблиц данными, полученными из json-файла (был для удобства помещён в корневую директорию)
- запуск бота.

## Описание работы 
Бот отвечает на команду /start и на любое другое текстовое сообщение. Это сообщение передётся как часть промта в LLM DeepSeek. 
LLM, обработав промт, возвращает sql-запрос, который очищается от Markdown и далее выполняется в БД. Результат выполнения запроса Бот возвращает пользователю в виде сообщения.

## Шаблон промта
role: system  
content:  
```
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
```
role: user  
content: <Введёный в чат Бота текст>

Если LLM не поймёт сообщения, Бот в качестве ответа отправит id первого попавшегося видео
