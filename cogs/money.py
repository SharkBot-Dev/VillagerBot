import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from bot import VillagerBot

class MoneyCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot

    @app_commands.command(name="balance", description="所持しているエメラルドを確認します。")
    @app_commands.describe(ユーザー="確認したいユーザー（省略すると自分の所持金を表示します）")
    async def balance(
        self,
        interaction: discord.Interaction,
        ユーザー: Optional[discord.User] = None
    ):
        await interaction.response.defer()

        target = ユーザー or interaction.user
        
        coin = await self.bot.money.get_money(target.id)

        name = "あなた" if target == interaction.user else f"{target.display_name} さん"
        await interaction.followup.send(content=f"💰 **{name}の所持金:** {coin} エメラルド")

async def setup(bot):
    await bot.add_cog(MoneyCog(bot))