from sqlalchemy import Column, DateTime, Integer, String, func

from database import Base


class ScreenAliasesORM(Base):
    __tablename__ = 'screen_aliases'

    id = Column(Integer, primary_key = True, index = True)
    screen_id = Column(Integer, unique = True, nullable = False, index = True)
    alias = Column(String(128), nullable = False)
    updated_at = Column(DateTime, server_default = func.now(), onupdate = func.now())
