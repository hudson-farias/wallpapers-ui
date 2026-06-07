from contextlib import asynccontextmanager
from importlib import import_module
from os import walk
from os.path import join
from pathlib import Path
import shutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import Base, engine
from database.screens import ScreenAliasesORM  # noqa: F401
from database.sources import SourcesORM  # noqa: F401
from env import BACKEND_DIR, CACHE_DIR, CORS_ORIGINS, DATA_DIR, FAVORITES_DIR, STORAGE_DIR


def _merge_dir(source: Path, dest: Path) -> None:
    dest.mkdir(parents = True, exist_ok = True)
    for entry in source.iterdir():
        target = dest / entry.name
        if entry.is_dir():
            _merge_dir(entry, target)
            shutil.rmtree(entry, ignore_errors = True)
        elif not target.exists():
            shutil.move(str(entry), str(target))


def _migrate_storage_dir(old: Path, new: Path) -> None:
    if not old.is_dir():
        return
    if old.resolve() == new.resolve():
        return

    new.parent.mkdir(parents = True, exist_ok = True)
    if not new.exists():
        old.rename(new)
        return

    _merge_dir(old, new)
    shutil.rmtree(old, ignore_errors = True)


def _migrate_storage_paths() -> None:
    _migrate_storage_dir(DATA_DIR / 'cache', CACHE_DIR)
    _migrate_storage_dir(BACKEND_DIR / 'cache', CACHE_DIR)
    _migrate_storage_dir(BACKEND_DIR / 'favorites', FAVORITES_DIR)
    _migrate_storage_dir(BACKEND_DIR.parent / 'storage', STORAGE_DIR)


def _migrate_screen_aliases_table(connection) -> None:
    legacy = connection.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name='monitor_aliases'")
    ).fetchone()
    if legacy is None:
        return

    connection.execute(
        text(
            'INSERT OR IGNORE INTO screen_aliases (screen_id, alias) '
            'SELECT monitor_id, alias FROM monitor_aliases'
        )
    )
    connection.execute(text('DROP TABLE monitor_aliases'))


@asynccontextmanager
async def lifespan(_: FastAPI):
    DATA_DIR.mkdir(parents = True, exist_ok = True)
    STORAGE_DIR.mkdir(parents = True, exist_ok = True)
    _migrate_storage_paths()
    CACHE_DIR.mkdir(parents = True, exist_ok = True)
    FAVORITES_DIR.mkdir(parents = True, exist_ok = True)
    (BACKEND_DIR / '.tmp-sync').mkdir(parents = True, exist_ok = True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_screen_aliases_table)
    yield


app = FastAPI(title = 'wallpaper-ui', version = '0.1.0', lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = CORS_ORIGINS,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)


def load(subapp: FastAPI, directory: str = 'routers'):
    import_cache = {}

    for root, _, files in walk(directory):
        for file in files:
            if not file.startswith('__') and file.endswith('.py'):
                path = join(root, file).replace('.py', '').replace('/', '.').replace('\\', '.')

                if path not in import_cache:
                    import_cache[path] = import_module(path)

    included_routers = set()

    for module in import_cache.values():
        router_id = id(module.router)

        if router_id in included_routers:
            continue

        included_routers.add(router_id)
        subapp.include_router(module.router)

    del import_cache


load(app)
