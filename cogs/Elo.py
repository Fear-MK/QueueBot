# every lounge is different so this file will probably
# have to be completely rewritten for each server.
# my implementation is here as an example; gspread is only
# needed if you get MMR from a spreadsheet.

# The important part is that the function returns False
# if a player's MMR can't be found,
# and returns the player's MMR otherwise

import discord
from discord.ext import commands
import aiohttp
import gspread
from collections import namedtuple, defaultdict
import dill as p

gc = gspread.service_account(filename='credentials.json')




Website_JSON_Framer = namedtuple('Website_JSON_Framer', 'name_name primary_rating_name secondary_rating_name')
Website_JSON_Info = namedtuple('Website_JSON_Info', 'API_URL primary_JSON_framing secondary_JSON_framing')
Website_Data = namedtuple('Website_Data', 'primary_data secondary_data')

Sheet_ = namedtuple('Sheet_', 'sheet_name sheet_range', defaults=[None, None])
Sheet_Data = namedtuple('Sheet_Data', 'sheet_id primary_rating secondary_rating', defaults=[None, Sheet_(), Sheet_()])
Spreadsheet_Data = namedtuple('Spreadsheet_Data', 'primary_sheet secondary_sheet', defaults=[Sheet_Data(), Sheet_Data()])
Guild_Rating_Data = namedtuple('Guild_Rating_Data', 'using_sheet sheet_data website_data', defaults=[True, Spreadsheet_Data(), Spreadsheet_Data()])


def owner_or_permissions(**perms):
    original = commands.has_permissions(**perms).predicate
    async def extended_check(ctx):
        if ctx.guild is None:
            return False
        return ctx.author.id == 706120725882470460 or await original(ctx)
    return commands.check(extended_check)


class GuildRating():
    def __init__(self):        
        #Website
        self.primary_website_url = "https://mariokartboards.com/lounge/json/player.php?type=rt&name="
        self.secondary_website_url = "https://mariokartboards.com/lounge/json/player.php?type=ct&name="
        
        self.guild_rating = Guild_Rating_Data()

        self.sheet_ratings = {True:
                              {True:None, False:None},
                              False:
                              {True:None, False:None}}
                
    def non_async_set_up_system(self):
        if self.guild_rating.using_sheet:
            if self.guild_rating.sheet_data.primary_sheet.sheet_id is None:
                return False
            if self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_name is None:
                return False
            if self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_range is None:
                return False
            
            worksheet_id = self.guild_rating.sheet_data.primary_sheet.sheet_id
            worksheet_name = self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_name
            try:
                self.sheet_ratings[True][True] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
            except:
                return False
            
            #Primary sheet, secondary rating connection
            if self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_name is None or\
            self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_range is None:
                pass
            else:
                worksheet_name = self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_name
                try:
                    self.sheet_ratings[True][False] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
                except:
                    pass
            #Secondary sheet, primary rating connection
            worksheet_id = self.guild_rating.sheet_data.secondary_sheet.sheet_id
            worksheet_name = self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name
            if worksheet_id is None or \
            self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name is None or\
            self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_range is None:
                pass
            else:
                worksheet_name = self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name
                try:
                    self.sheet_ratings[False][True] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
                except:
                    pass
            #Secondary sheet, secondary rating connection
            if worksheet_id is None or \
            self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_name is None or\
            self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_range is None:
                pass
            else:
                worksheet_name = self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_name
                try:
                    self.sheet_ratings[False][False] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
                except:
                    pass
        return True 
        
    async def set_up_system(self, ctx=None):
        if self.guild_rating.using_sheet:
            if self.guild_rating.sheet_data.primary_sheet.sheet_id is None:
                if ctx is not None:
                    await ctx.send("You must set your primary sheet id using this command: `!set primarysheet sheet id <id>` - If you need help, do `!rating_help`")
                return False
            if self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_name is None:
                if ctx is not None:
                    await ctx.send("You must set your primary sheet's primary leaderboard name using this command: `!set primarysheet primaryrating name <name>` - If you need help, do `!rating_help`")
                return False
            if self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_range is None:
                if ctx is not None:
                    await ctx.send("You must set your primary sheet's primary leaderboard name using this command: `!set primarysheet primaryrating range <range>` where range is a valid Excel range (eg C:D or A2:D) - If you need help, do `!set help`")
                return False
            
            info_str = "Connection info:\n"
            worksheet_id = self.guild_rating.sheet_data.primary_sheet.sheet_id
            worksheet_name = self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_name
            try:
                self.sheet_ratings[True][True] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
            except:
                if ctx is not None:
                    await ctx.send("✘ Unable to open the sheet.\nMake sure that the following account has access to the spreadsheet: mkw-war-lounge-bot-service-acc@responsive-bird-291003.iam.gserviceaccount.com\nAlso, make sure that your spreadsheet ID is correct, and also the sheet name. (The sheet name is not the title of your entire spreadsheet, it is the name of the sheet tab.)")
                return False
            else:
                info_str += "✓ Primary rating for primary sheet linked.\n"
            
            #Primary sheet, secondary rating connection
            if self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_name is None or\
            self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_range is None:
                info_str += "✘ Secondary rating for primary sheet not linked because it was not set up.\n"
            else:
                worksheet_name = self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_name
                try:
                    self.sheet_ratings[True][False] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
                except:
                    info_str += "✘ Secondary rating for primary sheet not linked because it failed when I tried to connect. Make sure the secondary sheet name is correct.\n"
                else:
                    info_str += "✓ Secondary rating for primary sheet linked.\n"
            #Secondary sheet, primary rating connection
            worksheet_id = self.guild_rating.sheet_data.secondary_sheet.sheet_id
            worksheet_name = self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name
            if worksheet_id is None or \
            self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name is None or\
            self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_range is None:
                info_str += "✘ Primary rating for secondary sheet not linked because it was not set up.\n"
            else:
                worksheet_name = self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name
                try:
                    self.sheet_ratings[False][True] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
                except:
                    info_str += "✘ Primary rating for secondary sheet not linked because it failed when I tried to connect. Make sure the secondary sheet name is correct and that this email has access to the sheet: mkw-war-lounge-bot-service-acc@responsive-bird-291003.iam.gserviceaccount.com\n"   
                else:
                    info_str += "✓ Primary rating for secondary sheet linked.\n"
            #Secondary sheet, secondary rating connection
            if worksheet_id is None or \
            self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_name is None or\
            self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_range is None:
                info_str += "✘ Secondary rating for secondary sheet not linked because it was not set up.\n"
            else:
                worksheet_name = self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_name
                try:
                    self.sheet_ratings[False][False] = gc.open_by_key(worksheet_id).worksheet(worksheet_name)
                except:
                    info_str += "✘ Secondary rating for secondary sheet not linked because it failed when I tried to connect. Make sure the secondary sheet name is correct.\n"
                else:
                    info_str += "✓ Secondary rating for secondary sheet linked.\n"
                    
            if ctx is not None:
                await ctx.send(info_str)
        return True 
        
    async def google_sheets_mmr(self, ctx, members:[discord.Member], is_primary_leaderboard=True, is_primary_rating=True):
        if len(members) == 0:
            return {}
        using_str = isinstance(members[0], str)
        
        member_ratings = dict(zip(members, [False]*len(members)))
        names = [member.display_name.lower().replace(" ", "") for member in members] if not using_str else [member.lower().replace(" ", "") for member in members]
        ratings = self.sheet_ratings[is_primary_leaderboard][is_primary_rating]
        if ratings is None:
            await ctx.send("Cannot pull mmr because the sheets were not set up properly. Contact an admin and tell them to use `!rating_help` to set up the sheets correctly.")
            return False
        
        
        sheet_data = (self.guild_rating.sheet_data.primary_sheet if is_primary_leaderboard\
                          else self.guild_rating.sheet_data.secondary_sheet)
        sheet = sheet_data.primary_rating if is_primary_rating else sheet_data.secondary_rating
        spreadsheet_range = sheet.sheet_range
        if spreadsheet_range is None:
            await ctx.send("Cannot pull mmr because the sheets are not set up properly. Contact an admin and tell them to use `!rating_help` to set up the sheets correctly.")
            return False 
                
        try:
            all_mmr_data = ratings.get(spreadsheet_range)
        except: #numerous failure types can occur, but they all mean the same thing: we didn't get out data
            await ctx.send("Cannot pull mmr. This can happen because the bot temporarily cannot connect to the sheets. However, it is more likely that the sheets were not set up properly. Contact an admin and tell them to use `!rating_help` to set up the sheets correctly if this issue does not resolve itself.")
            return False
        #Check for corrupt data
        if not isinstance(all_mmr_data, gspread.models.ValueRange):
            await ctx.send("Received bad data from the spreadsheet. Could not pull mmr. Wait and try again. If the issue persists, you should DM Bad Wolf.")
            return False
        
        check_value = None
        for player_data in all_mmr_data:
            #Checking for corrupt data
            if not isinstance(player_data, list):
                continue
            if len(player_data) != 2:
                continue
            if not (isinstance(player_data[0], str) and isinstance(player_data[1], str) and player_data[1].isnumeric()):
                continue
            this_name = player_data[0].lower().replace(" ", "")
            
            if this_name not in names:
                continue
            
            #We found a match
            check_value = int(player_data[1])
            found_member = members[names.index(this_name)]
            member_ratings[found_member] = False if check_value is None else check_value
            if using_str:
                temp = member_ratings[found_member]
                del member_ratings[found_member]
                member_ratings[player_data[0]] = temp
            
        return member_ratings
    
    
    async def website_mmr(self, members:[discord.Member], is_rt=True, is_runner=True):
        member_ratings = dict(zip(members, [False]*len(members)))
        names = [member.display_name.lower().replace(" ", "") for member in members]
        full_url = self.primary_website_url if is_rt else self.secondary_website_url
        full_url += ",".join(names)
        data = None
        try:
            data = await self.getJSONData(full_url)
        except: #numerous failure types can occur, but they all mean the same thing: we didn't get out data
            return False
        
        if self.data_is_corrupt(data, len(members)):
            return False
        
        for playerData in data:
            pdata_name = playerData['name'].lower().replace(" ", "")
            if pdata_name not in names:
                continue
            member_ratings[member[names.index(pdata_name)]] = playerData["current_mmr"]
        
        
        return member_ratings
    
        
        
    async def mmr(self, ctx, members:[discord.Member], is_primary_leaderboard=True, is_primary_rating=True):
        if self.guild_rating.using_sheet:
            return await self.google_sheets_mmr(ctx, members, is_primary_leaderboard, is_primary_rating)
        else:
            return await self.website_mmr(members, is_primary_leaderboard, is_primary_rating)
            
    
    async def getJSONData(self, full_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url) as r:
                if r.status == 200:
                    js = await r.json()
                    return js
    
    def data_is_corrupt(self, jsonData, data_size):
        if jsonData == None:
            print("Bad request to Lounge API... Data was None.")
            return True
        if "error" in jsonData:
            print("Bad request to Lounge API... Error in data.")
            return True
        if not isinstance(jsonData, list):
            print("Bad request to Lounge API... Data was not a list.")
            return True
        
        if len(jsonData) != data_size:
            return True
        
        for playerData in jsonData:
            if not isinstance(playerData, dict):
                return True
            
            #if "current_mmr" not in playerData or not isinstance(playerData["current_mmr"], int):
            #    return True
            if "current_mmr" not in playerData or not isinstance(playerData["current_mmr"], str) or not playerData["current_mmr"].isnumeric():
                return True
            if "name" not in playerData or not isinstance(playerData["name"], str):
                return True
        
        return int(playerData["current_mmr"]) < 0

    async def set_guild_rating_setting(self, ctx, which_sheet: str, which_leaderboard: str, item_to_set:str, setting:str):
        setting = " ".join(ctx.message.content.split(" ")[4:])
        valid_sheet_types = {"primarysheet", "secondarysheet"}
        if which_sheet.lower() not in valid_sheet_types:
            await ctx.send(f"Specify which sheet you are setting. Valid choices are: {', '.join(valid_sheet_types)}\nDo `!rating_help` for help.")
            return
        
        valid_leaderboard_types = {"sheet", "primaryrating", "secondaryrating"}
        if which_leaderboard.lower() not in valid_leaderboard_types:
            await ctx.send(f"Specify which leaderboard you are setting. Valid choices are: {', '.join(valid_leaderboard_types)}\nDo `!rating_help` for help.")
            return
        
        valid_item_to_set = {"name", "id", "range"}
        if item_to_set.lower() not in valid_item_to_set:
            await ctx.send(f"Specify which item you are setting. Valid choices are: {', '.join(valid_item_to_set)}\nDo `!rating_help` for help.")
            return
        
        if which_leaderboard == "sheet" and item_to_set != "id":
            await ctx.send(f"If you are trying to set the sheet id, do `!set <primarysheet/secondarysheet> sheet id <id>`\nDo `!rating_help` for help.")
            return
        if which_leaderboard != "sheet" and item_to_set == "id":
            await ctx.send(f"You cannot set the id of a leaderboard, only of a primarysheet or secondarysheet.\nDo `!rating_help` for help.")
            return
        
        is_primary_sheet = which_sheet == "primarysheet"
        new_sheet_data = self.guild_rating.sheet_data.primary_sheet if is_primary_sheet else self.guild_rating.sheet_data.secondary_sheet
        if which_leaderboard == "sheet":
            new_sheet_data = new_sheet_data._replace(sheet_id = setting)
        else:
            is_primaryrating = which_leaderboard == "primaryrating"
            new_sheet = new_sheet_data.primary_rating if is_primaryrating else new_sheet_data.secondary_rating
            if item_to_set == "name":
                new_sheet = new_sheet._replace(sheet_name=setting)
            if item_to_set == "range":
                new_sheet = new_sheet._replace(sheet_range=setting)
            new_sheet_data = new_sheet_data._replace(primary_rating=new_sheet) if is_primaryrating else new_sheet_data._replace(secondary_rating=new_sheet)
        if is_primary_sheet:
            self.guild_rating = self.guild_rating._replace(
            sheet_data=self.guild_rating.sheet_data._replace(primary_sheet = new_sheet_data)
            )
        else:
            self.guild_rating = self.guild_rating._replace(
            sheet_data=self.guild_rating.sheet_data._replace(secondary_sheet = new_sheet_data)
            )
        return True
    
    async def send_settings(self, ctx, is_new=False):
        spreadsheet_base_url = "https://docs.google.com/spreadsheets/d/"
        to_send = "**New Settings:**\n\n" if is_new else ""
        to_send += "Using Google Spreadsheets: *" + ("Yes" if self.guild_rating.using_sheet else "No") + "*\n"
        to_send += "\n**Primary Sheet Info:**\n"
        to_send += f"\u200b\t- Spreadsheet link: {'`'+spreadsheet_base_url + self.guild_rating.sheet_data.primary_sheet.sheet_id +'`' if self.guild_rating.sheet_data.primary_sheet.sheet_id is not None else '*No sheet id set*'}\n"
        to_send += "\u200b\t*Primary Rating Info:*\n"
        to_send += f"\u200b\t\t- Sheet tab name: *{self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_name}*\n"
        to_send += f"\u200b\t\t- Cell range: *{self.guild_rating.sheet_data.primary_sheet.primary_rating.sheet_range}*\n"
        to_send += "\u200b\t*Secondary Rating Info:*\n"
        to_send += f"\u200b\t\t- Sheet tab name: *{self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_name}*\n"
        to_send += f"\u200b\t\t- Cell range: *{self.guild_rating.sheet_data.primary_sheet.secondary_rating.sheet_range}*\n"

        to_send += "\n**Secondary Sheet Info:**\n"
        to_send += f"\u200b\t- Spreadsheet link: {'`'+spreadsheet_base_url + self.guild_rating.sheet_data.secondary_sheet.sheet_id +'`' if self.guild_rating.sheet_data.secondary_sheet.sheet_id is not None else '*No sheet id set*'}\n"
        to_send += "\u200b\t*Primary Rating Info:*\n"
        to_send += f"\u200b\t\t- Sheet tab name: *{self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_name}*\n"
        to_send += f"\u200b\t\t- Cell range: *{self.guild_rating.sheet_data.secondary_sheet.primary_rating.sheet_range}*\n"
        to_send += "\u200b\t*Secondary Rating Info:*\n"
        to_send += f"\u200b\t\t- Sheet tab name: *{self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_name}*\n"
        to_send += f"\u200b\t\t- Cell range: *{self.guild_rating.sheet_data.secondary_sheet.secondary_rating.sheet_range}*\n"

    
        to_send += "\nYou must do `!connect` when you're finished and ready to attempt to connect to your spreadsheet(s)."
        
        await ctx.send(to_send)
            
class Elo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_sheets = defaultdict(GuildRating)
        self.load_pkl_guild_sheets()
        self.connect_all_sheets()
        
    async def mmr(self, ctx, members: [discord.Member], is_primary_leaderboard=True, is_primary_rating=True):
        if str(ctx.guild.id) not in self.guild_sheets:
            #self.guild_sheets[str(ctx.guild.id)] = GuildRating(self.bot, ctx.guild)
            await ctx.send("A server admin needs to set up your rating system. Have a server admin do `!rating_help` for help.")
        else:
            return await self.guild_sheets[str(ctx.guild.id)].mmr(ctx, members, is_primary_leaderboard, is_primary_rating)
        
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.guild_only()
    @commands.max_concurrency(number=1,wait=True)
    @owner_or_permissions(administrator=True)
    async def set(self, ctx, which_sheet: str, which_leaderboard: str, item_to_set:str, setting:str):
        """Do !rating_help to understand how to use this command"""
        success = await self.guild_sheets[str(ctx.guild.id)].set_guild_rating_setting(ctx, which_sheet, which_leaderboard, item_to_set, setting)
        if success:
            self.pkl_guild_sheets()
            await self.guild_sheets[str(ctx.guild.id)].send_settings(ctx, is_new=True)
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.guild_only()
    @commands.max_concurrency(number=1,wait=True)
    @owner_or_permissions(administrator=True)
    async def rating_settings(self, ctx):
        """Displays the settings for how rating is pulled"""
        await self.guild_sheets[str(ctx.guild.id)].send_settings(ctx, is_new=False)
    
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.guild_only()
    @commands.max_concurrency(number=1,wait=True)
    @owner_or_permissions(administrator=True)
    async def connect(self, ctx):
        """Run this after you change settings and want to refresh your connection."""
        msg = await ctx.send("Testing connection...")
        await self.guild_sheets[str(ctx.guild.id)].set_up_system(ctx)
        await msg.delete()
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.guild_only()
    @commands.max_concurrency(number=1,wait=True)
    @owner_or_permissions(administrator=True)
    async def rating_help(self, ctx):
        """Tutorial for how to set up the bot with elo on sheets"""
        for i in range(5):
            try:
                with open(f"sheet_rating_setup_{i}.txt") as fp:
                    stuff = fp.read()
                    if len(stuff) < 5:
                        break
                    await ctx.send(stuff)
            except:
                pass
    
    
    def pkl_guild_sheets(self):
        pkl_dump_path = "guild_sheets_backup.pkl"
        with open(pkl_dump_path, "wb") as pickle_out:
            to_dump = {}
            for guild_id, rating_settings in self.guild_sheets.items():
                to_dump[guild_id] = rating_settings.guild_rating
            try:
                p.dump(to_dump, pickle_out)
            except:
                print("Could not dump pickle for guild sheet settings.")
                raise
                
    def load_pkl_guild_sheets(self):
        self.guild_sheets = defaultdict(GuildRating)
        try:
            with open("guild_sheets_backup.pkl", "rb") as pickle_in:
                try:
                    temp = p.load(pickle_in)
                    if temp is not None:
                        for guild_id, guild_rating in temp.items():
                            self.guild_sheets[guild_id].guild_rating = guild_rating
                except:
                    print("Could not read in pickle for guild_sheets_backup.pkl data.")
                    raise
        except:
            print("guild_sheets_backup.pkl does not exist, so no guild data loaded in. Will create when guilds set their settings.")         
            
    def connect_all_sheets(self):
        for guild_sheet in self.guild_sheets.values():
            guild_sheet.non_async_set_up_system()
        print("All sheets connected.")

    
def setup(bot):
    bot.add_cog(Elo(bot))
