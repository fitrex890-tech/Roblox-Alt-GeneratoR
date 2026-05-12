import os
import json
import secrets
import random
import asyncio
import discord
from datetime import datetime, date
from discord import app_commands, Embed, Color

# ==================== BOT SETUP ====================

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ==================== CONFIG ====================

DAILY_FILE = "daily_counter.json"
BOT_VERSION = "1.2"
DEVELOPER = "RealFitrex"
GROUP = "Zjednoczone Idee"

# ==================== TOKEN ====================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ Brak DISCORD_TOKEN w Railway Variables!")

# ==================== DAILY SYSTEM ====================

def get_today_key():
    return date.today().isoformat()

def get_daily_data():
    if not os.path.exists(DAILY_FILE):
        return {"date": get_today_key(), "count": 0}

    try:
        with open(DAILY_FILE, "r") as f:
            data = json.load(f)

        if data.get("date") != get_today_key():
            return {"date": get_today_key(), "count": 0}

        return data

    except:
        return {"date": get_today_key(), "count": 0}

def save_daily_data(data):
    with open(DAILY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_daily_count_and_increment():
    data = get_daily_data()
    data["count"] += 1
    save_daily_data(data)
    return data["count"]

def get_daily_count():
    return get_daily_data()["count"]

# ==================== EMBEDS ====================

def create_bot_info_embed():
    embed = Embed(title="🤖 Bot Informacje", color=0x00ff88)
    embed.add_field(name="Nazwa", value=bot.user.name if bot.user else "Loading...", inline=True)
    embed.add_field(name="Wersja", value=BOT_VERSION, inline=True)
    embed.add_field(name="Developer", value=DEVELOPER, inline=True)
    embed.add_field(name="Projekt", value=GROUP, inline=True)
    embed.add_field(name="Limit", value="2 konta / dzień", inline=True)
    return embed

def create_help_embed():
    embed = Embed(title="📜 Komendy", color=0x0099ff)
    embed.add_field(name="/generate", value="Tworzy konto (max 2/dzień)", inline=False)
    embed.add_field(name="/status", value="Status bota", inline=False)
    embed.add_field(name="/botinfo", value="Info o bocie", inline=False)
    embed.add_field(name="/help", value="Lista komend", inline=False)
    return embed

# ==================== COMMANDS ====================

@tree.command(name="botinfo", description="Informacje o bocie")
async def botinfo(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_bot_info_embed())

@tree.command(name="help", description="Lista komend")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_help_embed())

@tree.command(name="status", description="Status bota")
async def status(interaction: discord.Interaction):

    count = get_daily_count()

    embed = Embed(title="📊 Status", color=0xffaa00)
    embed.add_field(name="Dziś utworzono", value=f"{count}/2", inline=False)
    embed.add_field(name="Limit", value="2/dzień", inline=True)

    await interaction.response.send_message(embed=embed)

# ==================== GENERATE ====================

@tree.command(name="generate", description="Generuj konto")
async def generate(interaction: discord.Interaction, amount: int = 1):

    amount = max(1, min(amount, 2))
    count = get_daily_count()

    if count >= 2:
        embed = Embed(
            title="❌ Limit",
            description="Limit 2 kont/dzień osiągnięty.",
            color=Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    new_count = load_daily_count_and_increment()

    embed = Embed(
        title="✅ OK",
        description=f"Utworzono request. Dziś: {new_count}/2",
        color=Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ==================== READY ====================

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot online jako {bot.user}")

# ==================== RUN ====================

bot.run(TOKEN)
