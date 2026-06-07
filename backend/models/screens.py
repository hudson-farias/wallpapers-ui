import re

from pydantic import BaseModel, field_validator

_ALIAS_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9 _.-]{0,63}$')


class ScreenAliasDTO(BaseModel):
    alias: str

    @field_validator('alias')
    @classmethod
    def validate_alias(cls, value: str) -> str:
        alias = value.strip()
        if not alias:
            return ''
        if not _ALIAS_RE.match(alias):
            raise ValueError('alias inválido (use letras, números, espaço, -, _ e .)')
        return alias
