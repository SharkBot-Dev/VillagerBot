import discord
from discord.ext import commands
from discord import app_commands

from bot import VillagerBot

class RankingCog(commands.Cog):
    def __init__(self, bot: VillagerBot):
        self.bot = bot

    @app_commands.command(name="ranking", description="経済ランキングを表示します。")
    async def ranking(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()

        db = self.bot.async_db["VillagerBot"].Player
        
        cursor = db.find({}).sort("money", -1).limit(10)
        top_players = await cursor.to_list(length=10)

        if not top_players:
            return await interaction.followup.send("まだデータがありません。")

        rank_text = ""
        for i, r in enumerate(top_players, start=1):
            user_id = r.get('user_id')
            money = r.get('money', 0)
            rank_text += f"**{i}位**: <@{user_id}> - {money:,}エメラルド\n"

        embed = discord.Embed(
            title="🏆 経済ランキング",
            description=rank_text,
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RankingCog(bot))