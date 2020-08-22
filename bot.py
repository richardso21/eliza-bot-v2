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
async def changeChannel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        await ctx.send("```ERROR: wrong channel argument```")
        return
    await ctx.send("channel found!")
    print(existing_channel)
    CHANNEL = existing_channel

bot.run(TOKEN)