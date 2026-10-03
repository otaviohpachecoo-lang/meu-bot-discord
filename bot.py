import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot logado como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

TOKEN = os.getenv("DISCORD_TOKEN")
# Se não usar Variable na Railway, coloca direto:
# TOKEN = "SEU_TOKEN_AQUI"

bot.run(TOKEN)