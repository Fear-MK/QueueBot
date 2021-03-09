'''
Created on Mar 7, 2021

@author: willg
'''
LOUNGE_SERVER_ID = 387347467332485122
TESTING_SERVER_ID = 739733336871665696
TESTING=True

def is_lounge(ctx):
    if isinstance(ctx, str):
        return str(LOUNGE_SERVER_ID) == ctx or (str(TESTING_SERVER_ID) == ctx if TESTING else False)
    elif isinstance(ctx, int):
        return LOUNGE_SERVER_ID == ctx or (TESTING_SERVER_ID == ctx if TESTING else False)
    return ctx.guild.id == LOUNGE_SERVER_ID or (ctx.guild.id == ctx if TESTING else False)



