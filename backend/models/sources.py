from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, HttpUrl


class SourceDTO(BaseModel):
    source: HttpUrl


class Source(BaseModel):
    id: int
    slug: str
    source: str
    image_count: int = 0


def slug_from_source(source: str) -> str:
    path = urlparse(source).path.rstrip('/')
    return Path(path).name or source


def parse_source(raw: str) -> dict:
    value = raw.strip()
    if not value:
        raise ValueError('fonte vazia')
    if not value.startswith(('http://', 'https://')):
        raise ValueError('fonte deve ser URL http(s)')

    return {
        'slug': slug_from_source(value),
        'kind': 'pinterest',
        'source': value,
    }
