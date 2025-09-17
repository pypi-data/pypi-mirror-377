from pydantic import BaseModel


class UserShort(BaseModel):
    id: int
    name: str
    xbox: str
    telegram_id: int
    is_activated: bool
    is_banned: bool
    is_premium: bool