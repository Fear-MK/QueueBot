from discord.ext import commands, tasks
import json
import discord
from cogs import Queue
from itertools import cycle
from CustomExceptions import NoGuildSettings


bot = commands.Bot(owner_id=706120725882470460, command_prefix='!', case_insensitive=True)

#bot = commands.Bot(owner_id=706120725882470460, command_prefix='!', case_insensitive=True, intents=discord.Intents.all())

initial_extensions = ['cogs.Queue', 'cogs.Elo']
status_cycle = cycle(["Let's Squad Queue!", "!help for how to use bot"])


with open('./config.json', 'r') as cjson:
    config = json.load(cjson)

@bot.event
async def on_ready():
    statuses.start() 
    print("Logged in as {0.user}".format(bot))
       

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
    
    

@bot.event
async def on_command_error(ctx, error):
    if ctx.author.bot:
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await(await ctx.send("Your command is missing an argument: `%s`" %
                       str(error.param))).delete(delay=10)
        return
    if isinstance(error, commands.CommandOnCooldown):
        await(await ctx.send("This command is on cooldown; try again in %.0fs"
                       % error.retry_after)).delete(delay=5)
        return
    
    #TODO: Need to display the roles that they must have, just displays %s
    if isinstance(error, commands.MissingAnyRole):
        await(await ctx.send(f"You either need to be a server administrator, or have one of the following roles to use this command: `%s`",
                             )
            
              ).delete(delay=10)
        return
    if isinstance(error, commands.BadArgument):
        await(await ctx.send("BadArgument Error: `%s`" % error.args)).delete(delay=10)
        return
    if isinstance(error, commands.BotMissingPermissions):
        try:
            await(await ctx.send("I need the following permissions to use this command: %s"
                       % ", ".join(error.missing_perms))).delete(delay=10)
        except discord.Forbidden:
            pass
        return
    if isinstance(error, commands.NoPrivateMessage):
        await(await ctx.send("You can't use this command in DMs!")).delete(delay=5)
        return
    if isinstance(error, commands.MissingPermissions):
        try:
            await(await ctx.send("You need the following permissions to use this command: %s"
                       % ", ".join(error.missing_perms))).delete(delay=10)
        except discord.Forbidden:
            pass
        return
    if isinstance(error, NoGuildSettings):
        try:
            await ctx.send("Contact a server admin to set up Queuebot's settings by doing `!queuebot_setup`", delete_after=10)
        except discord.Forbidden:
            pass
        return

    
    if 'original' in error.__dict__:
        if isinstance(error.original, discord.Forbidden):
            #This should only run if bot can't send messages
            return

    
    raise error

@tasks.loop(seconds=20)
async def statuses():
    game = discord.Game(next(status_cycle))
    await bot.change_presence(status=discord.Status.online, activity=game)
    
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await Queue.Queue.elo_check(bot, message)
    #We overrode bot's on_message function, so we must manually invoke process commands
    await bot.process_commands(message)
                    
    
bot.run(config["token"])
