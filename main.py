import discord
import asyncio
from discord import app_commands
from colorama import Fore, init

# ================= COLORAMA SETUP =================
init(autoreset=True)
r   = Fore.RED
g   = Fore.GREEN
ora = Fore.YELLOW
p   = Fore.MAGENTA
s   = Fore.CYAN
wh  = Fore.WHITE

# ================= INTENTS & BOT =================
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ================= DATA STRUCTURES =================
whitelist = set()
welcome_channels = {}
farewell_channels = {}
invite_cache = {}

# ================= NEW PROTECTION TRACKING =================
ban_tracker = {}  # {guild_id: {user_id: [timestamps]}}
ONE_HOUR = 3600

# ================= BAN WITH RETRY =================
async def ban_with_retry(guild, target, reason, tries=3):
    for attempt in range(1, tries + 1):
        try:
            await guild.ban(target, reason=reason)
            print(f"[SUCCESS] Banned {target} on attempt {attempt}")
            return
        except Exception as e:
            print(f"[FAIL] Attempt {attempt} failed for {target}: {e}")
            await asyncio.sleep(1)

# ================= READY EVENT =================
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)  # force-online effect
    await tree.sync()
    for guild in bot.guilds:
        invite_cache[guild.id] = await guild.invites()
    
    # ================= CONSOLE BANNER =================
    print(f"""
                                {r} â–ˆâ–ˆâ–“â–ˆâ–ˆâ–ˆ   â–„â–„â–„      
                                {r}â–“â–ˆâ–ˆâ–‘  â–ˆâ–ˆâ–’â–’â–ˆâ–ˆâ–ˆâ–ˆâ–„    
                                {r}â–“â–ˆâ–ˆâ–‘ â–ˆâ–ˆâ–“â–’â–’â–ˆâ–ˆ  â–€â–ˆâ–„  
                                {r}â–’â–ˆâ–ˆâ–„â–ˆâ–“â–’ â–’â–‘â–ˆâ–ˆâ–„â–„â–„â–„â–ˆâ–ˆ 
                                {r}â–’â–ˆâ–ˆâ–’ â–‘  â–‘ â–“â–ˆ   â–“â–ˆâ–ˆâ–’
                                {r}â–’â–“â–’â–‘ â–‘  â–‘ â–’â–’   â–“â–’â–ˆâ–‘
                                {ora}â–‘â–’ â–‘       â–’   â–’â–’ â–‘
                                {ora}â–‘â–‘         â–‘   â–’   
                                {ora}             â–‘  â–‘

{g}â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆ      â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ 
{g}   â–ˆâ–ˆ    â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ             â–ˆâ–ˆ    â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ      â–ˆâ–ˆ      
{g}   â–ˆâ–ˆ    â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ          â–ˆâ–ˆ    â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆ      â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   
{g}   â–ˆâ–ˆ    â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ             â–ˆâ–ˆ    â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ      â–ˆâ–ˆ
{g}   â–ˆâ–ˆ    â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ        â–ˆâ–ˆ    â–ˆâ–ˆ   â–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ 
                                                                                        
{ora}{p} {s}- [{Fore.GREEN}+{s}] {wh}Logged in as {bot.user.name}
{ora}{p} {s}- [{Fore.GREEN}+{s}] {wh}Nuke command is {p}!getdiddyed
    """)

# ================= BAN TRACKER EVENT =================
@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
        if entry.target.id == user.id:
            executor = entry.user
            if executor.id in whitelist:
                return
            now = asyncio.get_event_loop().time()
            if guild.id not in ban_tracker:
                ban_tracker[guild.id] = {}
            if executor.id not in ban_tracker[guild.id]:
                ban_tracker[guild.id][executor.id] = []
            ban_tracker[guild.id][executor.id] = [
                t for t in ban_tracker[guild.id][executor.id]
                if now - t <= ONE_HOUR
            ]
            ban_tracker[guild.id][executor.id].append(now)
            if len(ban_tracker[guild.id][executor.id]) >= 2:
                await ban_with_retry(guild, executor, "Banned 2 members within 1 hour (Protection Triggered)")
            break

# ================= CHANNEL CREATE AUTO BAN =================
@bot.event
async def on_guild_channel_create(channel):
    guild = channel.guild
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_create):
        if entry.target.id == channel.id:
            executor = entry.user
            if executor.id in whitelist:
                return
            await ban_with_retry(guild, executor, "Unauthorized channel creation (Protection Triggered)")
            break

# ================= WHITELIST COMMANDS =================
@tree.command(name="whitelist", description="Add user to whitelist")
@app_commands.checks.has_permissions(administrator=True)
async def whitelist_cmd(interaction: discord.Interaction, member: discord.Member):
    whitelist.add(member.id)
    await interaction.response.send_message(f"✅ {member.mention} added to whitelist.", ephemeral=True)

@tree.command(name="unwhitelist", description="Remove user from whitelist")
@app_commands.checks.has_permissions(administrator=True)
async def unwhitelist_cmd(interaction: discord.Interaction, member: discord.Member):
    whitelist.discard(member.id)
    await interaction.response.send_message(f"❌ {member.mention} removed from whitelist.", ephemeral=True)

@tree.command(name="whitelistlist", description="Show whitelist")
@app_commands.checks.has_permissions(administrator=True)
async def whitelistlist_cmd(interaction: discord.Interaction):
    if not whitelist:
        await interaction.response.send_message("Whitelist is empty.", ephemeral=True)
        return
    names = []
    for uid in whitelist:
        user = interaction.guild.get_member(uid)
        if user:
            names.append(user.mention)
    await interaction.response.send_message("\n".join(names), ephemeral=True)

# ================= WELCOME / FAREWELL CHANNELS =================
@tree.command(name="add_welcome", description="Set welcome channel")
@app_commands.checks.has_permissions(administrator=True)
async def add_welcome(interaction: discord.Interaction, channel: discord.TextChannel):
    welcome_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"Welcome messages set to {channel.mention}", ephemeral=True)

@tree.command(name="add_byebye", description="Set farewell channel")
@app_commands.checks.has_permissions(administrator=True)
async def add_byebye(interaction: discord.Interaction, channel: discord.TextChannel):
    farewell_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"Farewell messages set to {channel.mention}", ephemeral=True)

# ================= MEMBER JOIN =================
@bot.event
async def on_member_join(member):
    guild = member.guild
    if member.bot:
        await asyncio.sleep(1)
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
            if entry.target.id == member.id:
                adder = entry.user
                if adder.id not in whitelist:
                    await ban_with_retry(guild, adder, "Attempted nuke")
                    await ban_with_retry(guild, member, "Attempted nuke")
                break
        return

# ================= MEMBER REMOVE =================
@bot.event
async def on_member_remove(member):
    guild = member.guild
    if guild.id in farewell_channels:
        channel = guild.get_channel(farewell_channels[guild.id])
        if channel:
            await channel.send(
                f"{member.mention} left the server, {guild.name} now has {guild.member_count} members."
            )

# ================= RUN BOT =================
bot.run("MTQ4MDkzMDI0NDAzNzk3MjEwMQ.GMqCOw.PuGM_OQOWACPk0LUs2ffl-rtZ2y88DwH7Hi5po")
