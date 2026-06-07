import asyncio
import shutil
import subprocess
from pathlib import Path

from env import BACKEND_DIR, CACHE_DIR, GALLERY_DL_BROWSER, IMAGE_EXTENSIONS


def cache_dir(slug: str) -> Path:
    return CACHE_DIR / slug


def cache_has_images(slug: str) -> bool:
    folder = cache_dir(slug)
    if not folder.is_dir():
        return False
    return any(
        entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS
        for entry in folder.iterdir()
    )


def remove_cache(slug: str) -> None:
    shutil.rmtree(cache_dir(slug), ignore_errors = True)


def _sync_from_url(slug: str, url: str) -> Path:
    if not shutil.which('gallery-dl'):
        raise RuntimeError('gallery-dl não encontrado — instale no venv ou no sistema')

    tmp_base = BACKEND_DIR / '.tmp-sync'
    tmp = tmp_base / slug
    dest = cache_dir(slug)

    shutil.rmtree(tmp, ignore_errors = True)
    tmp.mkdir(parents = True, exist_ok = True)

    image_ext = ', '.join(repr(ext.lstrip('.')) for ext in sorted(IMAGE_EXTENSIONS))

    cmd = ['gallery-dl', '-o', 'pinterest.videos=false', '--filter', f'extension in ({image_ext})']
    if GALLERY_DL_BROWSER and shutil.which(GALLERY_DL_BROWSER):
        cmd.extend(['--cookies-from-browser', GALLERY_DL_BROWSER])
    cmd.extend(['-D', str(tmp), '-f', f'{slug}-{{id}}.{{extension}}', url])

    proc = subprocess.run(cmd, capture_output = True, text = True)
    if proc.returncode != 0:
        shutil.rmtree(tmp, ignore_errors = True)
        detail = (proc.stderr or proc.stdout or 'gallery-dl falhou').strip()
        raise RuntimeError(detail)

    shutil.rmtree(dest, ignore_errors = True)
    CACHE_DIR.mkdir(parents = True, exist_ok = True)
    tmp.rename(dest)
    shutil.rmtree(tmp_base, ignore_errors = True)
    return dest


async def ensure_cache(slug: str, url: str, *, refresh: bool = False) -> Path:
    if not refresh and cache_has_images(slug):
        return cache_dir(slug)
    return await asyncio.to_thread(_sync_from_url, slug, url)
