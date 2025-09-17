from pydantic import BaseModel, Field

class Skin(BaseModel):
    id: int
    skin_id: str = Field(alias="skinId")
    skin_geometry: str = Field(alias="geometry")
    skin_height: int = Field(alias="height")
    skin_width: int = Field(alias="width")
