'''
Created on Feb 23, 2021

@author: willg
'''

from discord.ext.commands import CommandError

class NoGuildSettings(CommandError):
    pass

class NoCarrotAllowed(CommandError):
    pass

class NotLounge(CommandError):
    pass