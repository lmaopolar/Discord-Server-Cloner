import re, asyncio
import discord
from discord import app_commands, PermissionOverwrite, Colour
from aiohttp import ClientSession

TOKEN = "YOUR_TOKEN_HERE"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def extract_code(s: str) -> str:
    m = re.search(r"(?:discord\.new/|discord\.com/template/)?([A-Za-z0-9]{2,})$", s.strip())
    return m.group(1) if m else s.strip()

async def fetch_template(code: str):
    url = f"https://discord.com/api/v10/guilds/templates/{code}"
    async with ClientSession() as sess:
        async with sess.get(url) as r:
            if r.status != 200:
                return None
            return await r.json()

def perm_overwrite_from_raw(raw, role_map, member_map):
    overwrites = {}
    for ow in raw or []:
        t = ow.get("type")
        tid = str(ow.get("id"))
        allow = discord.Permissions(int(ow.get("allow", 0)))
        deny = discord.Permissions(int(ow.get("deny", 0)))
        target = None
        if t == 0:
            target = role_map.get(tid)
        elif t == 1:
            target = member_map.get(tid)
        if target is not None:
            overwrites[target] = PermissionOverwrite.from_pair(allow, deny)
    return overwrites

async def create_roles(guild: discord.Guild, roles_data):
    templ_id_to_role = {}
    base_order = sorted(roles_data, key=lambda r: r.get("position", 0))
    for r in base_order:
        if r.get("name") == "@everyone":
            templ_id_to_role[str(r["id"])] = guild.default_role
            continue
        if r.get("managed") or r.get("tags"):
            continue
        perms = discord.Permissions(int(r.get("permissions", 0)))
        colour = Colour(r.get("color", 0))
        role = await guild.create_role(name=r.get("name","New Role"), permissions=perms, hoist=r.get("hoist", False), mentionable=r.get("mentionable", False), colour=colour, reason="Template clone by Polar")
        templ_id_to_role[str(r["id"])] = role
    try:
        positions = {}
        for r in base_order:
            if r.get("name") == "@everyone":
                continue
            new = templ_id_to_role.get(str(r["id"]))
            if new:
                positions[new] = r.get("position", new.position)
        if positions:
            await guild.edit_role_positions(positions=positions)
    except:
        pass
    return templ_id_to_role

async def create_structure(guild: discord.Guild, data):
    serialized = data.get("serialized_source_guild") or {}
    roles_data = serialized.get("roles", [])
    channels_data = serialized.get("channels", [])
    role_map = await create_roles(guild, roles_data)
    member_map = {}
    cat_data = [c for c in channels_data if c.get("type") == 4]
    ch_data = [c for c in channels_data if c.get("type") != 4]
    id_to_category = {}
    for c in sorted(cat_data, key=lambda x: x.get("position", 0)):
        ow = perm_overwrite_from_raw(c.get("permission_overwrites"), role_map, member_map)
        cat = await guild.create_category(name=c.get("name","category"), overwrites=ow, position=c.get("position", None), reason="Template clone by Polar")
        id_to_category[str(c["id"])] = cat
        if c.get("nsfw"):
            try:
                await cat.edit(nsfw=True, reason="Template clone by Polar")
            except:
                pass
    for c in sorted(ch_data, key=lambda x: (x.get("position", 0), x.get("name",""))):
        parent = id_to_category.get(str(c.get("parent_id"))) if c.get("parent_id") else None
        ow = perm_overwrite_from_raw(c.get("permission_overwrites"), role_map, member_map)
        if c.get("type") == 0:
            ch = await guild.create_text_channel(name=c.get("name","text"), overwrites=ow, category=parent, position=c.get("position", None), topic=c.get("topic"), nsfw=c.get("nsfw", False), reason="Template clone by Polar")
            if c.get("rate_limit_per_user"):
                try:
                    await ch.edit(slowmode_delay=int(c.get("rate_limit_per_user",0)), reason="Template clone by Polar")
                except:
                    pass
        elif c.get("type") == 2:
            bitrate = c.get("bitrate", 64000)
            user_limit = c.get("user_limit", 0)
            await guild.create_voice_channel(name=c.get("name","voice"), overwrites=ow, category=parent, position=c.get("position", None), bitrate=bitrate, user_limit=user_limit, reason="Template clone by Polar")
        elif c.get("type") == 5:
            ch = await guild.create_text_channel(name=c.get("name","announcement"), overwrites=ow, category=parent, position=c.get("position", None), topic=c.get("topic"), nsfw=c.get("nsfw", False), reason="Template clone by Polar")
            try:
                await ch.edit(type=discord.ChannelType.news, reason="Template clone by Polar")
            except:
                pass

@tree.command(name="apply_template", description="Clone a Discord template into this server. Made by Polar.")
@app_commands.describe(template="Template code or link")
async def apply_template(interaction: discord.Interaction, template: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to run this. Made by Polar.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    code = extract_code(template)
    data = await fetch_template(code)
    if not data or not data.get("serialized_source_guild"):
        await interaction.followup.send("Invalid or unsupported template. Made by Polar.", ephemeral=True)
        return
    try:
        await create_structure(interaction.guild, data)
        await interaction.followup.send("Template applied to this server. Made by Polar.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed to apply template: {e}. Made by Polar.", ephemeral=True)

@tree.command(name="ping", description="Health check. Made by Polar.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong. Made by Polar.", ephemeral=True)

@client.event
async def on_ready():
    try:
        await tree.sync()
    except:
        pass
    activity = discord.Game(name="Made by Polar")
    await client.change_presence(activity=activity)
    print("Online. Made by Polar")

def main():
    client.run(TOKEN)

if __name__ == "__main__":
    main()