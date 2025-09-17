from pydantic import BaseModel


class Skin(BaseModel):

    id: int
    skin_id: str
    skin_geometry: str
    skin_height: int
    skin_width: int