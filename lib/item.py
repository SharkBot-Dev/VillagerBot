from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

class Item:
    def __init__(self, bot: commands.Bot, db: AsyncIOMotorClient):
        self.db = db
        self.bot = bot

        self.collection = self.db["VillagerBot"].Player

    def get_item_info(self, item_id: str) -> dict:
        items_cog = self.bot.get_cog("ItemsCog")
        if not items_cog:
            return {}
        return items_cog.ITEMS.get(item_id, {})
    
    def get_item_info_for_name(self, item_name: str) -> dict:
        items_cog = self.bot.get_cog("ItemsCog")
        if not items_cog or not hasattr(items_cog, 'ITEMS'):
            return {}

        for info in items_cog.ITEMS.values():
            if info.get('name') == item_name:
                return info
        return {}

    async def add_item(self, user_id: int, item_id: str, count: int):
        if not self.get_item_info(item_id):
            return

        await self.collection.update_one(
            {"user_id": user_id},
            {"$inc": {f"inventory.{item_id}": count}},
            upsert=True 
        )

        user_data = await self.collection.find_one({"user_id": user_id}, {f"inventory.{item_id}": 1})
        if user_data:
            current_count = user_data.get("inventory", {}).get(item_id, 0)
            if current_count <= 0:
                await self.collection.update_one(
                    {"user_id": user_id},
                    {"$unset": {f"inventory.{item_id}": ""}}
                )

    async def get_inventory(self, user_id: int) -> dict:
        user_data = await self.collection.find_one(
            {"user_id": user_id},
            {"inventory": 1, "_id": 0} 
        )
        
        if not user_data or "inventory" not in user_data:
            return {} 
            
        return user_data["inventory"]
    
    async def get_item_count(self, user_id: int, item_id: str) -> int:
        user_data = await self.collection.find_one(
            {"user_id": user_id},
            {f"inventory.{item_id}": 1, "_id": 0}
        )

        if not user_data or "inventory" not in user_data:
            return 0
        
        return user_data["inventory"].get(item_id, 0)