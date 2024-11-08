from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str
    category: str
    condition: str


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    condition: str
    is_available: bool

    class Config:
        orm_mode = True
