import re

from pydantic import BaseModel, field_validator

_SLUG_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$')


class FavoriteDTO(BaseModel):
    slug: str
    filename: str

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, value: str) -> str:
        name = value.strip()
        if not _SLUG_RE.match(name):
            raise ValueError('slug inválido')
        return name
