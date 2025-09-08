from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from src.database.db import Base

class AutomatonTable(Base):
    __tablename__ = "automaton_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    data = Column(LargeBinary, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    frames = Column(Integer, nullable=False)
    modified_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<AutomatonTable(name={self.name!r} w={self.width} h={self.height} f={self.frames})>"
    
