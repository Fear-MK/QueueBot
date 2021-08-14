'''
Created on Mar 7, 2021

@author: willg
'''
from datetime import timedelta
LOUNGE_SERVER_ID = 387347467332485122
TESTING_SERVER_ID = 739733336871665696
BAD_WOLF_ID = 706120725882470460
TESTING=False
QUEUEBOT_INVITE_LINK = "https://discord.com/api/oauth2/authorize?client_id=803378682479640586&permissions=269667344&scope=bot"
MK7_GUILD_ID = 280462328603082753
MKW_ITEM_RAIN_LOUNGE = 678245545881501727
CACHING_TIME_SECONDS = 30
CACHING_TIME = timedelta(seconds=CACHING_TIME_SECONDS)
DISCORD_MAX_MESSAGE_LEN = 2000

RATING_MANUALLY_MANAGED_GUILD_IDS = {MK7_GUILD_ID}

def is_lounge(ctx):
    if isinstance(ctx, str):
        return str(LOUNGE_SERVER_ID) == ctx or (str(TESTING_SERVER_ID) == ctx if TESTING else False)
    elif isinstance(ctx, int):
        return LOUNGE_SERVER_ID == ctx or (TESTING_SERVER_ID == ctx if TESTING else False)
    return ctx.guild.id == LOUNGE_SERVER_ID or (ctx.guild.id == ctx if TESTING else False)
