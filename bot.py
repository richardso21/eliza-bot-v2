import discord
from discord.ext import commands

TOKEN = 'NzQ2Mzk5ODgzODAzNjIzNTA0.Xz_xDw.CmbVbarP0SYdzqhROfhvjdWEmpo'
CHANNEL = None

bot = commands.Bot(command_prefix='$')

# @bot.command(name='test')
# async def test(ctx):
#     await ctx.send('lol')

# def genStr(string):


@bot.command(name='cd')
async def changeChannel(context, channel_name: str):
    guild = context.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        await context.send("```ERROR: voice channel isn't found (probably misspelled :p) ```")
        return
    elif type(existing_channel) != discord.channel.VoiceChannel:
        await context.send("```ERROR: this is not a voice channel!```")
        return
    CHANNEL = existing_channel
    await context.send("channel found!")

@bot.command(name='attendence')
async def channelAttendence(context):
    if not CHANNEL:
        await context.send("```ERROR: no channel currently selected```")
        return
    await context.send(f"Fetching attendence for {CHANNEL}")


bot.run(TOKEN)