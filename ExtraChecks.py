'''
Created on Mar 7, 2021

@author: willg
'''
from CustomExceptions import NoCarrotAllowed, NotLounge
from Shared import LOUNGE_SERVER_ID, is_lounge
from discord.ext import commands

def owner_or_permissions(**perms):
    original = commands.has_permissions(**perms).predicate
    async def extended_check(ctx):
        if ctx.guild is None:
            return False
        return ctx.author.id == 706120725882470460 or await original(ctx)
    return commands.check(extended_check)


def lounge_only_check():
    return commands.check(exception_on_not_lounge)

async def exception_on_not_lounge(ctx):
    if not is_lounge(ctx):
        raise NotLounge("Not Lounge server.")
    return True

        
        

def carrot_prohibit_check():
    return commands.check(carrot_prohibit)

async def carrot_prohibit(ctx):
    if ctx.message.content.startswith("^"):
        raise NoCarrotAllowed("Carrot prefix not allowed.")
    return True



