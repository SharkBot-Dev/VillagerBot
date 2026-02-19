import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot import VillagerBot

class ItemsCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot
        self.ITEMS = {
            "stone": {
                "name": "石",
                "price": 0.01,
                "id": "stone"
            },
            "dirt": {
                "name": "土",
                "price": 0.001,
                "id": "dirt"
            },
            "wooden_pickaxe": {
                "name": "木のツルハシ",
                "price": 0.5,
                "id": "wooden_pickaxe"
            }
        }

    item = app_commands.Group(
        name="item",
        description="アイテムのコマンドです。"
    )

    @item.command(name="list", description="アイテムリストを表示します。")
    async def item_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        inv = await self.bot.item.get_inventory(interaction.user.id)

        if not inv:
            await interaction.followup.send("❌持ち物は空っぽです。")
        else:
            msg = "\n".join([f"{self.ITEMS.get(item_id, {}).get('name', '不明')}: {count}個 ({self.ITEMS.get(item_id, {}).get('price', '0')}エメラルド)" for item_id, count in inv.items()])
            await interaction.followup.send(f"**あなたの持ち物:**\n{msg}")

async def setup(bot):
    await bot.add_cog(ItemsCog(bot))