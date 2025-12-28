import discord
from discord.ext import commands, tasks
import json, os
from aiohttp import web

# =====================
# CONFIG YÜKLE
# =====================
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# =====================
# BOT SETUP
# =====================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# KARŞILAMA
# =====================
@bot.event
async def on_member_join(member):
    kanal = discord.utils.get(member.guild.text_channels, name=config["channels"]["welcome"])
    if kanal:
        await kanal.send(
            f"👋 Hoş geldin {member.mention}!\n"
            f"🧩 Rol almak için **#{config['channels']['roles']}**\n"
            f"📜 Kuralları okumayı unutma."
        )

# =====================
# YARDIM KOMUTU
# =====================
@bot.command()
async def yardım(ctx):
    embed = discord.Embed(
        title="🟣 NEXORA BOT KOMUTLARI",
        color=0x9b59b6
    )
    embed.add_field(name="💸 Ekonomi", value="!para\n!günlük", inline=False)
    embed.add_field(name="📊 Sunucu", value="!bilgi", inline=False)
    embed.add_field(name="🎭 Roller", value="!rol", inline=False)
    await ctx.send(embed=embed)

# =====================
# EKONOMİ
# =====================
@bot.command()
async def para(ctx):
    eco = load("economy.json")
    uid = str(ctx.author.id)
    if uid not in eco:
        eco[uid] = config["economy"]["start_money"]
    save("economy.json", eco)
    await ctx.send(f"💰 {ctx.author.mention} bakiyen: **{eco[uid]}** coin")

@bot.command()
async def günlük(ctx):
    eco = load("economy.json")
    uid = str(ctx.author.id)
    eco[uid] = eco.get(uid, 0) + config["economy"]["daily_reward"]
    save("economy.json", eco)
    await ctx.send(f"🎁 Günlük ödül: +{config['economy']['daily_reward']} coin")

# =====================
# LEVEL SİSTEMİ
# =====================
@bot.event
async def on_message(message):
    if message.author.bot: return
    levels = load("level.json")
    uid = str(message.author.id)
    levels.setdefault(uid, {"xp":0, "level":1})
    levels[uid]["xp"] += config["level"]["xp_per_message"]

    if levels[uid]["xp"] >= levels[uid]["level"]*100:
        levels[uid]["level"] += 1
        await message.channel.send(f"🎉 {message.author.mention} level atladı! (**{levels[uid]['level']}**)")
        role_name = config["level"]["level_roles"].get(str(levels[uid]["level"]))
        if role_name:
            role = discord.utils.get(message.guild.roles, name=role_name)
            if role:
                await message.author.add_roles(role)
    save("level.json", levels)
    await bot.process_commands(message)

# =====================
# SUNUCU BİLGİ
# =====================
@bot.command()
async def bilgi(ctx):
    g = ctx.guild
    embed = discord.Embed(title="📊 Sunucu Bilgisi", color=0x9b59b6)
    embed.add_field(name="👥 Üyeler", value=g.member_count)
    embed.add_field(name="📅 Kuruluş", value=g.created_at.strftime("%d.%m.%Y"))
    await ctx.send(embed=embed)

# =====================
# ROL KOMUTU (ÖRNEK)
# =====================
@bot.command()
async def rol(ctx):
    await ctx.send("🎭 Rol sistemi aktif! Kanaldan rollerinizi alabilirsiniz.")

# =====================
# 7/24 REPLIT / GLITCH PING
# =====================
async def handle(request):
    return web.Response(text="NEXORA BOT AKTİF 🟣")

app = web.Application()
app.add_routes([web.get('/', handle)])
runner = web.AppRunner(app)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} aktif!")
    await bot.change_presence(activity=discord.Game("NEXORA | !yardım"))
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

# =====================
# BOTU ÇALIŞTIR
# =====================
bot.run(os.getenv("MTQ1NDgwNjU0MjYwMjczNTc4OA.G0F1wq.dNYlhJJz74QnLABMFYTaXbDZ_YgT0ZXl-mjq3Q"))
