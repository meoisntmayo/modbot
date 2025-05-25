import discord
import typing
import json
import enum
import time
import datetime
import aiohttp
import random
import asyncio
import requests
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ui import Button, View
from discord.utils import get
from typing import Literal

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='robert!', intents=intents)
tree = bot.tree

bot.session = None

# Load existing data from db.json
def load_db():
    try:
        with open('db.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save data to db.json
def save_db(data):
    with open('db.json', 'w') as f:
        json.dump(data, f, indent=4)

class truefalse(str, enum.Enum):
    Yes = "yes"
    No = "no"

def convert_time_to_seconds(time_str):
    time_unit = time_str[-1]  # Get the last character which indicates the unit (e.g., 'd')
    time_value = int(time_str[:-1])  # Get the numeric value (e.g., '4')

    if time_unit == 'w':
        return time_value * 604800  # 1 week = 604800 seconds
    elif time_unit == 'd':
        return time_value * 86400  # 1 day = 86400 seconds
    elif time_unit == 'h':
        return time_value * 3600  # 1 hour = 3600 seconds
    elif time_unit == 'm':
        return time_value * 60  # 1 minute = 60 seconds
    elif time_unit == 's':
        return time_value  # Already in seconds
    else:
        raise ValueError("Unsupported time unit")

@bot.event
async def on_ready():
    await bot.tree.sync()  # Synchronize the commands with Discord
    bot.session = aiohttp.ClientSession()
    print(f"haiiii :3")

@bot.hybrid_command(name="speak", description="makes robbert say something")
@app_commands.describe(message="what to says")
async def speak(ctx: commands.Context, message: str):
    try:
        await ctx.send(message)
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="ping", description="gets ping!!!!")
async def ping(ctx: commands.Context):
    try:
        await ctx.send(f"pong :3 brain delay of {round(bot.latency *1000)} ms")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="info", description="shows info (crazy)")
async def info(ctx: commands.Context):
    embed = discord.Embed(
        title="About Robert",
        description="Robert is a moderation bot. He's the boss of the Bitchly Peeps (:bp_blue: :bp_yellow: :bp_pink:), aka the BP Mafia. He can speak English, Spanish, Italian, and Serbian; he has gone round-trip around the world as well."
  color=discord.Color.green()
    )
    embed.set_footer(text="more coming soon maybe")
    try:
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="tip", description="not money")
async def info(ctx: commands.Context):
    tips = ["BUGS WILL ATTACK🪰🪰🪰🪰🪰🪰🪰🪰🪰🪲🪲🪲🪰🪲🪰🪲🪰🪲🪰🪲🪰🪲🪰🪲🪰🐜‼️‼️‼ ️‼️THROW YOUR PHONE OUT THE WINDOW OR IT WILL EXPLODE‼️‼️‼️✅✅✅🈯️🈯️🔇🔇🔕 🔕🟩▫️©➖❗️🖇🔥🔥💥🔥💥🔥🔥💥🔥🔥💥💥BUGS WILL ATTACK🪰🪰🪰🪰🪰🪰🪰🪰🪰 🪲🪲🪲🪰🪲🪰🪲🪰🪲🪰🪲🪰🪲🪰🐜‼️‼️‼️‼️THROW OUT PUT YOUR PHONE OUT THE WINDOW OR IT WILL EXPLODE‼️‼️‼️✅✅✅", "I rob orphans daily", "canonically I am multilingual, speaking English, Spanish, Italian, and Serbian. Unfortunately coder is too stupid to do thar in the bot", "pipe bomb", "this bot is made of 74% ai slop", "item asylum is way more interesting", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "meo was here", "robs you", "skibidi toilet ended my 5 year long relationship", "the game", "i ate 37 homeless people because I thought they were watermelons", "there's no actual tips here, you can stop running the command", "incoherent screaming"]
    emoji = ["<a:anistar_red:1370818130502221925>︱", "<a:anistar_orange:1370818231350071426>︱", "<a:anistar_yellow:1370818280394330193>︱", "<a:anistar_green:1370818329014440028>︱", "<a:anistar_blue:1370818376103886971>︱", "<a:anistar_purple:1370818424057630842>︱"]
    try:
        await ctx.send(random.choice(emoji)+random.choice(tips))
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="ban", description="banana no apple peal")
@discord.app_commands.default_permissions(ban_members=True)
@app_commands.describe(user="who need bye")
@app_commands.describe(reason="why who needs bye")
async def ban(ctx: commands.Context, user: discord.User, reason: str = "lol get rekd or something loser (no reason provided)", appeal: truefalse = "yes"):
    db = load_db()
    guild_id = str(ctx.guild.id)
    mod_roles = db.get(guild_id, {}).get("mod_roles", {})
    mod_role = ctx.guild.get_role(int(mod_roles.get("MODERATOR ACTIONS"))) if mod_roles.get("MODERATOR ACTIONS") else None
    admin_role = ctx.guild.get_role(int(mod_roles.get("Current Co Owner"))) if mod_roles.get("Current Co Owner") else None

    async def get_appeal_message():
        appeal_info = db.get(guild_id, {})
        if appeal != "yes":
            return "you can't appeal this ban bozo L"
        server_id = appeal_info.get("appeal_server")
        if server_id:
            try:
                appeal_guild = bot.get_guild(int(server_id))
                if appeal_guild and appeal_guild.text_channels:
                    invite = await appeal_guild.text_channels[0].create_invite(max_age=3600, max_uses=1, unique=True, reason="ban appeal link")
                    return f"if you think we made a mistake or something feel free to appeal here: {invite.url} no unban promises"
            except Exception as e:
                print(f"Failed to create appeal invite: {e}")
        return appeal_info.get("appeal_message", "you can't appeal this ban bozo L")

    confirm_button = discord.ui.Button(label="r yoy sure", style=discord.ButtonStyle.secondary)

    async def confirm_button_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("403 forbidden", ephemeral=True)
            return

        is_mod = (
            ctx.author.guild_permissions.ban_members
            or ctx.author.guild_permissions.administrator
            or (mod_role in ctx.author.roles if mod_role else False)
            or (admin_role in ctx.author.roles if admin_role else False)
        )

        if not is_mod:
            await interaction.response.edit_message(
                content=f"<@{ctx.author.id}> is trying to ban <@{user.id}> for `{reason}`.\nThey need a confirmation from a higher-up staff member because they are a LOSER lmaooooooo L BOZO",
                view=None
            )

            approval_view = discord.ui.View()
            approve_button = discord.ui.Button(label="yeah sure go for it", style=discord.ButtonStyle.danger)

            async def approve_button_callback(approval_interaction: discord.Interaction):
                approver = approval_interaction.user
                approver_is_mod = (
                    approver.guild_permissions.ban_members
                    or approver.guild_permissions.administrator
                    or (mod_role in approver.roles if mod_role else False)
                    or (admin_role in approver.roles if admin_role else False)
                )

                if not approver_is_mod:
                    await approval_interaction.response.send_message("403 forbidden (you can't approve this lol)", ephemeral=True)
                    return

                try:
                    appeal_message = await get_appeal_message()
                    await user.send(f"hi bozo you have been banned from {ctx.guild.name} for `{reason}`. {appeal_message}. do better next time lmao")
                except Exception as e:
                    print(f"Failed to send DM: {e}")

                await approval_interaction.guild.ban(user, reason=reason, delete_message_seconds=0)
                await log_action(ctx.guild, f"{user.mention} was permanently banned by {ctx.author.mention} (confirmed by {approver.mention}) for `{reason}`.")
                await approval_interaction.response.edit_message(
                    content=f"{user.mention} was banned by {ctx.author.mention} (confirmed by {approver.mention}) for `{reason}`.",
                    view=None,
                    allowed_mentions=discord.AllowedMentions.none()
                )

            approve_button.callback = approve_button_callback
            approval_view.add_item(approve_button)

            await interaction.followup.send(view=approval_view, ephemeral=False)
            return

        try:
            appeal_message = await get_appeal_message()
            await user.send(f"hi bozo you have been banned from {ctx.guild.name} for `{reason}`. {appeal_message}. do better next time lmao")
        except Exception as e:
            print(f"Failed to send DM: {e}")

        await interaction.guild.ban(user, reason=reason, delete_message_seconds=0)
        await log_action(ctx.guild, f"{user.mention} was permanently banned by {ctx.author.mention} for `{reason}`.")
        await interaction.response.edit_message(
            content=f"{user.mention} was permanently banned by {ctx.author.mention} for `{reason}`.",
            view=None,
            allowed_mentions=discord.AllowedMentions.none()
        )

    confirm_button.callback = confirm_button_callback

    view = discord.ui.View()
    view.add_item(confirm_button)

    try:
        await ctx.send(f"banning {user.mention}? (they cant come back legally)", view=view)
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

# Error handler
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("403 forbidden (you can't even ask for a ban LMAOOOOO)", ephemeral=True)
    else:
        raise error

@bot.hybrid_command(name="appeal", description="whar")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(appeal="how the fuck do you appeal")
async def speak(ctx: commands.Context, appeal: str):
    # Load the database
    db = load_db()

    # Save the appeal message and server ID
    server_id = str(ctx.guild.id)
    # Ensure the server ID exists in the database
    if server_id not in db:
        db[server_id] = {}

    db[server_id]["appeal_message"] = appeal


    # Save the updated database
    save_db(db)
    try:
        await log_action(ctx.guild, f"appeal message set to {appeal} for {ctx.guild.name} by {ctx.author}.")
        await ctx.send(f"appeal message set to {appeal} for {ctx.guild.name}")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="appeals-configure", description="Link this server as the appeals server for another server.")
@commands.has_permissions(administrator=True)
@app_commands.describe(main_server_id="The ID of the server this one will handle appeals for.")
async def appeals_configure(ctx: commands.Context, main_server_id: str):
    db = load_db()

    # Convert to int
    try:
        main_server_id_int = int(main_server_id)
    except ValueError:
        try:
            await ctx.send("invalid server id. right click the main server you want to link with developer mode enabled")
        except Exception as e:
            await ctx.channel.send(f"504 internal server error\n-# {e}")
        return

    main_guild = bot.get_guild(main_server_id_int)
    if not main_guild:
        try:
            await ctx.send("add the bot to the main server")
        except Exception as e:
            await ctx.channel.send(f"504 internal server error\n-# {e}")
        return

    main_member = main_guild.get_member(ctx.author.id)
    if not main_member:
        try:
            await ctx.send("lil bro isnt in that server :rofl:")
        except Exception as e:
            await ctx.channel.send(f"504 internal server error\n-# {e}")
        return

    if not main_member.guild_permissions.administrator:
        try:
            await ctx.send("you gotta have admin in main server bozo")
        except Exception as e:
            await ctx.channel.send(f"504 internal server error\n-# {e}")
        return

    if not ctx.author.guild_permissions.administrator:
        try:
            await ctx.send("you must also have admin in this server")
        except Exception as e:
            await ctx.channel.send(f"504 internal server error\n-# {e}")
        return

    # Store the link in both directions
    main_id = str(main_server_id_int)
    appeals_id = str(ctx.guild.id)

    if main_id not in db:
        db[main_id] = {}
    if appeals_id not in db:
        db[appeals_id] = {}

    db[main_id]["appeal_server"] = appeals_id
    db[appeals_id]["main_server"] = main_id

    save_db(db)

    await log_action(main_guild, f"📥 {ctx.guild.name} is now the appeals server for `{main_guild.name}`, set by {ctx.author.mention}.")
    try:
        await ctx.send(f"this server will now handle appeals for `{main_guild.name}`")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="accept", description="accept an appeal request and give em a second chance.")
@discord.app_commands.default_permissions(kick_members=True)
@app_commands.describe(user="The appealing user to accept")
@app_commands.describe(reason="Reason for accepting their appeal")
async def accept(ctx: commands.Context, user: discord.User, reason: str = "No reason provided."):
    db = load_db()
    appeal_guild_id = str(ctx.guild.id)
    appeal_data = db.get(appeal_guild_id, {})
    main_server_id = appeal_data.get("main_server")

    if not main_server_id:
        await ctx.reply("Main server is not linked in the database.")
        return

    main_guild = bot.get_guild(int(main_server_id))
    if not main_guild:
        await ctx.reply("Main server not found. Is the bot in it?")
        return

    # Try to generate an invite link
    try:
        first_text_channel = next((c for c in main_guild.text_channels if c.permissions_for(main_guild.me).create_instant_invite), None)
        invite = await first_text_channel.create_invite(max_age=3600, max_uses=1, unique=True, reason="Appeal accepted")
        await user.send(
            f"hello your appeal in `{main_guild.name}` has been accepted!\n"
            f"reason: `{reason}`\n"
            f"join back using {invite.url}"
        )
    except Exception as e:
        await ctx.reply(f"Failed to DM user: {e}")
        return

    # Try to unban
    try:
        await main_guild.unban(user, reason=f"appeal accepted!!!! {reason}")
    except discord.NotFound:
        await ctx.reply("user was not banned in the main server wtf are you doing")
    except Exception as e:
        await ctx.reply(f"Unban failed: {e}")
        return

    # Try to kick from appeals
    try:
        await ctx.guild.kick(user, reason="Appeal accepted and processed")
    except Exception as e:
        await ctx.reply(f"Kick failed: {e}")
        return

    # Send reply and log
    await log_action(main_guild, f"<@{user.id}>'s appeal was accepted by <@{ctx.author.id}> because`{reason}`.")
    try:
        await ctx.reply(f"<@{user.id}>'s appeal was accepted by <@{ctx.author.id}> because `{reason}`.")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="deny", description="GET OUUTTTTTTTTT")
@discord.app_commands.default_permissions(kick_members=True)
@app_commands.describe(user="The appealing user to deny")
@app_commands.describe(reason="Reason for denying their appeal")
async def deny(ctx: commands.Context, user: discord.User, reason: str = "No reason provided."):
    db = load_db()
    appeal_guild_id = str(ctx.guild.id)
    appeal_data = db.get(appeal_guild_id, {})
    main_server_id = appeal_data.get("main_server")

    if not main_server_id:
        await ctx.reply("Main server is not linked in the database.")
        return

    main_guild = bot.get_guild(int(main_server_id))
    if not main_guild:
        await ctx.reply("Main server not found. Is the bot in it?")
        return

    # DM the user
    try:
        await user.send(
            f"hi bozo your appeal in `{main_guild.name}` was denied for `{reason}`. lol imagine"
        )
    except Exception as e:
        await ctx.reply(f"Failed to DM user: {e}")
        return

    # Kick from appeals
    try:
        await ctx.guild.kick(user, reason="Appeal denied")
    except Exception as e:
        await ctx.reply(f"Kick failed: {e}")
        return

    # Reply and log
    await log_action(main_guild, f"<@{user.id}>'s appeal was denied by <@{ctx.author.id}> with the reason `{reason}`.")
    try:
        await ctx.reply(f"<@{user.id}>'s appeal was denied by <@{ctx.author.id}> with the reason `{reason}`.")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.event
async def on_member_join(member: discord.Member):
    db = load_db()
    appeals_id = str(member.guild.id)

    # Check if this server is registered as an appeals server
    main_id = db.get(appeals_id, {}).get("main_server")
    if not main_id:
        return

    main_guild = bot.get_guild(int(main_id))
    if not main_guild:
        return

    # Look for the action log channel in the main guild
    log_channel_id = db.get(main_id, {}).get("action_log_channel")
    if not log_channel_id:
        return

    log_channel = main_guild.get_channel(int(log_channel_id))
    if not log_channel:
        return

    # Search the latest 50 log messages for a ban message mentioning this user
    async for message in log_channel.history(limit=50):
        if f"<@{str(member.id)}> was permanently banned by" in message.content:
            # Found a relevant log, send it to the first text channel in the appeals server
            first_text_channel = discord.utils.get(member.guild.text_channels, type=discord.ChannelType.text)
            if first_text_channel:
                try:
                    await first_text_channel.send(message.content)
                except Exception as e:
                    print(f"Failed to send appeal context in {member.guild.name}: {e}")
            break  # Stop after first relevant match

@bot.hybrid_command(name="kick", description="yeet")
@discord.app_commands.default_permissions(kick_members=True)
@app_commands.describe(user="the nerd to yeet")
@app_commands.describe(reason="reason (e.g. memes in general)")
async def kick(ctx: commands.Context, user: discord.User, reason: str):
    # Define the button
    button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.secondary)

    # Define the callback function for the button
    async def button_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("403 forbidden", ephemeral=True)
            return

        # Perform the kick and stuff
        try:
            await user.send(f"hello nerd you might have been kicked from {ctx.guild.name} for `{reason}`.")
        except Exception as e:
            print(f"Failed to send DM: {e}")

        await interaction.guild.kick(user, reason=reason)
        await log_action(ctx.guild, f"{user} was kicked by {ctx.author} for `{reason}`.")
        await interaction.response.edit_message(content=f"{user.mention} was kicked by {interaction.user.mention} for `{reason}`.", view=None)

    # Assign the callback to the button
    button.callback = button_callback

    view = discord.ui.View()
    view.add_item(button)
    try:
        await ctx.send(f"Kicking {user.mention}?", view=view)
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="lock", description="lock emoji")
@discord.app_commands.default_permissions(manage_channels=True)
async def lock(ctx: commands.Context):
    perms = ctx.channel.overwrites_for(ctx.guild.default_role)
    perms.send_messages=False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    await log_action(ctx.guild, f"🔒 {ctx.channel.mention} has been locked by {ctx.author.mention}")
    try:
        await ctx.send(f"🔒 {ctx.channel.mention} has been locked by {ctx.author.mention}")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")
@lock.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="unlock", description="key emoji")
@discord.app_commands.default_permissions(manage_channels=True)
async def unlock(ctx: commands.Context):
    perms = ctx.channel.overwrites_for(ctx.guild.default_role)
    perms.send_messages=True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    await log_action(ctx.guild, f"🔓 {ctx.channel.mention} has been unlocked by {ctx.author.mention}")
    try:
        await ctx.send(f"🔓 {ctx.channel.mention} has been unlocked by {ctx.author.mention}")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")
@unlock.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="mute", description="hahah imagine being a mute")
@discord.app_commands.default_permissions(moderate_members=True)
@app_commands.describe(user="your free trial of talking has ended")
@app_commands.describe(lengh="lengh of no yap perms (e.g. 4d)")
@app_commands.describe(reason="i muted you becuz your annoying")
async def mute(ctx: commands.Context, user: discord.User, lengh: str, reason: str):
    clock = convert_time_to_seconds(lengh)
    try:
        await user.timeout(datetime.timedelta(seconds=clock), reason=f"{reason}")
        await log_action(ctx.guild, f"{user.mention} was muted by {ctx.author.mention} for `{reason}`! This mute expires <t:{round(time.time()) + clock}:R>")
        await ctx.send(f"{user.mention} was muted by {ctx.author.mention} for `{reason}`! This mute expires <t:{round(time.time()) + clock}:R>")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")
    try:
        await user.send(f"hello nerd you might have been muted in {ctx.guild.name} for `{reason}`.")
    except Exception as e:
        print(f"Failed to send DM: {e}")
@mute.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="nickname", description="change someone's identity (nickname)")
@discord.app_commands.default_permissions(manage_nicknames=True)
@app_commands.describe(user="who do you want to rename")
@app_commands.describe(new_nickname="their new embarrassing identity")
async def nickname(ctx: commands.Context, user: discord.Member, new_nickname: str):
    old_nickname = user.nick if user.nick else "(no nickname)"
    try:
        await user.edit(nick=new_nickname)
        await log_action(ctx.guild, f"{ctx.author.mention} renamed {user.mention} from `{old_nickname}` to `{new_nickname}`.")
        await ctx.send(f"{ctx.author.mention} renamed {user.mention} to `{new_nickname}`.")
    except discord.Forbidden:
        await ctx.send("cant :skull:")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@nickname.error
async def nickname_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="unmute", description="wtf i can talk")
@discord.app_commands.default_permissions(moderate_members=True)
@app_commands.describe(user="Mods, unmute this person")
@app_commands.describe(reason="why ummute tbh")
async def unmute(ctx: commands.Context, user: discord.User, reason: str):
    try:
        await ctx.send(f"{user.mention} was unmuted by {ctx.author.mention} for `{reason}`.")
        await log_action(ctx.guild, f"{user.mention} was unmuted by {ctx.author.mention} for `{reason}`!")
        await user.timeout(None, reason=f"{reason}")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")
@unmute.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="unban", description="unyeet??")
@discord.app_commands.default_permissions(ban_members=True)
@app_commands.describe(user="the nerd to... unyeet")
@app_commands.describe(reason="why was the user unyeet")
async def unban(ctx: commands.Context, user: discord.User, reason: str = "No reason provided"):
    try:
        await ctx.guild.unban(user, reason=reason)
        await log_action(ctx.guild, f"{user.mention} was unbanned by {ctx.author.mention} for `{reason}`!!!")
        await ctx.send(content=f"{user.mention} was unbanned by {ctx.author.mention} for `{reason}`!!!")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="purge", description="Ooh, live the dream with a time machine")
@discord.app_commands.default_permissions(manage_messages=True)
@app_commands.describe(user="user to purge")
@app_commands.describe(limit="max ammount is 1000")
async def purge(ctx: commands.Context, limit: int, user: discord.User = None):
    # Ensure the limit is within bounds
    limit = max(1, min(limit, 1000))

    # Define a check function to filter messages
    def check(msg):
        return user is None or msg.author == user

    # Perform the bulk delete
    deleted = await ctx.channel.purge(limit=limit, check=check)

    # Send a confirmation message
    try:
        await ctx.send(content=f"Last {len(deleted)} messages{' from ' + user.mention if user else ''} were purged by {ctx.author.mention}.")
        await log_action(ctx.guild, f"Last {len(deleted)} messages{' from ' + user.mention if user else ''} were purged by {ctx.author.mention}.")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="slowmode", description="change the speed of the chat")
@discord.app_commands.default_permissions(manage_channels=True)
@app_commands.describe(slowmode="slowmode time. max is 6 hours you goob, please specifiy unit")
async def slowmode(ctx: commands.Context, slowmode: str):
    delay = convert_time_to_seconds(slowmode)
    try:
        await ctx.channel.edit(slowmode_delay=delay)
        await log_action(ctx.guild, f"{slowmode} slowmode in {ctx.channel.mention} set by {ctx.author.mention}.")
        await ctx.send(f":zzz: Now going at {slowmode} slowmode!")
    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")
@slowmode.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="log", description="set up logging")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(type="what type of logs to set (message/action)")
@app_commands.describe(channel="where the logs go")
async def log(ctx: commands.Context, type: str, channel: discord.TextChannel):
    db = load_db()
    server_id = str(ctx.guild.id)

    if server_id not in db:
        db[server_id] = {}

    if type.lower() == "message":
        db[server_id]["message_log_channel"] = channel.id
        await ctx.send(f"message logs will go to {channel.mention}")
    elif type.lower() == "action":
        db[server_id]["action_log_channel"] = channel.id
        await ctx.send(f"action logs will go to {channel.mention}")
    else:
        await ctx.send("Invalid type! Choose either `message` or `action`.")

    save_db(db)

async def log_action(guild: discord.Guild, content: str):
    db = load_db()
    guild_id = str(guild.id)
    channel_id = db.get(guild_id, {}).get("action_log_channel")
    if channel_id:
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(content, allowed_mentions=discord.AllowedMentions.none())

import aiohttp
import io

@bot.event
async def on_message_delete(message: discord.Message):
    if message.guild is None or message.author.bot:
        return

    db = load_db()
    guild_id = str(message.guild.id)
    channel_id = db.get(guild_id, {}).get("message_log_channel")

    if channel_id:
        channel = message.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(color=discord.Color.from_str("#ff0000"))

            if message.content:
                embed.description = message.content[:4096]

            files = []
            if message.attachments:
                # Attempt to download each attachment
                async with aiohttp.ClientSession() as session:
                    for attachment in message.attachments:
                        try:
                            async with session.get(attachment.url) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    fp = io.BytesIO(data)
                                    fp.seek(0)
                                    files.append(discord.File(fp, filename=attachment.filename))
                        except Exception as e:
                            print(f"Failed to download attachment: {attachment.url} — {e}")

            embed.set_author(name=f"{message.author}'s message was deleted", icon_url=message.author.display_avatar.url)
            embed.set_footer(text=f"#{message.channel.name}")

            await channel.send(embed=embed, files=files, allowed_mentions=discord.AllowedMentions.none())

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.guild is None or before.author.bot or before.content == after.content:
        return

    db = load_db()
    guild_id = str(before.guild.id)
    channel_id = db.get(guild_id, {}).get("message_log_channel")

    if channel_id:
        channel = before.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                color=discord.Color.from_str("#757e8a")
            )
            embed.add_field(name="Before", value=before.content[:1024], inline=False)
            embed.add_field(name="After", value=after.content[:1024], inline=False)
            embed.set_author(name=str(f"{before.author} edited their message"), icon_url=before.author.display_avatar.url)
            embed.set_footer(text=f"#{before.channel.name}")
            await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())


@bot.tree.command(name="starboard", description="where good messages go")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(channel="WHAT !")
@app_commands.describe(emoji=":staring_ctqa:")
@app_commands.describe(threshold="how many people need to care, 0 to delete")
@app_commands.describe(starboard_id="ID for this starboard (1 = default)")
async def setstarboard(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    emoji: str = "⭐",
    threshold: int = 3,
    starboard_id: int = 1
):
    await interaction.response.defer(ephemeral=False)

    db = load_db()
    server_id = str(interaction.guild.id)

    if server_id not in db:
        db[server_id] = {}

    suffix = "" if starboard_id == 1 else f"_{starboard_id}"

    if threshold <= 0:
        # Remove this starboard config
        for key in ["channel_id", "emoji", "threshold", "webhook_url"]:
            db[server_id].pop(f"starboard_{key}{suffix}", None)
        save_db(db)
        await interaction.followup.send(f"❌ Removed starboard {starboard_id}")
        return

    # Set this starboard config
    db[server_id][f"starboard_channel_id{suffix}"] = channel.id
    db[server_id][f"starboard_emoji{suffix}"] = emoji
    db[server_id][f"starboard_threshold{suffix}"] = threshold
    save_db(db)

    await interaction.followup.send(
        f"⭐ Starboard {starboard_id} set to {channel.mention} with emoji {emoji} and threshold {threshold}."
    )

@bot.event
async def on_raw_reaction_add(payload):
    db = load_db()
    server_id = str(payload.guild_id)

    if server_id not in db:
        return

    # Try default starboard and numbered starboards
    starboard_ids = [1] + [int(k.split("_")[-1]) for k in db[server_id] if k.startswith("starboard_channel_id_")]
    starboard_ids = list(set(starboard_ids))  # Avoid duplicates

    for starboard_id in starboard_ids:
        suffix = "" if starboard_id == 1 else f"_{starboard_id}"
        emoji = db[server_id].get(f"starboard_emoji{suffix}")
        threshold = db[server_id].get(f"starboard_threshold{suffix}", 3)
        channel_id = db[server_id].get(f"starboard_channel_id{suffix}")
        webhook_id = db[server_id].get(f"starboard_webhook_id{suffix}")

        if not emoji or not channel_id:
            continue

        if payload.emoji.name != emoji and str(payload.emoji) != emoji:
            continue

        guild = bot.get_guild(payload.guild_id)
        if not guild:
            continue

        channel = guild.get_channel(payload.channel_id)
        if not channel:
            continue

        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if (reaction.emoji == payload.emoji.name or str(reaction.emoji) == emoji) and reaction.count >= threshold:
                async for user in reaction.users():
                    if user.id == bot.user.id:
                        return

                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    pass

                starboard_channel = guild.get_channel(channel_id)
                if not starboard_channel:
                    return

                webhook = None

                # Try to get the existing webhook
                if webhook_id:
                    try:
                        webhooks = await starboard_channel.webhooks()
                        webhook = discord.utils.get(webhooks, id=webhook_id)
                    except (discord.NotFound, discord.Forbidden):
                        webhook = None

                if webhook is None:
                    # Webhook is missing or invalid; create a new one
                    async with aiohttp.ClientSession() as session:
                        async with session.get("https://i.imgur.com/yHPNPoQ.png") as resp:
                            avatar_bytes = await resp.read() if resp.status == 200 else None

                    webhook_obj = await starboard_channel.create_webhook(
                        name="ctqa ploice webhook",
                        avatar=avatar_bytes
                    )
                    webhook_id = webhook_obj.id
                    db[server_id][f"starboard_webhook_id{suffix}"] = webhook_id
                    save_db(db)
                    webhook = webhook_obj


                author_name = f"{message.author.display_name} (#{channel.name})"
                author_name = author_name[:80] if len(author_name) > 80 else author_name
                avatar_url = message.author.avatar.url if message.author.avatar else None

                # Jump button
                jump_url = message.jump_url
                view = View()
                view.add_item(Button(label="Jump to message", url=jump_url))

                files = [await attachment.to_file() for attachment in message.attachments]

                await webhook.send(
                    content=message.content or None,
                    username=author_name,
                    avatar_url=avatar_url,
                    view=view,
                    files=files,
                    wait=True,
                    allowed_mentions=discord.AllowedMentions.none()
                )

@bot.hybrid_command(name="yapping-city", description="Add or remove a forum as a Yapping City forum")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(action="Whether to add or remove the forum", forum="The forum channel to modify")
async def yapping_city(ctx: commands.Context, action: Literal["add", "remove"], forum: discord.ForumChannel):
    db = load_db()
    guild_id = str(ctx.guild.id)
    forum_id = str(forum.id)

    db.setdefault(guild_id, {}).setdefault("yapping_forums", {})

    if action == "add":
        db[guild_id]["yapping_forums"][forum_id] = True
        await ctx.send(f"{ctx.author.mention} set {forum.mention} as a Yapping City forum.", ephemeral=False)
        await log_action(ctx.guild, f"{ctx.author.mention} set {forum.mention} as a Yapping City forum.")
    elif action == "remove":
        if forum_id in db[guild_id]["yapping_forums"]:
            del db[guild_id]["yapping_forums"][forum_id]
            await ctx.send(f"{ctx.author.mention} unset {forum.mention} as a Yapping City forum.", ephemeral=False)
            await log_action(ctx.guild, f"{ctx.author.mention} unset {forum.mention} as a Yapping City forum.")
        else:
            await ctx.send(f"{forum.mention} is not marked as a Yapping City forum, idiot.", ephemeral=False)

    save_db(db)

@bot.hybrid_command(name="dementia-chat", description="Add or remove a channel as a Dementia Chat channel")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(action="Whether to add or remove the channel", channel="The text channel to modify")
async def dementia_chat(ctx: commands.Context, action: Literal["add", "remove"], channel: discord.TextChannel):
    db = load_db()
    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)

    db.setdefault(guild_id, {}).setdefault("dementia_chats", {})

    if action == "add":
        db[guild_id]["dementia_chats"][channel_id] = True
        await ctx.send(f"{ctx.author.mention} set {channel.mention} as a Dementia Chat channel.", ephemeral=False)
        await log_action(ctx.guild, f"{ctx.author.mention} set {channel.mention} as a Dementia Chat channel.")
    elif action == "remove":
        if channel_id in db[guild_id]["dementia_chats"]:
            del db[guild_id]["dementia_chats"][channel_id]
            await ctx.send(f"{ctx.author.mention} unset {channel.mention} as a Dementia Chat channel.", ephemeral=False)
            await log_action(ctx.guild, f"{ctx.author.mention} unset {channel.mention} as a Dementia Chat channel.")
        else:
            await ctx.send(f"{channel.mention} is not marked as a Dementia Chat channel, idiot.", ephemeral=False)

    save_db(db)


@bot.hybrid_command(name="whitelist", description="Allow or remove someone from talking in your Yapping City post")
@app_commands.describe(user="The user to whitelist or remove", remove="Unwhitelist the user instead")
async def whitelist(ctx: commands.Context, user: discord.User, remove: bool = False):
    if not isinstance(ctx.channel, discord.Thread):
        return await ctx.send("You can only run this inside a thread.")

    thread = ctx.channel
    if ctx.author.id != thread.owner_id:
        return await ctx.send("Only the thread owner can manage the whitelist.")

    db = load_db()
    guild_id = str(ctx.guild.id)
    thread_id = str(thread.id)

    db.setdefault(guild_id, {}).setdefault("whitelists", {}).setdefault(thread_id, [])
    whitelist = db[guild_id]["whitelists"][thread_id]

    try:
        if remove:
            if user.id in whitelist:
                whitelist.remove(user.id)
                save_db(db)
                await ctx.send(f"{user.mention} has been removed from the whitelist.")
            else:
                await ctx.send(f"{user.mention} is not on the whitelist.")
        else:
            if user.id not in whitelist:
                whitelist.append(user.id)
                save_db(db)
                await ctx.send(f"{user.mention} can now post in this thread.")
            else:
                await ctx.send(f"{user.mention} is already whitelisted.")
    except discord.HTTPException as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.hybrid_command(name="setmodrole", description="Set a role as a minimod, mod, or admin role for the bot")
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(role_type="What kind of role", role="The role to set")
async def setmodrole(ctx: commands.Context, role_type: Literal["admin", "mod", "minimod", "functional_mod"], role: discord.Role):
    db = load_db()
    guild_id = str(ctx.guild.id)

    db.setdefault(guild_id, {}).setdefault("mod_roles", {})
    db[guild_id]["mod_roles"][role_type] = str(role.id)

    save_db(db)

    await log_action(ctx.guild, f"{ctx.author.mention} set {role.mention} as the `{role_type}` role.")
    await ctx.send(f"{ctx.author.mention} set {role.mention} as the `{role_type}` role.", ephemeral=False)

@bot.hybrid_command(name="setmod", description="Assign or remove a mod or minimod role from a user")
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(user="The user to modify", level="What level to assign", reason="The reason for this action")
async def setmod(ctx: commands.Context, user: discord.Member, level: Literal["mod", "minimod", "not mod"], reason: str = "None"):
    db = load_db()
    guild_id = str(ctx.guild.id)

    if not (
        ctx.author.guild_permissions.manage_guild or
        has_mod_role(ctx.author, "admin")
    ):
        await ctx.send("this message should not appear.", ephemeral=True)
        return

    roles = db.get(guild_id, {}).get("mod_roles", {})
    mod_role = ctx.guild.get_role(int(roles.get("mod"))) if roles.get("mod") else None
    minimod_role = ctx.guild.get_role(int(roles.get("minimod"))) if roles.get("minimod") else None
    functional_mod_role = ctx.guild.get_role(int(roles.get("functional_mod"))) if roles.get("functional_mod") else None

    has_mod = mod_role in user.roles if mod_role else False
    has_minimod = minimod_role in user.roles if minimod_role else False
    has_functional = functional_mod_role in user.roles if functional_mod_role else False

    try:
        to_add = []
        to_remove = []

        if level == "mod":
            if mod_role and not has_mod:
                to_add.append(mod_role)
            if minimod_role and has_minimod:
                to_remove.append(minimod_role)
            if functional_mod_role and not has_functional:
                to_add.append(functional_mod_role)
            status_text = "mod"

        elif level == "minimod":
            if minimod_role and not has_minimod:
                to_add.append(minimod_role)
            if mod_role and has_mod:
                to_remove.append(mod_role)
            if functional_mod_role and not has_functional:
                to_add.append(functional_mod_role)
            status_text = "minimod"

        elif level == "not mod":
            if mod_role and has_mod:
                to_remove.append(mod_role)
            if minimod_role and has_minimod:
                to_remove.append(minimod_role)
            if functional_mod_role and has_functional:
                to_remove.append(functional_mod_role)
            status_text = "not mod"

        # Apply changes
        if to_add:
            await user.add_roles(*to_add, reason=reason)
        if to_remove:
            await user.remove_roles(*to_remove, reason=reason)

        # Logging
        if level == "not mod":
            log_message = f"{user.mention} had their mod removed by {ctx.author.mention} for `{reason}`."
            send_message = f"{user.mention} had their mod removed by {ctx.author.mention} for `{reason}`."
            dm_message = f"hi nerd your mod status was removed in {ctx.guild} for `{reason}`"
        else:
            log_message = f"{user.mention} was made {status_text} by {ctx.author.mention} for `{reason}`."
            send_message = f"{user.mention} was made {status_text} by {ctx.author.mention} for `{reason}`."
            dm_message = f"hi nerd your mod status was changed to {status_text} in {ctx.guild} for `{reason}`"

        await log_action(ctx.guild, log_message)
        await user.send(dm_message)
        await ctx.send(send_message)

    except Exception as e:
        await ctx.channel.send(f"504 internal server error\n-# {e}")

@bot.event
async def on_message(message: discord.Message):
# AI LINE STARTS HERE
    if message.author.id == bot.user.id:
       return
    if any(mention.id == bot.user.id for mention in message.mentions):
        # Start typing indicator
        async with message.channel.typing():
            # Fetch last 10 messages in the channel
            messages = [msg async for msg in message.channel.history(limit=10)]
            message_history = "\n".join([f"{msg.author}: {msg.content}" for msg in messages])

            # Prepare the query with message history
            query = f"You are NeoCat Police. You are a Moderation bot for various discord servers. You are a clone of The Server Cat Stand's \"Cat Police\" bot. You are NOT an \"AI-Powered\" or \"AI Chatbot\" or anything of the like. You're simply an Isolated AI Feature in an otherwise AI-less bot. Please Keep your responces short unless needed. Do not start your message with the bot's username, as it is not needed. Here is more info about the bot: `NeoCat Police` (formerly called ctqa ploice) is a clone of milenakos' (aka Lia's) 'Cat police' bot, specifically for the Discord server Cat Stand. Both bots function very similarly, but with some changes, such as NeoCat Police lacking Cat Bot statistics commands, not being hard coded for Cat Stand, and adding a few more features. NeoCat Police is inspired by tema5002's Cat Bot clone called `ctqa bto`, a clone of Cat Bot written in C# that is no longer online, hence the former name \"ctqa ploice\". NeoCat Police is made by mari2, aka Mari. You are in a discord server called \"{message.guild.name}\", owned by \"{message.guild.owner}\". You are to present as a feminine bot.\n\nHere is the last 10 messages:\n{message_history}\n\nNow, respond to this query from {message.author}:\n{message.content}"
            
            # Get the response from the query
            response = await asyncio.to_thread(query_ollama, query)
            trimmed_response = response[:2000]  # Trim response to the first 2000 characters
            await message.reply(trimmed_response, allowed_mentions=discord.AllowedMentions.none())
    # AI END

    if message.guild is None or message.author.bot:
        return

    db = load_db()
    guild_id = str(message.guild.id)

    # I forgor what this is for
    channel_id = str(message.channel.id)

    # Check if in a Yapping City forum
    yapping_forums = db.get(guild_id, {}).get("yapping_forums", {})
    whitelists = db.get(guild_id, {}).get("whitelists", {})

    if isinstance(message.channel, discord.Thread) and str(message.channel.parent_id) in yapping_forums:
        thread = message.channel
        if message.author.id == thread.owner_id:
            return  # thread creator is allowed
        if str(thread.id) in whitelists and message.author.id in whitelists[str(thread.id)]:
            return  # whitelisted user is allowed

        try:
            # Download attachments first
            files = []
            if message.attachments:
                async with aiohttp.ClientSession() as session:
                    for attachment in message.attachments:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                fp = io.BytesIO(data)
                                fp.seek(0)
                                files.append(discord.File(fp, filename=attachment.filename))

            await message.delete()

            # Build the embed
            embed = discord.Embed(color=discord.Color.from_str("#ff0000"))

            if message.content:
                embed.description = message.content[:4096]

            embed.set_author(name=f"{message.author}'s message was deleted", icon_url=message.author.display_avatar.url)
            embed.set_footer(text=f"#{message.channel.name}")

            thread_owner = await message.guild.fetch_member(thread.owner_id)
            await thread_owner.send(embed=embed, files=files, allowed_mentions=discord.AllowedMentions.none())
        except Exception as e:
            print(f"Error deleting message or sending DM: {e}")

    # Check if it's a dementia chat channel
    if db.get(guild_id, {}).get("dementia_chats", {}).get(channel_id):
        # Fetch recent messages
        messages = [msg async for msg in message.channel.history(limit=100, oldest_first=True)]
        if len(messages) > 7:
            # How many to delete?
            to_delete = len(messages) - 7
            delete_msgs = messages[:to_delete]

            try:
                await message.channel.delete_messages(delete_msgs)
            except discord.HTTPException:
                # If bulk delete fails (too old?), delete one by one
                for msg in delete_msgs:
                    try:
                        await msg.delete()
                    except Exception:
                        pass  # Ignore failures

    await bot.process_commands(message)

bot.run("YOUR TOKEN HERE")
