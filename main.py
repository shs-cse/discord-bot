from discord.interactions import Interaction
from discord.ui.item import Item
import vars
import literals
import re
import discord  # upm package(py-cord)
from sync import sync_init, sync_roles, sync_sheets, sync_usis_before
from json_wrapper import check_and_load
from verify_student_codes import VerificationButtonView, verify_student
from utils_wrapper import get_channel, get_member, bot_admin_and_higher, faculty_and_higher, get_link_from_sheet_id
from assign_sections_button import AssignSectionsView, assign_sections
from marks import update_sec_marks, get_df_marks_by_student_id


# load json
vars.json_file = "info.json"
info = check_and_load(vars.json_file)


# Define the bot with proper intents
intents = discord.Intents(members=True, guilds=True, messages=True)
bot = discord.Bot(intents=intents, debug_guilds=[
                  info['guild_id']], status=discord.Status.idle)


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
        nick_in_eee_guild = vars.eee_guild.get_member(member.id).nick
        await member.edit(nick=nick_in_eee_guild)
        await member.send(f"Welcome! You have been given the faculty role to the {course_code} {semester} Discord server! " +
                          "Please change your **__nickname__** for the server to `[Initial] Full Name` format, " +
                          "e.g., `[ABA] Abid Abrar`")
        await member.add_roles(vars.faculty_role)
        await assign_sections(member)
    # most likely student
    else:
        rules = get_channel(name="📝rules")
        welcome = get_channel(name="👏🏻welcome✌🏻")

        welcome_msg = f"Welcome to the {course_code} {semester} Discord server! "
        welcome_msg += f"Please verify yourself by visiting {welcome.mention} and read the rules in {rules.mention}. "
        welcome_msg += f"Otherwise, you will not be able to access the server"

        await member.send(welcome_msg)


@bot.slash_command(name="check-everyone", description="DMs unverified students to complete verification & checks role of verified.")
@bot_admin_and_higher()
async def check_everyone(ctx):
    # await ctx.respond(content="Checking everyone...", ephemeral=True)
    await ctx.defer(ephemeral=True)
    course_code, semester = info["course_code"], info["semester"]

    for member in get_channel(name="💁🏻admin-help").members:
        if member.guild_permissions.manage_guild:
            continue
        elif member in vars.eee_guild.members:
            await member.send(f"Welcome! You have been given the faculty role to the {course_code} {semester} Discord server! " +
                              "Please change your **__nickname__** for the server to `[Initial] Full Name` format, " +
                              "e.g., `[SHS] Shadman Shahriar`")
            await member.add_roles(vars.faculty_role)
        else:
            welcome = get_channel(name="👏🏻welcome✌🏻")
            await member.send(f"Please verify yourself by visiting the {welcome.mention} channel")

    for member in vars.faculty_role.members:
        if not re.search(r"^\[[A-Z0-9]{3}\].*", member.display_name):
            nick_in_eee_guild = vars.eee_guild.get_member(
                member.id).display_name
            await member.edit(nick=nick_in_eee_guild)

    for member in vars.student_role.members:
        student_id = int(
            re.search(literals.regex_student['id'], member.display_name).group(0))
        if student_id not in vars.df_student.index:
            await member.edit(roles=[], nick=None)
        else:
            _ = await verify_student(member, student_id)

    await ctx.followup.send(content="Done checking everyone!", ephemeral=True)


@bot.slash_command(name="check-faculties", description="Verifies unverified faculty nicknames (same as EEE guild) and assigns roles by routine.")
@bot_admin_and_higher()
async def check_faculties(ctx):
    # await ctx.defer(ephemeral=True)
    for member in vars.faculty_role.members:
        if not re.search(r"^\[[A-Z0-9]{3}\].*", member.display_name):
            nick_in_eee_guild = vars.eee_guild.get_member(
                member.id).display_name
            await member.edit(nick=nick_in_eee_guild)
        print(f"checking {member.display_name}")
        await assign_sections(member)
    await ctx.followup.send(content="Done checking faculties!", ephemeral=True)


@bot.slash_command(name="post-faculty-section", description="Posts a button for faculties to auto assign section roles.")
@bot_admin_and_higher()
async def post_faculty_section(ctx):
    await ctx.respond(content=literals.messages['faculty_assign'],
                      view=AssignSectionsView())


@bot.slash_command(name="post-verify", description="Posts a button for students to verify.")
@bot_admin_and_higher()
async def post_verify(ctx):
    await ctx.respond(literals.messages['student_verify'],
                      view=VerificationButtonView())


@bot.slash_command(name="post-rules", description="Posts general rules.")
@bot_admin_and_higher()
async def post_rules(ctx):
    await ctx.respond(literals.messages['general_rules'],
                      view=VerificationButtonView())


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


@bot.slash_command(name="sync-sheets", description="Sync updates from enrolment sheet and marks sheets with bot.")
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


@bot.slash_command(name="get-links", description="Get the links for discord invite, enrolment and marks sheets")
@faculty_and_higher()
async def get_links(ctx):
    await ctx.defer(ephemeral=True)
    discord_link = info["invite"]
    enrolment_id = info["enrolment"]
    marks_ids = info["marks"]

    msg = f"Discord Invite Link: <{discord_link}>\n\n"
    msg += f"Enrolment Manager Sheet: <{get_link_from_sheet_id(enrolment_id)}>\n\n"
    for sec in marks_ids:
        msg += f"Section {sec} Marks Sheet: <{get_link_from_sheet_id(marks_ids[sec])}>\n"

    await ctx.followup.send(content=msg, ephemeral=True)


@bot.slash_command(name="post-as-bot", description="Finds a message by id and posts a copy of it in the specified channel")
@bot_admin_and_higher()
async def post_as_bot(ctx, message_id, channel: discord.TextChannel):
    await ctx.defer(ephemeral=True)
    message = await ctx.channel.fetch_message(message_id)
    files = []
    for attachment in message.attachments:
        await attachment.save(attachment.filename)
        files.append(discord.File(attachment.filename))
    await channel.send(content=message.content, embeds=message.embeds, files=files)
    await ctx.followup.send(f"Posted {message.jump_url} to {channel.mention}", ephemeral=True)


@bot.slash_command(name="update-section-marks", description="Update marks of the current channel")
@faculty_and_higher()
async def update_section_marks(ctx):
    await ctx.defer(ephemeral=True)
    category_name = ctx.channel.category.name  # only THEORY or LAB
    try:
        sec = int(re.search(r'^SECTION ([0-9]+)',
                  category_name.upper()).group(1))
        await update_sec_marks(info, sec, ctx)
    except:
        await ctx.followup.send(f"Message sent under {category_name} category."
                                f"This channel is not under a theory/lab section. "
                                f"Please post in a theory/lab channel.", ephemeral=True)


def format_marks_in_embed(data, total):
    if type(data) in [int, float]:
        return f"**[{data}](https://github.com/shs-cse/discord-bot)** _out of {total}_"
    else:
        return "_Not attended_"


def create_marks_embed(student, student_id, assessment_name, assessment_marks, assessment_children, final_total, final_grade, is_final_total_best_possible):
    section = vars.df_student.at[student_id, 'Section']
    name = vars.df_student.at[student_id, 'Name']
    gsuite = vars.df_student.at[student_id, 'Gsuite']
    if gsuite:
        gsuite = f"[{gsuite}](https://mail.google.com/mail/u/0/#inbox?compose=new&to={gsuite})"
    else:
        gsuite = ""
    # show actual or best possible total marks and grade
    if is_final_total_best_possible:
        summary = f"At this point, the highest total score possible for you is {format_marks_in_embed(final_total,100)} marks (grade: **{final_grade}**)."
    else:
        summary = f"You have secured {format_marks_in_embed(final_total,100)} marks (_grade:_ **{final_grade}**) in this course."
    # create embed
    embed = discord.Embed(
        title=f"{assessment_name} Marks",
        description=f"_`       User: `_ {student.mention} \n"
                    f"_` Student ID: `_ **{student_id}** \n"
                    f"_`    Section: `_ **{section:02d}** \n"
                    f"_`       Name: `_ **{name}** \n"
                    f"_`     Gsuite: `_ {gsuite} \n"
                    f"\u200b\n"
                    f"{summary}\n"
                    f"\u200b",
        color=0xe74c3c
    )
    embed.add_field(
        name=f"{assessment_name} Marks",
        value=format_marks_in_embed(
            # [0] is necessary if assessment_marks is a df. Not need if series.
            assessment_marks[student_id][0], assessment_marks['Total Marks'][0]
        ) + "\n\u200b",
        inline=False
    )
    # embed.add_field(
    #     name="Bonus Marks", value=f"{0} out of {2}\n\u200b", inline=True)
    for child in assessment_children.index:
        data = assessment_children.at[child, student_id]
        total = assessment_children.at[child, 'Total Marks']
        isnumeric = type(total) in [
            int, float]
        if isnumeric:
            embed.add_field(
                name=f"{child} Marks",
                value=format_marks_in_embed(data, total) + "\n\u200b",
                inline=True
            )
        else:
            embed.add_field(
                name=child,
                value=f"{data}\n\u200b",
                inline=False
            )
    return embed


def create_breakdown_dropdown(student, student_id, marks, further_breakdown_dict):
    class BreakdownSelectionView(discord.ui.View):
        def __init__(self):
            self.timeout = 30
            self.disable_on_timeout = True
            super().__init__(timeout=self.timeout,
                             disable_on_timeout=self.disable_on_timeout)

        @discord.ui.select(
            placeholder="Select within 30 seconds for further breakdowns",
            options=[
                discord.SelectOption(
                    label=assessment_name,
                    value=assessment_col
                ) for assessment_name, assessment_col in further_breakdown_dict.items()
            ]
        )
        async def select_callback(self, select, interaction):
            await interaction.response.defer(ephemeral=True)
            assessment_col = int(select.values[0])
            try:
                published_marks, assessment_name, assessment_marks, assessment_children = get_assessment_info(
                    marks, assessment_col)
                embed, view = create_embed_and_dropdown(
                    student, student_id, published_marks, assessment_name, assessment_marks, assessment_children)
                if view:
                    await interaction.followup.send(ephemeral=True, embed=embed, view=view)
                else:
                    await interaction.followup.send(ephemeral=True, embed=embed)
            except:
                await interaction.followup.send(
                    f"**{assessment_name}** Marks have not yet been published.", ephemeral=True)
    return BreakdownSelectionView()


def get_assessment_info(marks, assessment_col):
    published_marks = marks[marks['Publish?']]
    # fetch assessment marks
    assessment_marks = published_marks[published_marks['Self Column']
                                       == assessment_col]
    assessment_name = assessment_marks.index[0]
    assessment_children = published_marks[published_marks['Parent Column']
                                          == assessment_col]
    return published_marks, assessment_name, assessment_marks, assessment_children


def create_embed_and_dropdown(student, student_id, published_marks, assessment_name, assessment_marks, assessment_children):
    # fetch total and grade
    final_total = published_marks.at['Total', student_id]
    final_grade = published_marks.at['Grade', student_id]
    is_final_total_best_possible = not published_marks.at['Total',
                                                          'Actual Marks?']
    # now prepare embed to show this result
    embed = create_marks_embed(
        student, student_id, assessment_name, assessment_marks, assessment_children, final_total, final_grade, is_final_total_best_possible)
    # now prepare dropdown
    assessment_children = assessment_children.astype(str)
    further_breakdown_df = assessment_children['Self Column'][
        assessment_children['Children Columns'] != '']
    if not further_breakdown_df.empty:
        view = create_breakdown_dropdown(
            student,
            student_id,
            published_marks,
            further_breakdown_df.to_dict())
        return embed, view
    else:
        return embed, None


async def get_student_assessment_list(ctx: discord.AutocompleteContext):
    try:
        student = get_member(ctx.options['student'])
        if vars.student_role not in student.roles:
            return []
        sec = vars.df_marks_section.xs(
            student.id, level='Discord ID')['Marks Section']
        sec = sec.values[0]  # int value
        return vars.dict_sec_marks_assessments[sec]
    except:
        return []


async def show_marks(student, assessment_col, ctx=None, interaction=None):
    async def send_message(*args, **kwargs):
        if ctx:
            await ctx.followup.send(*args, **kwargs)
        else:
            await interaction.response.send_message(*args, **kwargs)
    # actual logics
    if student not in vars.student_role.members:
        await send_message(
            f"Can not retrieve marks since {student.mention} is not a verified student.", ephemeral=True)
    else:
        student_id = int(
            re.search(literals.regex_student['id'], student.display_name).group(0))
        marks = get_df_marks_by_student_id(student_id)
        if marks is not None:
            try:
                published_marks, assessment_name, assessment_marks, assessment_children = get_assessment_info(
                    marks, assessment_col)
                embed, view = create_embed_and_dropdown(
                    student, student_id, published_marks, assessment_name, assessment_marks, assessment_children)
                if view:
                    await send_message(ephemeral=True, embed=embed, view=view)
                else:
                    await send_message(ephemeral=True, embed=embed)
            except:
                await send_message(
                    f"**{assessment_name}** Marks have not yet been published.", ephemeral=True)
        else:
            await send_message(f"No marks record found for {student.mention}", ephemeral=True)


@ bot.slash_command(name="fetch-marks", description="Fetch marks of a particular student.")
@ faculty_and_higher()
async def fetch_marks(ctx,
                      student: discord.Member,
                      assessment: discord.Option(
                          int,
                          autocomplete=discord.utils.basic_autocomplete(
                              get_student_assessment_list)
                      )):
    await ctx.defer(ephemeral=True)
    await show_marks(student, assessment, ctx=ctx)


async def get_sec_assessment_list(ctx: discord.AutocompleteContext):
    try:
        category_name = ctx.interaction.channel.category.name
        sec = int(re.search(r'^SECTION ([0-9]+)',
                  category_name.upper()).group(1))
        return vars.dict_sec_marks_assessments[sec]
    except:
        return []


@ bot.slash_command(name="post-marks", description="Fetch marks of a particular student.")
@ faculty_and_higher()
async def post_marks(ctx,
                     assessment: discord.Option(
                         int,
                         autocomplete=discord.utils.basic_autocomplete(
                             get_sec_assessment_list)
                     )):
    await ctx.defer(ephemeral=True)
    # build custom id from section and assessment
    category_name = ctx.interaction.channel.category.name
    sec = int(re.search(r'^SECTION ([0-9]+)',
                        category_name.upper()).group(1))
    marks = vars.dict_df_marks[sec][
        list(literals.info_row_dict)
    ]
    _, assessment_name, _, _ = get_assessment_info(
        marks, assessment)  # assessmet_col -> assessment_name
    # create show marks button

    class ShowMarksButtonView(discord.ui.View):
        @discord.ui.button(label=f"{assessment_name} Marks", style=discord.ButtonStyle.primary)
        async def button_callback(self, button, interaction):
            await show_marks(interaction.user, assessment, interaction=interaction)
    await ctx.followup.send('@everyone Press the button below to show marks.', view=ShowMarksButtonView(timeout=None))

    # @ bot.slash_command()
    # @ bot_admin_and_higher()
    # async def test_embed(ctx,
    #                      student: discord.Member,
    #                      assessment: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_student_assessment_list))):
    #     await ctx.defer(ephemeral=True)
    #     student_id = int(
    #         re.search(literals.regex_student['id'], student.display_name).group(0))
    #     section = vars.df_student.at[student_id, 'Section']
    #     name = vars.df_student.at[student_id, 'Name']
    #     gsuite = vars.df_student.at[student_id, 'Gsuite']
    #     if gsuite:
    #         gsuite = f"[{gsuite}](https://mail.google.com/mail/u/0/#inbox?compose=new&to={gsuite})"
    #     else:
    #         gsuite = "_Not found_"
    #     embed = discord.Embed(
    #         title="Quiz 3 Marks",
    #         description=f"_`       User: `_ {student.mention} \n"
    #                     f"_` Student ID: `_ **{student_id}** \n"
    #                     f"_`    Section: `_ **{section:02d}** \n"
    #                     f"_`       Name: `_ **{name}** \n"
    #                     f"_`     Gsuite: `_ {gsuite} \n"
    #                     f"\u200b"
    #     )
    #     embed.add_field(
    #         name="Marks", value=f"{16} out of {20}\n\u200b", inline=True)
    #     embed.add_field(
    #         name="Bonus Marks", value=f"{0} out of {2}\n\u200b", inline=True)
    #     embed.add_field(
    #         name="Comment (if any)", value="Need to study more\n\u200b", inline=False)
    #     embed.add_field(
    #         name="Question 1 Marks", value=f"{16} out of {20}\n\u200b", inline=True)
    #     # embed.set_footer(
    #     #     text="Select an option below to show further marks breakdown."
    #     # )
    #     await ctx.followup.send(ephemeral=True, embed=embed, view=BreakdownSelectionView(timeout=30))

    # # need to change this parts. (old code marks)
    # async def get_marks_categories(ctx: discord.AutocompleteContext):
    #     return vars.marks_categories

    # @bot.slash_command(name="fetch-marks", description="Fetch marks of a particular student.")
    # @faculty_and_higher()
    # async def fetch_marks(ctx,
    #                       member: discord.Member,
    #                       category: discord.Option(str,
    #                                                autocomplete=discord.utils.basic_autocomplete(get_marks_categories))):
    #     await ctx.defer(ephemeral=True)
    #     # check if member is a verified student
    #     if member not in vars.student_role.members:
    #         await ctx.followup.send(f"Can not retrieve marks since {member.mention} is not a verified student.")
    #     else:
    #         marks = vars.df_marks.loc[member.id].xs(category, level=1)[0]
    #         marks_child = vars.df_marks.loc[member.id, category]
    #         await ctx.followup.send(f"Marks for {member.mention}:\n{category}:{marks}\n{marks_child.to_dict()}")

    # mainly for debugging...
    # async def autocomplete_df_selection(ctx: discord.AutocompleteContext):
    #     return ["Student", "Routine"]

    # @bot.slash_command(name = "show-dataframe", description="Shows the head of the selected dataframe")
    # @bot_admin_and_higher()
    # async def show_dataframe(ctx, dataframe: discord.Option(str, "Which DF", autocomplete=autocomplete_df_selection)):
    #     fig, ax = plt.subplots(1, 1, figsize=(140, 10), dpi=160, frameon=False) # no visible frame
    #     ax.xaxis.set_visible(False)
    #     ax.yaxis.set_visible(False)
    #     if dataframe == "Student":
    #         table(ax, vars.df_student.head())
    #     else:
    #         table(ax, vars.df_routine.head())
    #     plt.savefig('mytable.png', dpi=160)
    #     await ctx.respond("Here is the dataframe head", file=discord.File('mytable.png'), ephemeral=True)

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
