import random
import discord
from discord.ext import commands
from discord import app_commands
from bot import VillagerBot

class FurnaceCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot
        self.FURNACE_MAP = {
            "iron_ore": "iron_ingot"
        }
        self.FUEL_LIST = ["coal"]
        self.MATERIAL_LIST = ["iron_ore"]

    async def choice_fuel_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        inv = await self.bot.item.get_inventory(interaction.user.id)
        items_cog = self.bot.get_cog("ItemsCog")
        
        if not items_cog or not inv:
            return []

        choices = []
        for item_id, count in inv.items():
            if item_id in self.FUEL_LIST:
                item_info = items_cog.ITEMS.get(item_id)
                if not item_info:
                    continue
                
                name = item_info["name"]
                if current.lower() in name.lower():
                    choices.append(
                        app_commands.Choice(name=f"{name} (所持: {count})", value=item_id)
                    )
        
        return choices[:25]
    
    async def choice_material_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        inv = await self.bot.item.get_inventory(interaction.user.id)
        items_cog = self.bot.get_cog("ItemsCog")
        
        if not items_cog or not inv:
            return []

        choices = []
        for item_id, count in inv.items():
            if item_id in self.MATERIAL_LIST:
                item_info = items_cog.ITEMS.get(item_id)
                if not item_info:
                    continue
                
                name = item_info["name"]
                if current.lower() in name.lower():
                    choices.append(
                        app_commands.Choice(name=f"{name} (所持: {count})", value=item_id)
                    )
        
        return choices[:25]

    @app_commands.command(name="furnace", description="かまどを使用します。")
    @app_commands.describe(燃料="使用する燃料を選択してください", 材料="使用する材料を選択してください")
    @app_commands.autocomplete(燃料=choice_fuel_autocomplete, 材料=choice_material_autocomplete)
    async def mine_item(
        self,
        interaction: discord.Interaction,
        材料: str,
        燃料: str
    ):
        await interaction.response.defer()

        items_cog = self.bot.get_cog("ItemsCog")
        if not items_cog:
            return await interaction.followup.send("❌")

        fuel_item_info = items_cog.ITEMS.get(燃料)
        if not fuel_item_info:
            return await interaction.followup.send("❌ 有効な燃料を選択してください。")

        fuel_count = await self.bot.item.get_item_count(interaction.user.id, 燃料)
        if fuel_count < 1:
            return await interaction.followup.send(f"❌ {fuel_item_info['name']}を持っていません。")

        material_item_info = items_cog.ITEMS.get(材料)
        if not material_item_info:
            return await interaction.followup.send("❌ 有効な材料を選択してください。")

        material_count = await self.bot.item.get_item_count(interaction.user.id, 材料)
        if material_count < 1:
            return await interaction.followup.send(f"❌ {material_item_info['name']}を持っていません。")

        item = self.FURNACE_MAP.get(材料)

        item_info = self.bot.item.get_item_info(item)

        await self.bot.item.add_item(interaction.user.id, item, 1)
        await self.bot.item.add_item(interaction.user.id, 燃料, -1)
        await self.bot.item.add_item(interaction.user.id, 材料, -1)

        text = f"🔥{item_info.get('name')}を入手しました。\n❗燃料を一個消費しました。"

        await interaction.followup.send(content=text)

async def setup(bot):
    await bot.add_cog(FurnaceCog(bot))