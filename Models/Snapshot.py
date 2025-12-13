from typing import Any
from pydantic import BaseModel

class Snapshot(BaseModel):
    id: str
    video_id: str
    views_count: int
    likes_count: int
    reports_count: int
    comments_count: int
    delta_views_count: int
    delta_likes_count: int
    delta_reports_count: int
    delta_comments_count: int
    created_at: str
    updated_at: str

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found")