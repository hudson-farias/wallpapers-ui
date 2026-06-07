import re
import shutil
from pathlib import Path

from env import FAVORITES_DIR, IMAGE_EXTENSIONS

_SLUG_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$')
LEGACY_STORED_SEP = '__'
LEGACY_USER_FOLDERS = {'geral'}


def validate_slug(name: str) -> str:
    name = name.strip()
    if not _SLUG_RE.match(name):
        raise ValueError('slug inválido')
    return name


def slug_dir(source_slug: str) -> Path:
    return FAVORITES_DIR / validate_slug(source_slug)


def favorite_file_path(source_slug: str, filename: str) -> Path:
    return slug_dir(source_slug) / filename


def is_favorited(source_slug: str, filename: str) -> bool:
    return favorite_file_path(source_slug, filename).is_file()


def list_slugs() -> list[dict]:
    FAVORITES_DIR.mkdir(parents = True, exist_ok = True)
    slugs: list[dict] = []

    for entry in sorted(FAVORITES_DIR.iterdir()):
        if not entry.is_dir():
            continue
        count = _count_slug_images(entry)
        if count == 0:
            continue
        slugs.append({'name': entry.name, 'image_count': count})

    return slugs


def _count_slug_images(slug_path: Path) -> int:
    return sum(
        1
        for entry in slug_path.iterdir()
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS
    )


def list_slug_images(source_slug: str) -> list[dict]:
    path = slug_dir(source_slug)
    if not path.is_dir():
        return []

    slug = validate_slug(source_slug)
    images: list[dict] = []

    for entry in sorted(path.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        stat = entry.stat()
        images.append(
            {
                'name': entry.name,
                'filename': entry.name,
                'slug': slug,
                'size_bytes': stat.st_size,
                'url': f'/api/favorites/images/{slug}/{entry.name}',
                'favorite': True,
            }
        )

    return images


def list_all_images() -> list[dict]:
    images: list[dict] = []
    for slug in list_slugs():
        images.extend(list_slug_images(slug['name']))
    return images


def add_favorite(source_slug: str, filename: str) -> Path:
    from services import sources as sources_service

    slug = validate_slug(source_slug)
    src = sources_service.resolve_image_path(slug, filename)
    dest = favorite_file_path(slug, filename)
    dest.parent.mkdir(parents = True, exist_ok = True)
    shutil.copy2(src, dest)
    return dest


def remove_favorite(source_slug: str, filename: str) -> None:
    path = favorite_file_path(source_slug, filename)
    if not path.is_file():
        raise FileNotFoundError(filename)
    path.unlink()
    _prune_empty_parents(path.parent)


def resolve_favorite_path(source_slug: str, filename: str) -> Path:
    favorites_root = FAVORITES_DIR.resolve()
    image = favorite_file_path(source_slug, filename).resolve()
    if favorites_root not in image.parents:
        raise ValueError('invalid path')
    if not image.is_file():
        raise FileNotFoundError(filename)
    if image.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError('unsupported file type')
    return image


def favorite_count() -> int:
    return len(list_all_images())


def _prune_empty_parents(path: Path) -> None:
    favorites_root = FAVORITES_DIR.resolve()
    current = path.resolve()

    while favorites_root in current.parents and current != favorites_root:
        if any(current.iterdir()):
            break
        current.rmdir()
        current = current.parent


def _parse_legacy_stored_name(stored: str) -> tuple[str, str]:
    if LEGACY_STORED_SEP not in stored:
        return stored, stored
    source_slug, filename = stored.split(LEGACY_STORED_SEP, 1)
    return source_slug, filename


def _move_to_slug(source_slug: str, file_path: Path) -> None:
    target = favorite_file_path(source_slug, file_path.name)
    target.parent.mkdir(parents = True, exist_ok = True)
    if target.exists():
        return
    shutil.copy2(file_path, target)


def _is_current_slug_dir(entry: Path) -> bool:
    if not entry.is_dir():
        return False
    children = list(entry.iterdir())
    if not children:
        return False
    return all(
        child.is_file() and child.suffix.lower() in IMAGE_EXTENSIONS
        for child in children
    )
