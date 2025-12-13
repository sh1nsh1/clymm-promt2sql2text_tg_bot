from Utils.AsyncJSONParser import AsyncJSONParser
from datetime import datetime
import asyncpg
import os



class DataLoader:
    @staticmethod
    async def __get_connection():
        return await asyncpg.connect(
            os.getenv("DATABASE_URL")
        )
    
    @staticmethod

    async def truncate_db():
        conn = await DataLoader.__get_connection()
        await conn.execute('TRUNCATE TABLE video_snapshots CASCADE;')
        await conn.execute('TRUNCATE TABLE videos CASCADE;')
        await conn.close()

    @staticmethod
    async def init_db():
        conn = await DataLoader.__get_connection()
        
        await conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS videos (
                id UUID PRIMARY KEY,
                
                video_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                views_count INTEGER NOT NULL DEFAULT 0,
                likes_count INTEGER NOT NULL DEFAULT 0,
                reports_count INTEGER NOT NULL DEFAULT 0,
                comments_count INTEGER NOT NULL DEFAULT 0,
                
                creator_id VARCHAR(64) NOT NULL,
                
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            '''
        )
        await conn.execute(
            '''
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
                    ON DELETE CASCADE
            );
            '''
        )
        await conn.close()

    @staticmethod
    async def load_data(from_path:str):
        ...
        # async for video in AsyncJSONParser.parse_file(from_path):
        async for video in AsyncJSONParser.stream_json_pydantic(from_path):
            await DataLoader.__insert_video(video)
            await DataLoader.__insert_video_stapshots(video["snapshots"])

    @staticmethod
    async def fetch(sql):
        conn = await DataLoader.__get_connection()
        try:
            result = await conn.fetchrow(sql)
            return result
        except Exception as e:
            return f"PG error: {e}"
        finally:
            await conn.close()

    @staticmethod
    async def __insert_video(video):
        conn = await DataLoader.__get_connection()
        await conn.execute("""
            INSERT INTO videos (
                id, video_created_at, views_count, likes_count,
                reports_count, comments_count, creator_id,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO UPDATE SET
                video_created_at = EXCLUDED.video_created_at,
                views_count = EXCLUDED.views_count,
                likes_count = EXCLUDED.likes_count,
                reports_count = EXCLUDED.reports_count,
                comments_count = EXCLUDED.comments_count,
                creator_id = EXCLUDED.creator_id,
                updated_at = EXCLUDED.updated_at
        """,
        video['id'],
        datetime.fromisoformat(video['video_created_at'].replace('Z', '+00:00')),
        video['views_count'],
        video['likes_count'],
        video['reports_count'],
        video['comments_count'],
        video['creator_id'],
        datetime.fromisoformat(video['created_at'].replace('Z', '+00:00')),
        datetime.fromisoformat(video['updated_at'].replace('Z', '+00:00'))
        )
        await conn.close()    

    @staticmethod
    async def __insert_video_stapshots(snapshots):
        records = []
        for snap in snapshots:
            records.append((
                snap['id'],
                snap['video_id'],
                snap['views_count'],
                snap['likes_count'],
                snap['reports_count'],
                snap['comments_count'],
                snap['delta_views_count'],
                snap['delta_likes_count'],
                snap['delta_reports_count'],
                snap['delta_comments_count'],
                datetime.fromisoformat(snap['created_at'].replace('Z', '+00:00')),
                datetime.fromisoformat(snap['updated_at'].replace('Z', '+00:00'))
            ))
        conn = await DataLoader.__get_connection()
        await conn.copy_records_to_table(
            'video_snapshots',
            records=records,
            columns=[
                'id', 'video_id', 'views_count', 'likes_count',
                'reports_count', 'comments_count', 'delta_views_count',
                'delta_likes_count', 'delta_reports_count',
                'delta_comments_count', 'created_at', 'updated_at'
            ]
        )
        await conn.close()
    

    