import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
import dotenv
import os

from lib import item, money, daily

dotenv.load_dotenv()

class VillagerBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()

        super().__init__(
            help_command=None,
            intents=intents,
            command_prefix="!"
        )
        
        self.async_db = AsyncIOMotorClient("mongodb://localhost:27017")

        self.item = item.Item(self, self.async_db)
        self.money = money.Money(self, self.async_db)
        self.daily = daily.Daily(self, self.async_db)

    async def setup_hook(self) -> None:
        await self.load_cogs()
        try:
            await self.tree.sync()
            print("スラッシュコマンドを同期しました。")
        except Exception as e:
            print(f"スラッシュコマンドの同期に失敗しました。: {e}")

    async def load_cogs(self, base_folder="cogs"):
        for root, dirs, files in os.walk(base_folder):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    relative_path = os.path.relpath(os.path.join(root, file), base_folder)
                    module = f"{base_folder}." + relative_path.replace(os.sep, ".")[:-3]
                    try:
                        await self.load_extension(module)
                        print(f"Loaded {module}")
                    except Exception as e:
                        print(f"Failed to load {module}: {e}")

    async def on_ready(self):
        print(f"--- InitDone ---")
        print(f"Logged in as {self.user} (ID: {self.user.id})")

if __name__ == "__main__":
    bot = VillagerBot()
    bot.run(os.environ.get('TOKEN'))