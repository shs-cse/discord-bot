import vars, literals
from utils_wrapper import get_role, get_category


async def check_discord_sec(info):
    # skip section 01, works as template
    for ctype in literals.class_types:
        prev_category = get_sec_category(1, ctype)
        for sec in vars.available_sections[1:]:
            role = get_sec_role(sec, ctype)
            if not role:
                role = await create_sec_role(sec, ctype)
            category = get_sec_category(sec, ctype)
            if not category:
                category = await create_sec_category(sec, ctype, role)
            # reorder: theory of all sections, then labs of all sections
            await category.move(after=prev_category)
            prev_category = category


async def create_sec_role(section, class_type):
    template_role = get_sec_role(1, class_type)
    role_name = get_sec_role_name(section, class_type)
    print(f"Creating role: {role_name}...")
    new_role = await vars.guild.create_role(name=role_name, 
                                       permissions=template_role.permissions, 
                                       colour=template_role.colour)
    print("Done!\n")
    return new_role


async def create_sec_category(section, class_type, new_role):
    template_role = get_sec_role(1, class_type)
    template_category = get_sec_category(1, class_type)
    # clone category with permissions
    category_name = get_sec_category_name(section, class_type)
    print(f"Creating category: {category_name}...")
    new_category = await template_category.clone(name=category_name)
    await change_permissions(template_category, template_role, new_category, new_role)
    # clone every channel with permissions
    for template_channel in template_category.channels:
        print(f"┝━━{template_channel.name}")
        new_channel = await template_channel.clone()
        await change_permissions(template_channel, template_role, new_channel, new_role)
        await new_channel.edit(category=new_category, position=template_channel.position)
    print("Done!\n")
    return new_category


async def change_permissions(from_channel, from_role, to_channel, to_role):
    overwrite = from_channel.overwrites[from_role]
    await to_channel.set_permissions(from_role, overwrite=None)
    await to_channel.set_permissions(to_role, overwrite=overwrite)



def get_sec_role_name(section, class_type):
    return literals.sec_role_name_format[class_type].format(section)

def get_sec_role(*args, **kwargs):
    return get_role(get_sec_role_name(*args, **kwargs))



def get_sec_category_name(section, class_type):
    return literals.sec_category_name_format[class_type].format(section)

def get_sec_category(*args, **kwargs):
    return get_category(get_sec_category_name(*args, **kwargs))

    

# mainly for debugging...
async def bulk_delete_category(section, class_type):
    if section == 1:
        return "can't delete template section=01"
    category = get_sec_category(section, class_type)
    if not category:
        return "category does not exist."
    for channel in category.channels:
        await channel.delete()
        print(f"deleted {channel=}")
    await category.delete()
    return f"deleted {category.name=}"
