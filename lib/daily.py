from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

class Daily:
    def __init__(self, bot: commands.Bot, db: AsyncIOMotorClient):
        self.db = db
        self.bot = bot
        self.collection = self.db["VillagerBot"].Player

    async def check_and_claim(self, user_id: int):
        now = datetime.utcnow()
        user_data = await self.collection.find_one({"user_id": user_id}, {"last_daily": 1})

        if user_data and "last_daily" in user_data:
            last_daily = user_data["last_daily"]
            if now < last_daily + timedelta(hours=24):
                next_claim = last_daily + timedelta(hours=24)
                return False, next_claim

        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_daily": now}},
            upsert=True
        )
        return True, now