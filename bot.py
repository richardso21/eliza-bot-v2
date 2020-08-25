import discord
import os
from datetime import datetime
from discord.ext.commands import Bot

TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(command_prefix='$')

bot.selected_channel = None
bot.bot_channel = None
bot.selected_members = None
bot.vc_members = {}


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
                                                        name='Hamilton on Disney+'))
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
        await infoString(context, f'"{member.display_name}" Joined \'{after.channel.name}\'')
        # get current time that member joined VC
        bot.vc_members[member] = datetime.now().replace(microsecond=0)

    # if member leaves a VC
    elif after.channel == None and before.channel != None:
        # find amount of time member spent in VC (time difference)
        time_diff = datetime.now().replace(microsecond=0) - bot.vc_members[member]

        await infoString(context, f'"{member.display_name}" Left \'{before.channel.name}\'' +
                                  f'({str(time_diff)} on VC)')
                                #   f'({str(time_diff)} @ \'{before.channel.name}\')')
        # clear dict entry (save memory)
        del bot.vc_members[member]

    # # if member changes VC (beware of channel spam!!!)
    # elif before.channel.name != after.channel.name:
    #     # find amount of time member spent in VC (time difference)
    #     time_diff = datetime.now().replace(microsecond=0) - bot.vc_members[member]

    #     await infoString(context, f'"{member.display_name}" ' +
    #                      f'Switched from \'{before.channel.name}\' -> \'{after.channel.name}\'' +
    #                      f'({str(time_diff)} @ \'{before.channel.name}\')')
    #     # reassign current time to member
    #     bot.vc_members[member] = datetime.now().replace(microsecond=0)


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
    await infoString(context, f'Channel "{existing_channel}" Selected')


@bot.command(name='current', help='Prints the current selected channel.')
async def currentChannel(context):
    # raise error if no channel is selected yet
    if not bot.selected_channel:
        await errorString(context, 'no channel currently selected (You might end up with unwanted results)!')
        return
    # output current selected channel
    await infoString(context, f'Selected Channel: "{bot.selected_channel}"')


@bot.command(name='present', help='Prints who are currently in selected VC. Default: `@everyone`.')
async def channelPresence(context, *, tag='@everyone'):
    # try to auto-select no channel is selected yet
    vc_available = False
    if not bot.selected_channel:
        for voice_channel in context.guild.voice_channels:
            if len(voice_channel.members) != 0:
                await infoString(context, f'No Channel Selected, Auto-Selecting: "{voice_channel}"')
                channel = voice_channel
                vc_available = True
                break
        if not vc_available:
            await errorString(context, 'no channel selected or has members!')
            return
    else:
        channel = bot.selected_channel

    # create a list of member names that hold the tag/role currently in the channel
    members = [member.display_name for member in channel.members
               if tag in [role.name for role in member.roles]]

    # turn list into string
    txt = genList(members)

    # output summary of current attendees
    await infoString(context,
                     f'members Present in "{channel}" with Tag "{tag}": \n{txt}' +
                     f'# of people with Tag "{tag}" IN "{channel}": {len(members)}')

    bot.selected_members = members


@bot.command(name='absent', help='Lists members of tag not in selected VC.')
async def channelAbsence(context, *, tag='@everyone'):
    # try to auto-select no channel is selected yet
    vc_available = False
    if not bot.selected_channel:
        for voice_channel in context.guild.voice_channels:
            if len(voice_channel.members) != 0:
                await infoString(context, f'No Channel Selected, Auto-Selecting: "{voice_channel}"')
                channel = voice_channel
                vc_available = True
                break
        if not vc_available:
            await errorString(context, 'no channel selected or has members!')
            return
    else:
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
                     f'members Absent in "{channel}" with Tag "{tag}": \n{txt}' +
                     f'# of people with Tag "{tag}" NOT IN "{channel}": {len(absent_members)}')

    bot.selected_members = absent_members


@bot.command(name='ping', help='After using `absent`/`present`/`role`, tags the selected members.')
async def ping(context):
    # raise error if `$absent` isn't used yet or there are no absent people
    if not bot.selected_members:
        await errorString(context, 'list of absentees are empty (try using `$absent|present|role` first)')
        return
    # "ping" absentees from gotten from `$absent`
    await infoString(context, 'Pinging Absentees...')
    for member in bot.selected_members:
        await context.send(member.mention)


@bot.command(name='role', help='Lists all members with the role')
async def roles(context, *, tag: str):
    # raise error if argument isn't given
    if not tag:
        await errorString(context, '`$role` requires an extra argument: role/tag/dept.')
        return

    # list all members that has the role
    role_members = [member for member in context.guild.members
                   if tag in [role.name for role in member.roles]]

    # generate list string
    txt = genList([member.display_name for member in role_members])

    await infoString(context,
                     f'members with Tag "{tag}": \n{txt}' +
                     f'# of people with Tag "{tag}": {len(role_members)}')

    bot.selected_members = role_members


bot.run(TOKEN)
