import random
import discord
from discord.ext import commands
from discord import app_commands
from bot import VillagerBot

class FishCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot

    @app_commands.command(name="fish", description="魚を釣ります。")
    async def fish_item(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()

        items_cog = self.bot.get_cog("ItemsCog")
        if not items_cog:
            return await interaction.followup.send("❌")

        pickaxe_count = await self.bot.item.get_item_count(interaction.user.id, "fishing_rod")
        if pickaxe_count < 1:
            return await interaction.followup.send(f"❌ 釣り竿を持っていません。")

        reward_id = None
        break_chance = 8

        reward_id = random.choice(["tropical_fish", "salmon"])

        if not reward_id:
            return await interaction.followup.send("❌ この道具では何も採掘できません。")

        reward_info = items_cog.ITEMS.get(reward_id)
        reward_name = reward_info["name"] if reward_info else "不明な物体"

        await self.bot.item.add_item(interaction.user.id, reward_id, 1)

        text = f"🎣 **{reward_name}** を釣りました！"

        if random.randint(1, break_chance) == 1:
            await self.bot.item.add_item(interaction.user.id, "fishing_rod", -1)
            text += f"\n❗ *釣竿** が壊れてしまいました..."

        await interaction.followup.send(content=text)

async def setup(bot):
    await bot.add_cog(FishCog(bot))