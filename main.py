import discord
import asyncio
from discord.ext import commands
import os
from discord_slash import SlashCommand
import json

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash=SlashCommand(bot, sync_commands=True)
bot.remove_command("help")

@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('---------------------------------------')
    print('Bot running.')


async def status_task():
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(set(bot.users))} user | {len(bot.guilds)} Server🌍"))

with open("ban.json", "r")as f:
  banned=json.load(f)
with open("servers.json", "r")as f:
  servers=json.load(f)

@bot.event
async def on_message(message):
    with open("ban.json", "r")as f:
      banned=json.load(f)
    if message.author.bot:
        return
    if message.author.id in banned["Banned"]:
      await message.delete()
      embed=discord.Embed(title=f"{message.author}, Du bist aus dem Chat leider gebannt!", color=0x5adcf3)
      hinweis=await message.channel.send(embed=embed)
      await asyncio.sleep(5)
      await hinweis.delete()
      return
    if get_globalChat(message.guild.id, message.channel.id, ):
        await sendAll(message)
    await bot.process_commands(message)


if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)


@slash.slash(name="addGlobal", description="Add the Global chat into this channel")
async def addGlobal(ctx, tee="None"):
    if ctx.author.guild_permissions.administrator:
      with open("servers.json", "r")as f:
        servers=json.load(f)
        if not guild_exists(ctx.guild.id):
            if not tee.startswith("<#"):
              server = {
                  "guildid": ctx.guild.id,
                  "channelid": ctx.channel.id,
                  "invite": f'{(await ctx.channel.create_invite()).url}'
              }
            else:
              tee=tee.replace("<#", "")
              tee=tee.replace(">", "")
              server = {
                  "guildid": ctx.guild.id,
                  "channelid": tee,
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
            await ctx.send(embed=embed)
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
            await ctx.send(embed=embed)


@slash.slash(name="removeGlobal", description="Remove the Global chat from this channel")
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
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="ERROR", description="You still got no Global Chat.\r\n"
                                                             f"\n`addGlobal` zum hinzufügen, des GlobalChats🌍",
                                  color=0x5adcf3)
            await ctx.send(embed=embed)

@slash.slash(name="ban", description="Ban a user from Global Chat")
async def ban(ctx, member: discord.Member, reason=None):
      if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
          embed=discord.Embed(title="Error", description="Your Server got no Global Chat!", color=0x5adcf3)
          await ctx.send(embed=embed, hidden=True)
          return
        with open("ban.json", "r")as f:
            banned=json.load(f)
        if ctx.author.id==member.id:
            embed=discord.Embed(title="Error", description="You cant ban yourself!", color=0x5adcf3)
            await ctx.send(embed=embed, hidden=True)
            return
        if ctx.author.id in banned["Banned"]:
            embed=discord.Embed(title="Error", description="You can ban yourself because you are banned too!", color=0x5adcf3)
            await ctx.send(embed=embed, hidden=True)
            return
        if member.id in banned["Banned"]:
          embed=discord.Embed(title="Error", description="This User is already banned!", color=0x5adcf3)
          await ctx.send(embed=embed, hidden=True)
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
          await ctx.send(embed=discord.Embed(title="Ban Successfull", color=0x5adcf3), hidden=True)
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
          await ctx.send(embed=discord.Embed(title="Ban Successfull", color=0x5adcf3), hidden=True)
          embed=discord.Embed(title="You are banned from Global chat", color=0x5adcf3)
          embed.add_field(name="Banned by:", value=f"{ctx.author.mention}")
          embed.add_field(name="Server:", value=f"{ctx.guild.name}")
          await member.send(embed=embed)


@slash.slash(name="unban", description="Unban a user from Global Chat")
async def unban(ctx, member: discord.Member):
      if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
          embed=discord.Embed(title="Error", description="Your Server got no Global Chat!", color=0x5adcf3)
          await ctx.send(embed=embed, hidden=True)
          return
        with open("ban.json", "r")as f:
            banned=json.load(f)
        if ctx.author.id==member.id:
            embed=discord.Embed(title="Error", description="You cant unban yourself!", color=0x5adcf3)
            await ctx.send(embed=embed, hidden=True)
            return
        if ctx.author.id in banned["Banned"]:
            embed=discord.Embed(title="Error", description="You can unban yourself because you are banned too!", color=0x5adcf3)
            await ctx.send(embed=embed, hidden=True)
            return
        if not member.id in banned["Banned"]:
          embed=discord.Embed(title="Error", description="This User is not banned!", color=0x5adcf3)
          await ctx.send(embed=embed, hidden=True)
          return
        search=banned["Banned"].index(member.id)
        banned["Banned"].pop(search)
        with open('ban.json', 'w') as f:
              json.dump(banned, f, indent=4)
        embed=discord.Embed(title="Ban", description="Unban erfolgreich", color=0x5adcf3)
        embed.add_field(name="User:", value=f"{member.mention}")
        embed.add_field(name="Unbanned by:", value=f"{ctx.author.mention}")
        embed.add_field(name="Server:", value=f"{ctx.guild.name}")
        await ctx.send(embed=discord.Embed(title="Unban Successfull", color=0x5adcf3), hidden=True)
        await sendAll(embed=embed)
        embed=discord.Embed(title="You are unbanned from Global chat", color=0x5adcf3)
        embed.add_field(name="Unbanned by:", value=f"{ctx.author.mention}")
        embed.add_field(name="Server:", value=f"{ctx.guild.name}")
        await member.send(embed=embed)


@slash.slash(name="servers", description="See Server using Global Chat")
async def servers(ctx, number=None):
  if number==None:
    number=10
  if int(number)>=30:
    number=30
  x=0
  embed=discord.Embed(title="Servers", color=0x5adcf3)
  for guild in bot.guilds:
    embed.add_field(name=f"{guild.name}", value=f"{len(guild.members)} User")
    x+=1
    if x==int(number):
      await ctx.send(embed=embed, hidden=True)
      return
  if x==int(number):
    x=0
  else:
    await ctx.send(embed=embed, hidden=True)




async def sendAll(message: discord.Message = None, embed: discord.Embed = None):
    with open("servers.json", "r")as f:
      servers=json.load(f)
    if message:
        content = message.content
        author = message.author
        attachments = message.attachments
        msg_embed = discord.Embed(description=content, color=author.color)

        icon = author.avatar_url
        if message.author.id ==874349035312537661:
            msg_embed.set_author(name=author.name + "│🛡 Moderator", icon_url=icon)
        elif message.author.id ==775432882474450965:
            msg_embed.set_author(name=author.name + "│🜲 Inhaber", icon_url=icon)

        else:
            msg_embed.set_author(name=author.name, icon_url=icon)
        icon_url = "https://i.giphy.com/media/xT1XGzYCdltvOd9r4k/source.gif"
        icon = message.guild.icon_url
        if icon:
            icon_url = icon
        msg_embed.set_thumbnail(url=icon_url)
        member = 0
        bots = 0
        guild = bot.get_guild(message.guild.id)
        for m in guild.members:
            member += 1
            if m.bot:
                bots += 1
        msg_embed.set_footer(text=f'Gesendet von: {message.guild.name}  👤 {member} - 🤖 {bots}', icon_url=icon_url)
        links = '[🤖Invite Bot](https://discord.com/api/oauth2/authorize?client_id=939628984457633804&permissions=8&scope=bot%20applications.commands) | '
        globalchat = get_globalChat(message.guild.id, message.channel.id)
        if len(globalchat["invite"]) > 0:
            invite = globalchat["invite"]
            if 'discord.gg' not in invite:
                invite = f'https://discord.gg/FjD4uvHYKH{invite}'
            links += f'[🚨Server Support]({invite})'
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
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                perms: Permissions = channel.permissions_for(guild.me)
                if perms.send_messages:
                    if perms.embed_links and perms.attach_files and perms.external_emojis:
                        await channel.send(embed=msg_embed)
                    else:
                        await channel.send('{0}: {1}'.format(author.name, content))
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

@slash.slash(name="help", description="Get all commands from Bot")
async def help(ctx):
  embed=discord.Embed(title="Help", color=0x5adcf3)
  embed.add_field(name="Commands:", value="```/addGlobal - Hinzufüge einen Gobal chat in einen channel\n/removeGlobal - Entferne einen Global Chat von deinen Server\n/ban - Banne membe r vom Global Chat\n/unban - Unban einen Member vom Global chat\n/servers - Siehe alle server in den Der Bot drauf ist.```")
  await ctx.send(embed=embed, hidden=True)


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
