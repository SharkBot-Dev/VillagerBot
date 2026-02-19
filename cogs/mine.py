import random
import discord
from discord.ext import commands
from discord import app_commands
from bot import VillagerBot

class MineCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot

    async def choice_pickaxe_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ):
        count = await self.bot.item.get_item_count(interaction.user.id, "wooden_pickaxe")
        
        if count <= 0:
            return []

        choices = [
            app_commands.Choice(name=f"木のつるはし (所持: {count})", value="wooden_pickaxe")
        ]
        return [c for c in choices if current.lower() in c.name.lower()][:25]

    @app_commands.command(name="mine", description="鉱石を採掘します。")
    @app_commands.autocomplete(ツルハシ=choice_pickaxe_autocomplete)
    async def mine_item(
        self,
        interaction: discord.Interaction,
        ツルハシ: str
    ):
        await interaction.response.defer()

        items_cog = self.bot.get_cog("ItemsCog")
        item_info = items_cog.ITEMS.get(ツルハシ)

        if not item_info:
            return await interaction.followup.send(content="❌ 有効なツルハシを選択してください。")

        pickaxe_count = await self.bot.item.get_item_count(interaction.user.id, ツルハシ)
        if pickaxe_count < 1:
            return await interaction.followup.send(content=f"❌ {item_info['name']}を持っていません。")

        if ツルハシ == "wooden_pickaxe":
            reward_id = random.choice(["stone", "dirt"])
            reward_name = self.bot.item.get_item_info(reward_id)

            await self.bot.item.add_item(interaction.user.id, reward_id, 1)

            text = f"⛏️ **{reward_name["name"]}** を採掘しました！"

            if random.randint(1, 8) == 8:
                await self.bot.item.add_item(interaction.user.id, ツルハシ, -1)
                text += f"\n❗ {item_info['name']} が壊れてしまいました..."

            await interaction.followup.send(content=text)

async def setup(bot):
    await bot.add_cog(MineCog(bot))