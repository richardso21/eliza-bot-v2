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
        await context.send("```ERROR: voice channel isn't found (probably misspelled :p) ```")
        return
    elif type(existing_channel) != discord.channel.VoiceChannel:
        await context.send("```ERROR: this is not a voice channel!```")
        return
    bot.channel = existing_channel.name
    await context.send("channel found!")

@bot.command(name='attendence')
async def channelAttendence(context):
    if not bot.channel:
        await context.send("```ERROR: no channel currently selected```")
        return
    await context.send(f"Fetching attendence for {bot.channel}")

# @bot.event()

bot.run(TOKEN)