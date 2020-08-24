import discord
import os
from discord.ext.commands import Bot

TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(command_prefix='$')

bot.selected_channel = None
bot.bot_channel = None
bot.absents = None


# >>> HELPERS >>>
async def errorString(context, e):
    # used to output errors
    await context.send(f'```ml\nERROR: "{e}"```')


async def infoString(context, msg):
    # used to output any input
    await context.send(f'```ml\n{msg}```')


def genList(itr):
    # used to generate a spaced string from an interable
    txt = ''
    for i in itr:
        txt += f' - \"{i}\"\n'
    return txt
# <<< HELPERS <<<


@bot.event
async def on_ready():
    # change bot activity to "Watching Hamilton" :P
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name='Hamilton'))
    # find for a text channel named `bot` to defaultly output text
    for channel in bot.get_all_channels():
        if channel.name in ['bot', 'Bot']:
            bot.bot_channel = channel
            break


@bot.event
async def on_voice_state_update(member, before, after):
    # disable this feature if there's no `bot` dedicated channel.
    if bot.bot_channel == None:
        return
    # Otherwise, assign the channel as context
    context = bot.bot_channel
    # if member connects to a VC
    if before.channel == None and after.channel != None:
        await infoString(context, f'User "{member.display_name}" joined \'{after.channel.name}\'')
    # if member leaves a VC
    elif after.channel == None and before.channel != None:
        await infoString(context, f'User "{member.display_name}" left \'{before.channel.name}\'')
    # if member changes VC
    elif before.channel.name != after.channel.name:
        await infoString(context, f'User "{member.display_name}" ' +
                         'Switched from \'{before.channel.name}\' -> \'{after.channel.name}\'')


@bot.command(name='server', help='Prints server information.')
async def serverInfo(context):
    # get information about the guild
    guild = context.guild
    # output guild info (name, # members, owner)
    await infoString(context, f'Server Name: "{guild.name}"\n' +
                              f'Server Size: {len(guild.members)}\n' +
                              f'Server Owner: "{guild.owner.display_name}"')


@bot.command(name='select', help='Select a voice channel.')
async def changeChannel(context, *, channel_name: str):
    guild = context.guild
    # get current guild channels
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    # error if channel doesn't exist
    if not existing_channel:
        await errorString(context, 'voice channel is not found (misspelling?)')
        return
    # error if channel isn't a voice channel
    elif existing_channel not in guild.voice_channels:
        await errorString(context, 'this is not a voice channel!')
        return
    # save channel object for further use (selected)
    bot.selected_channel = existing_channel
    # output confirmation
    await infoString(context, f'Channel "{existing_channel}" found & selected!')


@bot.command(name='pc', help='Prints the current selected channel.')
async def currentChannel(context):
    # raise error if no channel is selected yet
    if not bot.selected_channel:
        await errorString(context, 'no channel currently selected!')
        return
    # output current selected channel
    await infoString(context, f'Selected Channel: "{bot.selected_channel}"')


@bot.command(name='present', help='Prints who are currently in selected VC. Default: `@everyone`.')
async def channelAttendence(context, *, tag='@everyone'):
    # raise error if no channel is selected yet
    if not bot.selected_channel:
        await errorString(context, 'no channel currently selected!')
        return

    channel = bot.selected_channel

    # create a list of member names that hold the tag/role currently in the channel
    members = [member.display_name for member in channel.members
               if tag in [role.name for role in member.roles]]

    # turn list into string
    txt = genList(members)

    # output summary of current attendees
    await infoString(context,
                     f'Members Present In "{channel}" With Tag "{tag}": \n{txt}' +
                     f'# Of People With Tag "{tag}" In "{channel}": {len(members)}')


@bot.command(name='absent', help='Lists members of tag not in selected VC.')
async def channelAbsence(context, *, tag='@everyone'):
    # raise error if no channel is selected yet
    if not bot.selected_channel:
        await errorString(context, 'no channel currently selected!')
        return

    channel = bot.selected_channel

    # get all member objects with the tag/role
    all_members = [member for member in context.guild.members
                   if tag in [role.name for role in member.roles]]

    # get all member objects with the tag/role, currently in the selected VC
    present_members = [member for member in channel.members
                       if tag in [role.name for role in member.roles]]

    # select only the differences b/w both lists (the absent members)
    absent_members = list(set(all_members) ^ set(present_members))

    # turn list of absentees into string
    txt = genList([member.display_name for member in absent_members])

    # output summary of absent members
    await infoString(context,
                     f'Members Absent In "{channel}" With Tag "{tag}": \n{txt}' +
                     f'# Of People With Tag "{tag}" NOT In "{channel}": {len(absent_members)}')

    bot.absents = absent_members


@bot.command(name='ping', help='After using `absent`, tags the absent members.')
async def ping(context):
    # raise error if `$absent` isn't used yet or there are no absent people
    if not bot.absents:
        await errorString(context, 'list of absentees are empty (try using `$absent ...` first)')
        return
    # "ping" absentees from gotten from `$absent`
    await infoString(context, 'Pinging Absent People (shame on you!)...')
    for member in bot.absents:
        await context.send(member.mention)


bot.run(TOKEN)
