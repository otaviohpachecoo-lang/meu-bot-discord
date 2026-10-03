import 【entity-discord¦canonical_name=discord】
from 【entity-discord¦canonical_name=discord】.ext import commands, tasks
import os
import random
import asyncio
from openai import AsyncOpenAI

# --- CONFIGURAÇÃO ---
# Não precisa mexer aqui, o token vai ser colocado na Railway
TOKEN = os.getenv("DISCORD_TOKEN")
IA_KEY = os.getenv("IA_API_KEY")

intents = 【entity-discord¦canonical_name=discord】.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Conecta na IA da Groq (grátis)
ia_client = AsyncOpenAI(
    api_key=IA_KEY,
    base_url="https://api.groq.com/openai/v1"
) if IA_KEY else None

# Personalidade da IA
PERSONALIDADE = "Você é o ADM do servidor, brasileiro, zoeiro, gente boa, ajuda todo mundo. Fala curto, com gíria. Você gerencia o servidor."

async def responder_ia(pergunta):
    if not ia_client:
        return "Minha IA ainda não foi configurada na hospedagem."
    try:
        resp = await ia_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PERSONALIDADE},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=250
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Buguei aqui: {e}"

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")
    falar_sozinho.start()
    try:
        await bot.tree.sync()
    except: pass

# --- GERENCIAMENTO ---
@bot.event
async def on_member_join(member):
    # Mensagem de boas vindas
    canal = discord.utils.get(member.guild.text_channels, name="geral") or member.guild.system_channel
    if canal:
        await canal.send(f"Bem vindo {member.mention}! Leia as regras! 🚀")

    # Cargo automático
    cargo = discord.utils.get(member.guild.roles, name="Membro")
    if cargo:
        try: await member.add_roles(cargo)
        except: pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Anti link 【entity-discord¦canonical_name=discord】
    if "【entity-discord¦canonical_name=discord】.gg/" in message.content and not message.author.guild_permissions.administrator:
        await message.delete()
        await message.channel.send(f"{message.author.mention} link de outro discord não pode!", delete_after=5)
        return

    # Se mencionar o bot, responde com IA
    if bot.user in message.mentions:
        async with message.channel.typing():
            resposta = await responder_ia(message.content)
            await message.reply(resposta)

    await bot.process_commands(message)

# --- FALA SOZINHO A CADA 30 MIN ---
@tasks.loop(minutes=30)
async def falar_sozinho():
    # Pega o primeiro canal de texto que achar
    for guild in bot.guilds:
        canal = discord.utils.get(guild.text_channels, name="conversa") or discord.utils.get(guild.text_channels, name="geral") or guild.text_channels[0]
        if canal:
            perguntas = [
                "Fala galera, o que tão jogando hoje?",
                "Pergunta polêmica: pizza com ketchup sim ou não?",
                "Manda uma piada pra animar o chat",
                "Alguém afim de jogar alguma coisa agora?"
            ]
            prompt = random.choice(perguntas)
            resposta = await responder_ia(prompt)
            try: await canal.send(resposta)
            except: pass
            break

# --- COMANDOS DE ADM ---
@bot.tree.command(name="ban", description="Banir membro")
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("Você não tem permissão!", ephemeral=True)
    await membro.ban(reason=motivo)
    await interaction.response.send_message(f"{membro} banido! Motivo: {motivo}")

@bot.tree.command(name="clear", description="Limpar mensagens")
async def clear(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("Sem permissão!", ephemeral=True)
    await interaction.channel.purge(limit=quantidade)
    await interaction.response.send_message(f"{quantidade} mensagens apagadas!", ephemeral=True)

@bot.tree.command(name="ping", description="Ver ping do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency*1000)}ms")

bot.run(TOKEN)