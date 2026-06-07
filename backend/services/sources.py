from pathlib import Path

from env import CACHE_DIR, IMAGE_EXTENSIONS
from services.cache import cache_dir


def _is_favorite(slug: str, filename: str) -> bool:
    from services.favorites import is_favorited

    return is_favorited(slug, filename)


def list_images(slug: str) -> list[dict]:
    folder = cache_dir(slug)
    if not folder.is_dir():
        return []

    images: list[dict] = []
    for entry in sorted(folder.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        stat = entry.stat()
        images.append(
            {
                'name': entry.name,
                'slug': slug,
                'size_bytes': stat.st_size,
                'url': f'/api/images/{slug}/{entry.name}',
                'favorite': _is_favorite(slug, entry.name),
            }
        )
    return images


def resolve_image_path(slug: str, filename: str) -> Path:
    folder = (CACHE_DIR / slug).resolve()
    image = (folder / filename).resolve()
    if folder not in image.parents:
        raise ValueError('invalid path')
    if not image.is_file():
        raise FileNotFoundError(filename)
    if image.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError('unsupported file type')
    return image
