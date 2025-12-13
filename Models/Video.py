from Models import Snapshot
from typing import Any, List
from pydantic import BaseModel

class Video(BaseModel):
    id: str
    video_created_at: str
    views_count: int
    likes_count: int
    reports_count: int
    comments_count: int
    creator_id: str
    created_at: str
    updated_at: str
    snapshots: List["Snapshot"] = []

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found")