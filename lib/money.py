from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

class Money:
    def __init__(self, bot: commands.Bot, db: AsyncIOMotorClient):
        self.db = db
        self.bot = bot

    async def get_money(self, user_id: int):
        db = self.db["VillagerBot"].Player

        user_data = await db.find_one(
            {"user_id": user_id}
        )
        
        if not user_data or "money" not in user_data:
            return 0
            
        return user_data["money"]
    
    async def add_money(self, user_id: int, count: int):
        db = self.db["VillagerBot"].Player
        
        await db.update_one(
            {"user_id": user_id},
            {"$inc": {
                "money": count
            }},
            upsert=True 
        )