import os
import json
import asyncio
from typing import Union, Dict, Any, Optional

import discord
from discord.ext import commands

with open("ban.json") as f:
  banned = json.load(f)

if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all(), sync_commands=True)
bot.remove_command("help")
bot_invite = discord.utils.oauth_url(str(bot.app.id), permissions=discord.Permissions().all_channel(), scopes=('bot', 'application.commands'))

@bot.event
async def on_ready():
    if not hasattr(bot, '_status_task'):
        bot.loop.create_task(status_task())
        print('started status-task')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('---------------------------------------')
    print('Bot running.')


async def status_task():
    while True:
        name = f"{len(set(bot.users))} user | {len(bot.guilds)} Server🌍"
        if name != bot.activity.name:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=name))
        await asyncio.sleep(15)

@bot.event
async def on_message(message):
    with open("ban.json", "r")as f:
        banned = json.load(f)
    if message.author.bot or not message.guild:
        return
    global_chat = get_globalChat(message.guild.id, message.channel.id)
    if global_chat:
        if message.author.id in banned["Banned"]:
            await message.delete()
            embed = discord.Embed(title=f"{message.author}, Du bist aus dem Chat leider gebannt!", color=0x5adcf3)
            await message.channel.send(embed=embed, delete_after=5)
        else:
            await sendAll(message)
    await bot.process_commands(message)


@bot.slash_command(name="add-global",
                   description="Add the Global chat into this channel",
                   options=[
                       discord.SlashCommandOption(
                           'channel',
                           discord.TextChannel,
                           'The channel to use for the global chat',
                           requiered=False
                       )
                   ])
async def add_global(ctx, channel: Optional[discord.TextChannel] = None):
    if ctx.author.guild_permissions.administrator:
      with open("servers.json", "r")as f:
        servers=json.load(f)
        if not guild_exists(ctx.guild.id):
            if not channel:
              server = {
                  "guildid": ctx.guild.id,
                  "channelid": ctx.channel.id,
                  "invite": f'{(await ctx.channel.create_invite()).url}'
              }
            else:
              server = {
                  "guildid": ctx.guild.id,
                  "channelid": channel.id,
                  "invite": f'{(await ctx.channel.create_invite()).url}'
              }
            servers["servers"].append(server)
            with open('servers.json', 'w') as f:
                json.dump(servers, f, indent=4)
            embed = discord.Embed(title="**Willkomme im Global chat™**",
                                  description="Du kannst jetzt denn Chat nutzen."
                                              " Jede Nachricht, die Sie in diesen Kanal schreiben, ist öffentlich"
                                              " auf einem anderen Server!", color=0x5adcf3)
            embed.set_footer(text='Im Globalmode soll es ab 5 Sek. einen Slowmode geben')
            await ctx.respond(embed=embed)
            member = 0
            bot = 0
            for i in ctx.guild.members:
                member += 1
                if i.bot:
                    bot += 1
            embed = discord.Embed(title=f"**WILLKOMMEN**\r\n \r\n", color=0x5adcf3)
            embed.add_field(name=f"**{ctx.guild}** joined",
                            value=f"**{member}** Members und **{bot}** Bots")
            embed.add_field(name="AUFMERKSAMKEIT",
                            value=f"```Wenn Sie eine Nachricht mit einem Präfix beginnen, wird es nicht in denn globalen chat\r\n Geschrieben Für Ein Test: hey```")
            embed.set_footer(text=f'Remove the Global Chat with removeGlobal')
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f'Global added by {ctx.author}', icon_url=ctx.author.avatar_url)
            await sendAll(embed=embed)
        else:
            embed = discord.Embed(title="ERROR", description="You always got an Global Chat.\r\n"
                                                             "Every Server can only got one Global Chat.",
                                  color=0x5adcf3)
            await ctx.respond(embed=embed)


@bot.slash_command(name="removeGlobal", description="Remove the Global chat from this channel")
async def removeGlobal(ctx):
      if ctx.author.guild_permissions.administrator:
        with open("servers.json", "r")as f:
          servers=json.load(f)
        if guild_exists(ctx.guild.id):
            globalid = get_globalChat_id(ctx.guild.id)
            if globalid != -1:
                servers["servers"].pop(globalid)
                with open('servers.json', 'w') as f:
                    json.dump(servers, f, indent=4)
            member = 0
            bot = 0
            for i in ctx.guild.members:
                member += 1
                if i.bot:
                    bot += 1
            embed = discord.Embed(title=f"**Bye <:VA_CatDed:939450167411765288>**\r\n \r\n", color=0x5adcf3)
            embed.add_field(name="We lost an Server!",
                            value=f"Now **{ctx.guild}** leaved our little chat with **{member}** 👦 Members and **{bot}** 🤖 Bots")
            embed.set_footer(text=f'For Feedback, Text GrinderHood#2624')
            await sendAll(embed=embed)
            embed = discord.Embed(title="See Ya!",
                                  description="Du hast denn Global Chat, entfernt"
                                              f" `addGlobal` zum hinzufügen⚙", color=0x5adcf3)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="ERROR", description="You still got no Global Chat.\r\n"
                                                             f"\n`addGlobal` zum hinzufügen, des GlobalChats🌍",
                                  color=0x5adcf3)
            await ctx.respond(embed=embed)

@bot.slash_command(name="ban", description="Ban a user from Global Chat")
async def ban(ctx, member: discord.Member, reason=None):
      if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
          embed=discord.Embed(title="Error", description="Your Server got no Global Chat!", color=0x5adcf3)
          await ctx.respond(embed=embed, hidden=True)
          return
        with open("ban.json", "r")as f:
            banned=json.load(f)
        if ctx.author.id==member.id:
            embed=discord.Embed(title="Error", description="You cant ban yourself!", color=0x5adcf3)
            await ctx.respond(embed=embed, hidden=True)
            return
        if ctx.author.id in banned["Banned"]:
            embed=discord.Embed(title="Error", description="You can ban yourself because you are banned too!", color=0x5adcf3)
            await ctx.respond(embed=embed, hidden=True)
            return
        if member.id in banned["Banned"]:
          embed=discord.Embed(title="Error", description="This User is already banned!", color=0x5adcf3)
          await ctx.respond(embed=embed, hidden=True)
          return
        banned["Banned"].append(member.id)
        with open('ban.json', 'w') as f:
              json.dump(banned, f, indent=4)
        if reason:  
          embed=discord.Embed(title="Ban", description="Ban erfolgreich", color=0x5adcf3)
          embed.add_field(name="User:", value=f"{member.mention}")
          embed.add_field(name="Banned by:", value=f"{ctx.author.mention}")
          embed.add_field(name="Server:", value=f"{ctx.guild.name}")
          embed.add_field(name="Reason:", value=f"```{reason}```")
          await sendAll(embed=embed)
          await ctx.respond(embed=discord.Embed(title="Ban Successfull", color=0x5adcf3), hidden=True)
          embed=discord.Embed(title="You are banned from Global chat", color=0x5adcf3)
          embed.add_field(name="Banned by:", value=f"{ctx.author.mention}")
          embed.add_field(name="Server:", value=f"{ctx.guild.name}")
          embed.add_field(name="Reason:", value=f"```{reason}```")
          await member.send(embed=embed)
        else:
          embed=discord.Embed(title="Ban", description="Ban erfolgreich", color=0x5adcf3)
          embed.add_field(name="User:", value=f"{member.mention}")
          embed.add_field(name="Banned by:", value=f"{ctx.author.mention}")
          embed.add_field(name="Server:", value=f"{ctx.guild.name}")
          await sendAll(embed=embed)
          await ctx.respond(embed=discord.Embed(title="Ban Successfull", color=0x5adcf3), hidden=True)
          embed=discord.Embed(title="You are banned from Global chat", color=0x5adcf3)
          embed.add_field(name="Banned by:", value=f"{ctx.author.mention}")
          embed.add_field(name="Server:", value=f"{ctx.guild.name}")
          await member.send(embed=embed)


@bot.slash_command(name="unban", description="Unban a user from Global Chat")
async def unban(ctx, member: discord.Member):
      if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
          embed=discord.Embed(title="Error", description="Your Server got no Global Chat!", color=0x5adcf3)
          await ctx.respond(embed=embed, hidden=True)
          return
        with open("ban.json", "r")as f:
            banned=json.load(f)
        if ctx.author.id==member.id:
            embed=discord.Embed(title="Error", description="You cant unban yourself!", color=0x5adcf3)
            await ctx.respond(embed=embed, hidden=True)
            return
        if ctx.author.id in banned["Banned"]:
            embed=discord.Embed(title="Error", description="You can unban yourself because you are banned too!", color=0x5adcf3)
            await ctx.respond(embed=embed, hidden=True)
            return
        if not member.id in banned["Banned"]:
          embed=discord.Embed(title="Error", description="This User is not banned!", color=0x5adcf3)
          await ctx.respond(embed=embed, hidden=True)
          return
        search=banned["Banned"].index(member.id)
        banned["Banned"].pop(search)
        with open('ban.json', 'w') as f:
              json.dump(banned, f, indent=4)
        embed=discord.Embed(title="Ban", description="Unban erfolgreich", color=0x5adcf3)
        embed.add_field(name="User:", value=f"{member.mention}")
        embed.add_field(name="Unbanned by:", value=f"{ctx.author.mention}")
        embed.add_field(name="Server:", value=f"{ctx.guild.name}")
        await ctx.respond(embed=discord.Embed(title="Unban Successfull", color=0x5adcf3), hidden=True)
        await sendAll(embed=embed)
        embed=discord.Embed(title="You are unbanned from Global chat", color=0x5adcf3)
        embed.add_field(name="Unbanned by:", value=f"{ctx.author.mention}")
        embed.add_field(name="Server:", value=f"{ctx.guild.name}")
        await member.send(embed=embed)


@bot.slash_command(name="servers",
                   description="See Server using Global Chat",
                   options=[
                       discord.SlashCommandOption(
                           'show',
                           int,
                           'How many servers should be shown on a page',
                           min_value=10,
                           max_value=30,
                           required=False
                       )
                   ])
async def servers(ctx: discord.ApplicationCommandInteraction, number: int = 10):
    start = 0  # TODO: Add option for this later
    stop = start + number
    embed = discord.Embed(title="Servers", description=f'Total `{len(bot.guilds)}`', color=0x5adcf3)
    for guild in bot.guilds[start:stop]:
        embed.add_field(name=f"{guild.name}", value=f"{len(guild.members)} Members")
    await ctx.respond(embed=embed, hidden=True)


async def sendAll(message: Union[discord.Message, discord.Embed], embed: discord.Embed = None):
    with open("servers.json", "r") as f:
        servers: Dict[str, Any] = json.load(f)
    if isinstance(message, discord.Message):
        guild = message.guild # Speedup attribute access

        content = message.content
        author = message.author
        attachments = message.attachments
        msg_embed = discord.Embed(description=content, color=author.color)
        icon = author.avatar_url

        if author.id in bot.owner_ids:
            msg_embed.set_author(name=f'{author.name}│🛡 Moderator', url=f'https://discord.com/users/{author.id}', icon_url=icon)
        elif is_global_moderator(message.author.id): # type: ignore # TODO: Implement this
            msg_embed.set_author(name=f'{author.name} │🜲 Inhaber', url=f'https://discord.com/users/{author.id}', icon_url=icon)
        else:
            msg_embed.set_author(name=author.name, url=f'https://discord.com/users/{author.id}', icon_url=icon)
        icon_url = guild.icon_url or "https://i.giphy.com/media/xT1XGzYCdltvOd9r4k/source.gif"
        msg_embed.set_thumbnail(url=icon_url)

        member_count = 0
        bot_count = 0
        for m in guild.members:  # Using this single iteration instead of two list-comprehensions because its faster
            if m.bot:
                bot_count += 1
            else:
                member_count += 1

        msg_embed.set_footer(text=f'Gesendet von: {guild.name}  👤 {member_count} - 🤖 {bot_count}', icon_url=icon_url)
        links = f'[🤖Invite Bot]({bot_invite})'
        globalchat = get_globalChat(guild.id, message.channel.id)
        invite = globalchat.get("invite", None)
        if invite:
            if 'discord.gg' not in invite:
                invite = f'https://discord.gg/{invite}'
            links += f'[🚨Server]({invite})'
        msg_embed.add_field(name='Bot Invite und Support', value=links, inline=False)

        if len(attachments) > 0:
            for a in attachments:
                if a.url.endswith(('.png', '.jpg', '.gif')) or a.url.startswith(("https://tenor.com/")):
                    msg_embed.set_image(url=a.url)
                    break
        await message.delete()
    else:
        msg_embed = embed
    for server in servers["servers"]:
        guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel = guild.get_channel(int(server["channelid"]))
            if channel:
                perms = channel.permissions_for(guild.me)
                if perms.send_messages:
                    if perms.embed_links and perms.attach_files and perms.external_emojis:
                        await channel.send(embed=msg_embed)
                    else:
                        if isinstance(message, discord.Message):
                            await channel.send(f'{author.mention}: {content}') # type: ignore
                        await channel.send('We are missing some Permissions. '
                                           '`Send messages` `get links` `get Data`'
                                           '`using external Emojis`')


def guild_exists(guildid):
    with open("servers.json", "r")as f:
      servers=json.load(f)
    for server in servers['servers']:
        if int(server['guildid'] == int(guildid)):
            return True
    return False


def get_globalChat(guild_id, channelid=None):
    with open("servers.json", "r")as f:
      servers=json.load(f)
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            if channelid:
                if int(server["channelid"]) == int(channelid):
                    return server
                return
            else:
                return server


def get_globalChat_id(guild_id):
    with open("servers.json", "r")as f:
      servers=json.load(f)
    globalChat = -1
    i = 0
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            globalChat = i
        i += 1
    return globalChat


#-----------------------------------------------------------#

@bot.slash_command(name="help", description="Get all commands from Bot")
async def help(ctx):
  embed=discord.Embed(title="Help", color=0x5adcf3)
  embed.add_field(name="Commands:", value="```/addGlobal - Hinzufüge einen Gobal chat in einen channel\n/removeGlobal - Entferne einen Global Chat von deinen Server\n/ban - Banne membe r vom Global Chat\n/unban - Unban einen Member vom Global chat\n/servers - Siehe alle server in den Der Bot drauf ist.```")
  await ctx.respond(embed=embed, hidden=True)


@bot.event
async def on_guild_join(guild):
    members = guild.member_count
    if members <= 5:
        embed = discord.Embed(title="Error", color=0x5adcf3)
        embed.add_field(name="You cant add this Bot now",
                        value="Leider hat Ihr Server nicht die \nerforderliche Anzahl an Mitgliedern, um diesen Bot \nhinzufügen zu können. \nVersuchen Sie es einfach erneut, wenn Sie mindestens **4 Mitglieder** \n auf Ihrem Server haben: [Invite Link](https://discord.com/api/oauth2/authorize?client_id=939628984457633804&permissions=8&scope=bot%20applications.commands)")
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/706132176378527755/824707773887021066/3ad09d4905511990cccc98d904bd1e94_w200.gif")
        embed.set_footer(text="Dieses Limit wurde festgelegt, um gefälschte Einladungen zu vermeiden!")
        await guild.owner.send(embed=embed)
        await guild.leave()
        return

bot.run("YOUR TOKEN HERE")
