from datetime import datetime
import random

import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot import VillagerBot

class DailyCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot

    @app_commands.command(name="daily", description="毎日ログインに参加します。")
    async def daily_get(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()

        can_claim, result = await self.bot.daily.check_and_claim(interaction.user.id)

        if not can_claim:
            wait_time = result - datetime.utcnow()
            hours, remainder = divmod(int(wait_time.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            return await interaction.followup.send(
                f"❌ あと **{hours}時間{minutes}分** お待ちください。"
            )

        money = random.randint(1, 3)

        await self.bot.money.add_money(interaction.user.id, money)
        await self.bot.item.add_item(interaction.user.id, "wooden_pickaxe", 1)

        await interaction.followup.send(f"✅ ログインしました。\n✅ {money}エメラルドを入手しました。\n✅ 木のツルハシを入手しました。")

async def setup(bot):
    await bot.add_cog(DailyCog(bot))