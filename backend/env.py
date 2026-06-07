from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

BACKEND_DIR = Path(__file__).parent
STORAGE_DIR = Path(getenv('STORAGE_DIR', BACKEND_DIR / 'storage'))
DATA_DIR = Path(getenv('DATA_DIR', BACKEND_DIR / 'data'))
CACHE_DIR = Path(getenv('CACHE_DIR', STORAGE_DIR / 'cache'))
FAVORITES_DIR = Path(getenv('FAVORITES_DIR', STORAGE_DIR / 'favorites'))
APPLIED_DIR = Path(getenv('APPLIED_DIR', DATA_DIR / 'applied'))

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
GALLERY_DL_BROWSER = getenv('GALLERY_DL_BROWSER', 'vivaldi')

CORS_ORIGINS = [
    origin.strip()
    for origin in getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    if origin.strip()
]

def _async_database_url() -> str:
    url = getenv('DATABASE_URL')
    if url:
        if url.startswith('sqlite:///'):
            return url.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)
        return url

    db_path = (DATA_DIR / 'sources.db').resolve()
    return f'sqlite+aiosqlite:///{db_path}'


DATABASE_URL = _async_database_url()
