from pydantic import BaseModel


class ApplyDTO(BaseModel):
    screen_id: int
    slug: str
    filename: str
    from_favorites: bool = False
