from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from aioallay.types.BankCard import BankCard
from aioallay.types.CityOrder import CityOrder
from aioallay.types.GameProfile import GameProfile
from aioallay.types.Skin import Skin


class User(BaseModel):
    id: int
    rate: float
    name: str
    age: int
    sex: str
    bio: Optional[str]
    country: str
    username: str
    create_at: datetime
    telegram_id: int
    is_activated: bool
    is_banned: bool
    city_region: Optional[str]
    is_bot: bool
    is_premium: bool
    city_weather: Optional[str]
    birthday_at: Optional[datetime]
    game_profiles: List[GameProfile]
    bank_cards: List[BankCard]
    city_orders: List[CityOrder]

    def get_gp(self, xbox: str) -> GameProfile:
        for game_profile in self.game_profiles:
            if game_profile.xbox == xbox:
                return game_profile

#todo
  #  async def update_rate(self, rate: int):
       # new_user: User = await httpClient.update_user_rate(self.id, rate)
        #self.rate = new_user.rate


