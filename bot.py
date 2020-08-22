import discord
from discord.ext import commands

TOKEN = 'NzQ2Mzk5ODgzODAzNjIzNTA0.Xz_xDw.CmbVbarP0SYdzqhROfhvjdWEmpo'

bot = commands.Bot(command_prefix='$')

bot.channel = None

@bot.command(name='cd')
async def changeChannel(context, channel_name: str):
    guild = context.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        await context.send("```ml\nERROR: voice channel isn't found (probably misspelled :p) ```")
        return
    elif type(existing_channel) != discord.channel.VoiceChannel:
        await context.send("```ml\nERROR: this is not a voice channel!```")
        return
    bot.channel = existing_channel
    await context.send("channel found!")

@bot.command(name='attendence')
async def channelAttendence(context):
    if not bot.channel:
        await context.send("```ml\nERROR: no channel currently selected```")
        return
    await context.send(f'```ml\nfetching attendence for "{[i.name for i in bot.channel.members]}"```')

# @bot.event()

bot.run(TOKEN)