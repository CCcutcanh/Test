import json
import os
from datetime import datetime
import asyncio
import discord
import pytz
from discord import Message, Guild, TextChannel, Permissions
from discord.ext import commands

bot = commands.Bot(command_prefix='^', intents=discord.Intents.all())

if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)

async def UpdateMemberCount():
    while True:
        usercount = len(list(filter(lambda m: m.bot == False, bot.users)))
        await bot.change_presence(activity=discord.Game(f'🌎 | bot trên {len(bot.guilds)} Server'))
        await asyncio.sleep(50)

@bot.event
async def on_ready():
    print(f'{bot.user} ist nun online!')
    print(f'{bot.user.id}')
    await bot.loop.create_task(UpdateMemberCount())


@bot.command()
async def ketnoi(ctx):
    if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
            server = {
                "guildid": ctx.guild.id,
                "channelid": ctx.channel.id,
                "invite": f'{(await ctx.channel.create_invite()).url}'
            }
            servers["servers"].append(server)
            with open('servers.json', 'w') as f:
                json.dump(servers, f, indent=4)
            embed = discord.Embed(title="**Cảm Ơn đã sử dụng dịch vụ globalchat của chúng tôi**",
                                  description=" Máy chủ của bạn đã sẵn sàng để sử dụng!"
                                              " Từ giờ trở đi, tất cả các tin nhắn trong kênh này sẽ được gửi trực tiếp cho mọi người"
                                                                              " đã chuyển tiếp đến một máy chủ khác!",
                                  color=0x2ecc71)
            embed.set_footer(text='Xin lưu ý rằng trong GlobalChat luôn có chế độ chậm ít nhất 5 giây'
                                  ' Tin nhắn từ bot.')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="Bạn đã có GlobalChat trên máy chủ của mình.\r\n"
                                              "Xin lưu ý rằng mỗi máy chủ chỉ có thể có một GlobalChat",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)
             #ctx.channel.edit(slowmode_delay=5)

#huyketnoi đang lỗi

@bot.command()
async def huyketnoi(ctx):
    if ctx.member.guild_permissions.administrator:
        if guild_exists(ctx.guild.id):
            globalid = get_globalChat_id(ctx.guild.id)
            if globalid != -1:
                servers["servers"].pop(globalid)
                with open('servers.json', 'w') as f:
                    json.dump(servers, f, indent=4)
            embed = discord.Embed(title="**Tạm Biệt Bạn Đã Rời Khỏi Tính Năng chat Toàn Cầu**",
                                  description="bây giờ các tin nhắn của toàn bộ servers đều sẽ không còn gởi ở đâu nữa!"
                                              " `^ketnoi` dùng lệnh này để kết nối",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="Bạn chưa có GlobalChat trên máy chủ của mình.\r\n"
                                              "Thêm một kênh có `^ketnoi` vào một kênh mới.",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)


#########################################

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.content.startswith('!'):
        if get_globalChat(message.guild.id, message.channel.id):
            await sendAll(message)
    await bot.process_commands(message)


#########################################

async def sendAll(message: Message):
    conent = message.content
    author = message.author
    attachments = message.attachments
    de = pytz.timezone('Europe/Berlin')
    embed = discord.Embed(description=conent, timestamp=datetime.now().astimezone(tz=de), color=author.color)

    user = bot.user.display_avatar.url
    icon = message.guild.icon.url
    embed.set_author(name=author.name, icon_url=icon)

    icon_url = "https://images-ext-1.discordapp.net/external/UhuF1jw07zSR1onvtJ3vs1xxctys7s5gsFTjUdPdmcM/%3Fsize%3D1024/https/cdn.discordapp.com/icons/793403717859803156/1f7ed4541dfbafe1f3d4f3a11aa5c454.webp?width=178&height=178"
    if icon:
        icon_url = icon
    embed.set_thumbnail(url=icon_url)
    embed.set_footer(
        text=f'{message.guild.name} | Servers Hiện Tại: {message.guild.member_count}',
        icon_url=f'{message.guild.icon.url}')
    embed.set_thumbnail(url=message.author.display_avatar.url)
    embed.add_field(name="** **", value="`📌`[Support](https://discord.gg/ens)・`🤖`[Bot-Invite](https://discord.com/api/oauth2/authorize?client_id=626889262&permissions=8&scope=bot%20applications.commands)", inline=False)
    


    if len(attachments) > 0:
        img = attachments[0]
        embed.set_image(url=img.url)

    for server in servers["servers"]:
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                perms: Permissions = channel.permissions_for(guild.get_member(bot.user.id))
                if perms.send_messages:
                    if perms.embed_links and perms.attach_files and perms.external_emojis:
                        await channel.send(embed=embed)
                    else:
                        await channel.send('{0}: {1}'.format(author.name, conent))
                        await channel.send('Một số quyền bị thiếu '
                                           '`Gửi tin nhắn` `Nhúng liên kết` `Đính kèm tệp`'
                                           '`Sử dụng biểu tượng cảm xúc bên ngoài servers`')
    await message.delete()
async def sendAllWillkommen(ctx):
    embed = discord.Embed(
        title=f"Chào mừng!",
        description=f'Máy chủ {ctx.guild.name} hiện đã thêm bot!',
        color=0x662a85,
        timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f'{ctx.guild.name} | {ctx.guild.member_count} User',
                     icon_url=f'{ctx.guild.icon_url}')
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.add_field(name=f'⠀', value='⠀', inline=False)
    embed.add_field(
        name=f'Support & Bot⠀',
        value=
        f'[Support](https://discord.gg/)・[Bot invite](https://discord.com/api/oauth2/authorize?client_id=&permissions=8&scope=bot%20applications.commands)',
        inline=False)

    for server in servers["servers"]:
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                await channel.send(embed=embed)
    await ctx.message.delete()


def guild_exists(guildid):
    for server in servers['servers']:
        if int(server['guildid'] == int(guildid)):
            return True
    return False


def get_globalChat(guild_id, channelid=None):
    globalChat = None
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            if channelid:
                if int(server["channelid"]) == int(channelid):
                    globalChat = server
            else:
                globalChat = server
    return globalChat


def get_globalChat_id(guild_id):
    globalChat = -1
    i = 0
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            globalChat = i
        i += 1
    return globalChat



@bot.event
async def on_guild_join(guild):
    print(f'Máy chủ {ctx.guild.name} hiện đã thêm bot!')
    channel = bot.get_channel(922468435802337341)
    if channel:
        embed = discord.Embed(
            title='Bot !',
            description=
            f'Server Name: {guild.name}\nTên Servers: {guild.id}\Id Servers: {guild.member_count}\n\n**Số lượng người dùng: {len(bot.guilds)}**'
        )
        embed.set_thumbnail(url=f'{guild.icon_url}')
        await channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    print(f'Máy Chủ {guild.name} đã xóa bot!')
    channel = bot.get_channel(896459432001671200)
    if channel:
        embed = discord.Embed(
            title='Bot được xóa trên máy chủ!',
            description=
            f'Server Name: {guild.name}\n Tên servers: {guild.id}\nId máy chủ: {guild.member_count}\n\n*Số lượng members: {len(bot.guilds)}**'
        )
        embed.set_thumbnail(url=f'{guild.icon_url}')
        await channel.send(embed=embed)

@bot.command()
async def invite(ctx):
    embed=discord.Embed(title="\nInvite\n", url="https://discord.com/api/oauth2/authorize?client_id=53626889288&permissions=8&scope=bot%20applications.commands",color=0x662a85)
    await ctx.send(embed=embed)

@bot.command(name='support', aliases=['ss'])
async def support(ctx):
		
		embed = discord.Embed(
				title = f'Link <:Clyde_Bot:868384930147749910>',
				description = '**[Support server](https://discord.gg/...)**',
				color=0x662a85)
		await ctx.send(embed=embed)
        
        
        
@bot.command(aliases=['av'])
async def avatar(ctx, user: discord.Member = None):
    if not user:
        user = ctx.message.author
        embed = discord.Embed()
        embed.set_image(url=user.avatar_url)
        embed.set_footer(text=f'Avatar Của {user}')
        await ctx.channel.send(embed=embed)

bot.run('Token')
