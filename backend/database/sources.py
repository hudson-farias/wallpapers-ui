from sqlalchemy import Column, DateTime, Integer, String, func

from database import Base


class SourcesORM(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key = True, index = True)
    slug = Column(String(255), unique = True, nullable = False, index = True)
    kind = Column(String(32), nullable = False)
    source = Column(String(2048), unique = True, nullable = False)
    created_at = Column(DateTime, server_default = func.now())
