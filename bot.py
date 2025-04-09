import nextcord
from nextcord.ext import commands, tasks
import os
from dotenv import load_dotenv
import requests

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
owner_id = int(os.getenv("OWNER_ID"))
channel_id = int(os.getenv("CHANNEL_ID"))
guild_id = int(os.getenv("GUILD_ID"))
join_code = os.getenv("JOIN_CODE")
join_link = "https://www.roblox.com/games/start?placeId=7711635737&launchData=joinCode%3D" + join_code
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
guild = None
channel = None

@bot.event
async def on_ready():
    global guild
    global channel
    guild = bot.get_guild(guild_id)
    channel = bot.get_channel(channel_id)
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Connected to guild: {guild.name} (ID: {guild.id})")
    print(f"Channel: {channel.name} (ID: {channel.id})")
    update_status.start()

def get_server_info():
    servers_url = f"https://api.emergency-hamburg.com/public/servers"
    response = requests.get(servers_url).json()

    target_server = None
    for server in response:
        if server.get("ownerId") == owner_id:
            target_server = server
            break
    return target_server

def create_embed():
    server_info = get_server_info()
    players = 0
    max_players = 42
    status = "🔴"
    if server_info:
        players = server_info['currentPlayers']
        max_players = server_info['maxPlayers']
        status = "🟢"

    embed = nextcord.Embed(
        title="Server Status",
        description="Current server status and player count.",
        color=nextcord.Color.blue(),
    )
    embed.add_field(name="Status", value=status, inline=False)
    embed.add_field(name="Players", value=f"{players}/{max_players}", inline=False)
    embed.add_field(name="Join Code", value=join_code, inline=False)
    embed.add_field(name="Join Link", value=f"[Click here to join]({join_link})", inline=False)
    embed.set_footer(text="Updated every minute.")
    return embed

@tasks.loop(minutes=1)
async def update_status():
    global channel
    if channel:
        embed = create_embed()
        await channel.purge(limit=1)
        await channel.send(embed=embed)

bot.run(token)
