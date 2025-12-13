from .Snapshot import Snapshot
from .Video import Video

# Rebuild моделей для разрешения forward references
Video.model_rebuild()

# Экспортируем
__all__ = ['Snapshot', 'Video']