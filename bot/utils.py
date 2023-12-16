import json

import discord
from discord import Color

from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def create_embed(bot: GuyaBot, title=None, description=None, color: Color = None):
    embed = discord.Embed(title=title, description=description, color=color or Color.embed_background())
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.set_footer(text="Bot by mattyee, tominix356, denisd3d & leherlemaxime")
    embed.set_thumbnail(url=bot.user.avatar.url)
    return embed


# database function
def database(self, table, field, value):
    cur = self.bot.players.cursor()
    temp = cur.execute(f"SELECT * FROM {table} WHERE {field}=?", [value]).fetchone()
    if temp is None:
        return None

    # Si on change cette data (relatif a la BDD, il ne faut pas oublier la fonction database_parametres ci dessous pour le /edit)
    elif table == "country":
        data = {
            "id": temp[0],
            "discord_id": temp[1],
            "ingame_name": temp[2],
            "recruitment_date": temp[3],
            "grade": temp[4],
            "country": temp[5],
            "last_connection": temp[6],
            "absence": temp[7],
            "age_badge": temp[8],
            "speaker_badge": temp[9],
            "dc_badge": temp[10],
            "schemalink_badge": temp[11],
            "soldat_badge": temp[12],
            "recruiter_badge": temp[13],
            "animator_badge": temp[14],
            "money_badge": temp[15]
        }
    else:
        data = {
            "id": temp[0],
            "discord_id": temp[1],
            "ingame_name": temp[2]
        }
    return data


# default grades
async def default_grades(self, ctx, user):
    try:
        await user.edit(nick=None)
    except discord.errors.Forbidden:
        pass
    for role in user.roles:
        try:
            if role.name != "@everyone":
                await user.remove_roles(ctx.guild.get_role(role.id))
        except discord.errors.Forbidden or discord.errors.NotFound:
            pass

    text = ""

    await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
    text += f" <@&{config['grades']['neutre']}>"

    for role in config["grades"]["deco"]["global"]:
        await user.add_roles(ctx.guild.get_role(role))
        text += f", <@&{role}>"

    embed = create_embed(self.bot, title=f"Rôles obtenus par {user.name}:", description=f"{text}", color=Color.gold())
    await ctx.channel.send(embed=embed)


# database paramètres (for /edit)
def database_parametres(setting=None, question=None, value=None):
    if setting is None:
        return ["id", "discord_id", "ingame_name", "recruitment_date", "grade", "country", "last_connection", "absence",
                "age_badge", "speaker_badge", "dc_badge", "schemalink_badge", "soldat_badge", "recruiter_badge", "animator_badge", "money_badge"]

    if question == "IsInDiplomacyDB":
        if setting in ["id", "discord_id", "ingame_name"]:
            return True
        return False

    if question == "NeedFormat":
        if setting in ["id", "discord_id", "grade", "last_connection", "age_badge", "speaker_badge", "dc_badge", "schemalink_badge", "soldat_badge", "recruiter_badge", "animator_badge"]:
            if value is None:
                return 0
            return int(value)
