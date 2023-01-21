import vars, literals, re
import discord  #upm package(py-cord)
from sync import sync_init, sync_roles, sync_sheets, sync_usis_before
from json_wrapper import check_and_load
from verify_student_codes import VerificationButtonView, verify_student
from utils_wrapper import get_channel, bot_admin_and_higher, faculty_and_higher, get_link_from_sheet_id
from assign_sections_button import AssignSectionsView


# load json
vars.json_file = "info.json"
info = check_and_load(vars.json_file)


# Define the bot with proper intents
intents = discord.Intents(members=True, guilds=True, messages=True)
bot = discord.Bot(intents=intents, debug_guilds=[info['guild_id']], status=discord.Status.idle)


@bot.event
async def on_ready():
    await sync_init(bot, info)
    await sync_roles(info)
    await sync_sheets(info)
    print('Bot ready to go!')
    await bot.change_presence(status=discord.Status.online)

@bot.event
async def on_member_join(member):
    # check if a member of eee guild joined, add faculty role
    course_code, semester = info["course_code"], info["semester"]
    if member.bot:
        return
    elif member in vars.eee_guild.members:
        await member.send(f"Welcome! You have been given the faculty role to the {course_code} {semester} Discord server! " + 
                          "Please change your **__nickname__** for the server to `[Initial] Full Name` format, " + 
                          "e.g., `[ABA] Abid Abrar`")
        await member.add_roles(vars.faculty_role)
    # most likely student
    else:
        rules = get_channel(name="📝rules")
        welcome = get_channel(name="👏🏻welcome✌🏻")

        welcome_msg = f"Welcome to the {course_code} {semester} Discord server! "
        welcome_msg += f"Please verify yourself by visiting {welcome.mention} and read the rules in {rules.mention}. "
        welcome_msg += f"Otherwise, you will not be able to access the server"

        await member.send(welcome_msg)


@bot.slash_command(name = "check-everyone", description="DMs unverified students to complete verification & checks role of verified.")
@bot_admin_and_higher()
async def check_everyone(ctx):
    #await ctx.respond(content="Checking everyone...", ephemeral=True)
    await ctx.defer(ephemeral=True)

    for member in get_channel(name="💁🏻admin-help").members:
        if member.guild_permissions.manage_guild:
            continue
        else:
            welcome = get_channel(name="👏🏻welcome✌🏻")
            await member.send(f"Please verify yourself by visiting the {welcome.mention} channel")

    for member in vars.student_role.members:
        student_id = int(re.search(literals.regex_student['id'], member.display_name).group(0))
        if student_id not in vars.df_student.index:
            member.remove_roles(*member.roles)
        else:
            _ = await verify_student(member, student_id)

    await ctx.followup.send(content="Done checking everyone!", ephemeral=True)

@bot.slash_command(name = "post-faculty-section", description="Posts a button for faculties to auto assign section roles.")
@bot_admin_and_higher()
async def post_faculty_section(ctx):
    await ctx.respond(content="Click the button below to get access to your sections", view=AssignSectionsView())


@bot.slash_command(name = "post-verify", description="Posts a button for students to verify.")
@bot_admin_and_higher()
async def post_verify(ctx):
    await ctx.respond("Click the button below to verify", view=VerificationButtonView())


@bot.message_command(name="Revive as 'Verify Me'")
@bot_admin_and_higher()
async def revive_verify(ctx, message):
    try:
        await message.edit(view=VerificationButtonView())
        await ctx.respond(f"message revived as 'verify me': {message.jump_url}", ephemeral=True, delete_after=3)
    except:
        await ctx.respond("failed to revive message.", ephemeral=True)


@bot.message_command(name="Revive as 'Generate Sec Access'")
@bot_admin_and_higher()
async def revive_sec_access(ctx, message):
    try:
        await message.edit(view=AssignSectionsView())
        await ctx.respond(f"message revived as 'generate section access': {message.jump_url}", ephemeral=True, delete_after=3)
    except:
        await ctx.respond("failed to revive message.", ephemeral=True)


@bot.slash_command(name = "sync-sheets", description = "Sync updates from enrolment sheet and marks sheet with bot.")
@faculty_and_higher()
async def sync_with_sheets(ctx):
    # await ctx.respond(content="Syncing with sheets...", ephemeral=True)
    await ctx.defer(ephemeral=True)
    await sync_sheets(info)
    await ctx.followup.send(content="Done syncing with sheets!", ephemeral=True)


@bot.message_command(name="Update USIS (Before)")
@bot_admin_and_higher()
async def update_usis_before(ctx, message):
    await ctx.defer(ephemeral=True)
    try:
        valid_filenames = []
        for attachment in message.attachments:
            if attachment.filename.endswith(".xls"):
                valid_filenames.append(attachment.filename)
                await attachment.save(attachment.filename) 
        if not valid_filenames:
            await ctx.followup.send(content="No xls found in the this message.", ephemeral=True)
        else:
            sync_usis_before(info, valid_filenames)
            await ctx.followup.send(content="USIS Before Updated", ephemeral=True)
    except:
        await ctx.followup.send(content="No attachments found in the this message.", ephemeral=True)

@bot.slash_command(name = "get-links", description = "Get the links for discord invite, enrolment and marks sheet")
@faculty_and_higher()
async def get_links(ctx):
    discord_link = info["invite"]
    enrolment_id = info["enrolment"]
    marks_id = info["marks"]

    msg = f"Discord Invite Link: <{discord_link}>\n\n"
    msg += f"Enrolment Manager Sheet: <{get_link_from_sheet_id(enrolment_id)}>\n\n"
    msg += f"Marks Sheet: <{get_link_from_sheet_id(marks_id)}>"

    await ctx.respond(content=msg, ephemeral=True)

# mainly for debugging...
# from discord_sec_manager import bulk_delete_category as bdc
# from literals import class_types
# @bot.slash_command()
# @discord.default_permissions(administrator=True)
# async def bulk_delete_category(ctx, 
#                                sec: int = None, 
#                                ctype: discord.Option(choices=class_types) = None):
#     if sec:
#         secs = [sec]
#     else:
#         secs = range(2,100)
#     for sec in secs:
#         if ctype:    
#             msg = await bdc(sec, ctype)
#         else:
#             msg1 = await bdc(sec, 'theory')
#             msg2 = await bdc(sec, 'lab')
#             msg = f"{msg1}\n{msg2}"
#     await ctx.respond(msg, ephemeral=True)

bot.run(info['bot_token'])
