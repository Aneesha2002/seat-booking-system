from pydantic import BaseModel

class SeatOut(BaseModel):
    id: int
    status: str
    locked_by: int | None


    class Config:
        orm_mode = True
