from pydantic import BaseModel


class Skin(BaseModel):

    id: int
    skinId: str
    geometry: str
    height: int
    width: int