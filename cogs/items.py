import discord
from discord.ext import commands, tasks
from discord import app_commands

import math

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
            "iron_ore": {
                "name": "鉄鉱石",
                "price": 0.5,
                "id": "iron_ore"
            },
            "iron_ingot": {
                "name": "鉄インゴット",
                "price": 1.0,
                "id": "iron_ingot"
            },
            "coal": {
                "name": "石炭",
                "price": 0.05,
                "id": "coal"
            },
            "wooden_pickaxe": {
                "name": "木のツルハシ",
                "price": 0.5,
                "id": "wooden_pickaxe"
            },
            "stone_pickaxe": {
                "name": "石のツルハシ",
                "price": 1.0,
                "id": "stone_pickaxe"
            },
            "fishing_rod": {
                "name": "釣竿",
                "price": 1.0,
                "id": "fishing_rod"
            },
            "tropical_fish": {
                "name": "熱帯魚",
                "price": 0.5,
                "id": "tropical_fish"
            },
            "salmon": {
                "name": "生鮭",
                "price": 0.5,
                "id": "salmon"
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
            await interaction.followup.send("❌持ち物は空です。")
        else:
            msg = "\n".join([f"{self.ITEMS.get(item_id, {}).get('name', '不明')}: {count}個 ({self.ITEMS.get(item_id, {}).get('price', '0')}エメラルド)" for item_id, count in inv.items()])
            await interaction.followup.send(f"**あなたの持ち物:**\n{msg}")

    async def sell_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ):
        inv = await self.bot.item.get_inventory(interaction.user.id)
        
        choices = []
        for item_id, count in inv.items():
            item_info = self.ITEMS.get(item_id)
            if not item_info: continue
            
            name = item_info.get("name", "不明")
            price = item_info.get("price", 0)
            
            choice_text = f"{name} (所持: {count} / 単価: {price})"
            if current.lower() in choice_text.lower():
                choices.append(app_commands.Choice(name=choice_text, value=item_id))
        
        return choices[:25]

    @item.command(name="sell", description="アイテムを売却してエメラルドを得ます。")
    @app_commands.autocomplete(アイテム=sell_autocomplete)
    @app_commands.describe(アイテム="売却するアイテム", 個数="売却する数（1以上の整数）")
    async def item_sell(
        self,
        interaction: discord.Interaction,
        アイテム: str,
        個数: int = 1
    ):
        if 個数 <= 0:
            return await interaction.response.send_message("❌ 個数は1以上にしてください。", ephemeral=True)

        await interaction.response.defer()

        item_info = self.ITEMS.get(アイテム)
        if not item_info:
            return await interaction.followup.send("❌ そのアイテムは存在しません。")

        current_count = await self.bot.item.get_item_count(interaction.user.id, アイテム)
        if current_count < 個数:
            return await interaction.followup.send(f"❌ {item_info['name']}が足りません（所持: {current_count}個）")

        total_price = math.floor(item_info["price"] * 個数)
        
        await self.bot.item.add_item(interaction.user.id, アイテム, -個数)
        await self.bot.money.add_money(interaction.user.id, total_price)

        await interaction.followup.send(
            f"✅ **{item_info['name']}** を **{個数}個** 売却しました。\n"
            f"💰 **{total_price}エメラルド** を獲得しました。"
        )

    async def buy_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        inv = self.bot.item.get_all_item_list()
        
        choices = []
        for item_id, count in inv.items():
            item_info = self.ITEMS.get(item_id)
            if not item_info:
                continue
            
            name = item_info.get("name", "不明")
            price = item_info.get("price", 0)

            if current.lower() in name.lower():
                choices.append(
                    app_commands.Choice(
                        name=f"{name} (単価: {price}エメラルド)",
                        value=item_id
                    )
                )
            
            if len(choices) >= 25:
                break
        
        return choices

    @app_commands.command(name="buy", description="アイテムを購入します。")
    @app_commands.describe(アイテム="購入するアイテム", 個数="購入する数")
    @app_commands.autocomplete(アイテム=buy_autocomplete)
    async def buy_item(self, interaction: discord.Interaction, アイテム: str, 個数: int = 1):
        if 個数 <= 0:
            return await interaction.response.send_message("❌ 個数は1以上にしてください。", ephemeral=True)

        await interaction.response.defer()
        info = self.bot.item.get_item_info(アイテム)
        if not info:
            return await interaction.followup.send("❌ そのアイテムはショップで扱っていません。")

        total_cost = math.ceil(info["price"] * 個数)
        balance = await self.bot.money.get_money(interaction.user.id)

        if balance < total_cost:
            return await interaction.followup.send(f"❌ エメラルドが足りません！（必要: {total_cost} | 所持: {balance}）")

        await self.bot.money.add_money(interaction.user.id, -total_cost)
        await self.bot.item.add_item(interaction.user.id, アイテム, 個数)

        await interaction.followup.send(
            f"✅ **{info['name']}** を{個数}個購入しました！\n"
            f"💸 支払額: **{total_cost}エメラルド**"
        )

async def setup(bot):
    await bot.add_cog(ItemsCog(bot))