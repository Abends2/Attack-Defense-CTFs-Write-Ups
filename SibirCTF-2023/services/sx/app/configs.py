import os
from pathlib import Path


DATABASE_FILE = Path(os.getenv("DATABASE_FILE", "sqlite.db"))

RESPONSE_ITEMS_LIMIT = 100

AVATARS_DIR = Path(os.getenv("AVATARS_DIR", "avatars"))
if not AVATARS_DIR.is_dir():
    AVATARS_DIR.mkdir(parents=True)

MAX_AVATAR_SIZE = 50000
