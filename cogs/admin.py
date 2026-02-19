from datetime import datetime
import random

import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot import VillagerBot

class AdminCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot
        self.OWNER_ID = 1335428061541437531

    @app_commands.command(name="load", description="Cogをロードします。")
    async def load_command(
        self,
        interaction: discord.Interaction,
        cog_name: str
    ):
        await interaction.response.defer()
        
        if interaction.user.id != self.OWNER_ID:
            return await interaction.followup.send(content="❌ アクセスが拒否されました。")

        await self.bot.load_extension(f"cogs.{cog_name}")

        await interaction.followup.send(embed=discord.Embed(title="✅リロードしました。", color=discord.Color.green()))

    @app_commands.command(name="reload", description="Cogをリロードします。")
    async def reload_command(
        self,
        interaction: discord.Interaction,
        cog_name: str
    ):
        await interaction.response.defer()
        
        if interaction.user.id != self.OWNER_ID:
            return await interaction.followup.send(content="❌ アクセスが拒否されました。")

        await self.bot.reload_extension(f"cogs.{cog_name}")

        await interaction.followup.send(embed=discord.Embed(title="✅リロードしました。", color=discord.Color.green()))

    @app_commands.command(name="sync", description="スラッシュコマンドを同期します。")
    async def sync_command(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()
        
        if interaction.user.id != self.OWNER_ID:
            return await interaction.followup.send(content="❌ アクセスが拒否されました。")

        await self.bot.tree.sync()

        await interaction.followup.send(embed=discord.Embed(title="✅同期しました。", color=discord.Color.green()))

async def setup(bot):
    await bot.add_cog(AdminCog(bot))