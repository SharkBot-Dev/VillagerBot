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
    ) -> list[app_commands.Choice[str]]:
        inv = await self.bot.item.get_inventory(interaction.user.id)
        items_cog = self.bot.get_cog("ItemsCog")
        
        if not items_cog or not inv:
            return []

        choices = []
        for item_id, count in inv.items():
            if "pickaxe" in item_id:
                item_info = items_cog.ITEMS.get(item_id)
                if not item_info:
                    continue
                
                name = item_info["name"]
                if current.lower() in name.lower():
                    choices.append(
                        app_commands.Choice(name=f"{name} (所持: {count})", value=item_id)
                    )
        
        return choices[:25]

    @app_commands.command(name="mine", description="鉱石を採掘します。")
    @app_commands.describe(ツルハシ="使用するツルハシを選択してください")
    @app_commands.autocomplete(ツルハシ=choice_pickaxe_autocomplete)
    async def mine_item(
        self,
        interaction: discord.Interaction,
        ツルハシ: str
    ):
        await interaction.response.defer()

        items_cog = self.bot.get_cog("ItemsCog")
        if not items_cog:
            return await interaction.followup.send("❌")

        item_info = items_cog.ITEMS.get(ツルハシ)
        if not item_info:
            return await interaction.followup.send("❌ 有効なツルハシを選択してください。")

        pickaxe_count = await self.bot.item.get_item_count(interaction.user.id, ツルハシ)
        if pickaxe_count < 1:
            return await interaction.followup.send(f"❌ {item_info['name']}を持っていません。")

        reward_id = None
        break_chance = 8

        if ツルハシ == "wooden_pickaxe":
            reward_id = random.choice(["stone", "dirt", "coal"])
        elif ツルハシ == "stone_pickaxe":
            reward_id = random.choice(["stone", "stone", "stone", "dirt", "iron_ore", "coal", "coal"]) 

        if not reward_id:
            return await interaction.followup.send("❌ この道具では何も採掘できません。")

        reward_info = items_cog.ITEMS.get(reward_id)
        reward_name = reward_info["name"] if reward_info else "不明な物体"

        await self.bot.item.add_item(interaction.user.id, reward_id, 1)

        text = f"⛏️ **{reward_name}** を採掘しました！"

        if random.randint(1, break_chance) == 1:
            await self.bot.item.add_item(interaction.user.id, ツルハシ, -1)
            text += f"\n❗ **{item_info['name']}** が壊れてしまいました..."

        await interaction.followup.send(content=text)

async def setup(bot):
    await bot.add_cog(MineCog(bot))