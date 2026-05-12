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
GROUP = "Zjednoczone Ideą"

# ==================== TOKEN FIX (RAILWAY SAFE) ====================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ Brak DISCORD_TOKEN w Railway Variables!")

# ==================== FILE HELPERS ====================

def load_settings():
    with open('settings.json') as f:
        return json.load(f)

def load_proxies():
    if not os.path.exists('proxy.txt'):
        return []
    with open('proxy.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def get_today_key():
    return date.today().isoformat()

def get_daily_data():
    if not os.path.exists(DAILY_FILE):
        return {"date": get_today_key(), "count": 0}

    try:
        with open(DAILY_FILE, 'r') as f:
            data = json.load(f)

        if data.get("date") != get_today_key():
            return {"date": get_today_key(), "count": 0}

        return data

    except:
        return {"date": get_today_key(), "count": 0}

def save_daily_data(data):
    with open(DAILY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_daily_count_and_increment():
    data = get_daily_data()
    data["count"] += 1
    save_daily_data(data)
    return data["count"]

def get_daily_count():
    return get_daily_data()["count"]

# ==================== UTIL ====================

def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

def generate_random_username():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(10))

def generate_strong_password():
    return secrets.token_urlsafe(20)

async def human_like_delay(min_sec=8, max_sec=20):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

def write_to_file(username, password, proxy_used="Brak"):
    with open('accounts.txt', 'a', encoding='utf-8') as f:
        f.write(f"{username}:{password} | Proxy: {proxy_used} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

# ==================== EMBEDS ====================

def create_bot_info_embed():
    embed = Embed(title="🤖 Bot Informacje", color=0x00ff88)
    embed.add_field(name="Nazwa", value=bot.user.name if bot.user else "Loading...", inline=True)
    embed.add_field(name="Wersja", value=BOT_VERSION, inline=True)
    embed.add_field(name="Developer", value=DEVELOPER, inline=True)
    embed.add_field(name="Projekt", value=GROUP, inline=True)
    embed.add_field(name="Cel", value="Automatyczne tworzenie kont Roblox", inline=False)
    embed.add_field(name="Limit", value="2 konta / dzień", inline=True)
    return embed

def create_help_embed():
    embed = Embed(title="📜 Komendy", color=0x0099ff)
    embed.add_field(name="/generate [amount]", value="Tworzy konto (max 2/dzień)", inline=False)
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
    proxies = load_proxies()
    count = get_daily_count()

    embed = Embed(title="📊 Status", color=0xffaa00)
    embed.add_field(name="Dziś utworzono", value=f"{count}/2", inline=False)
    embed.add_field(name="Proxy", value=str(len(proxies)), inline=True)
    embed.add_field(name="Limit", value="2/dzień", inline=True)

    await interaction.response.send_message(embed=embed)

# ==================== GENERATE (placeholder) ====================

@tree.command(name="generate", description="Generuj konto")
@app_commands.describe(amount="Ile kont (1-2)")
async def generate(interaction: discord.Interaction, amount: int = 1):

    amount = min(max(amount, 1), 2)
    count = get_daily_count()

    if count >= 2:
        embed = Embed(title="❌ Limit", description="Limit 2 kont/dzień osiągnięty.", color=Color.red())
        return await interaction.response.send_message(embed=embed)

    new_count = load_daily_count_and_increment()

    embed = Embed(title="✅ OK", description=f"Utworzono request. Dziś: {new_count}/2", color=Color.green())
    await interaction.response.send_message(embed=embed)

# ==================== READY ====================

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot online jako {bot.user}")

# ==================== RUN ====================

bot.run(TOKEN)
