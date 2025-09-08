from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AutomatonEntryCreate(BaseModel):
    name: str
    width: int
    height: int
    frames: int
    cells: bytes

class AutomatonEntry(BaseModel):
    id: int
    name: str
    width: int
    height: int
    frames: int
    modified_at: datetime
    cells: Optional[bytes] = None

    class Config:
        orm_mode = True