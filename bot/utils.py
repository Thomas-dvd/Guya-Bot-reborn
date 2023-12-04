import discord
from discord import Color

from main import GuyaBot


def create_embed(bot: GuyaBot, title=None, description=None, color: Color = None):
    embed = discord.Embed(title=title, description=description, color=color or Color.embed_background())
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.set_footer(text="Bot by mattyee, tominix356, denisd3d & leherlemaxime")
    embed.set_thumbnail(url=bot.user.avatar.url)
    return embed


# database function
def database(self, table, field, value):
    cur = self.bot.players.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {field}={value}")
    temp = cur.fetchone()
    if temp is None:
        return None
    elif table == "country":
        data = {
            "id": temp[0],
            "discord_id": temp[1],
            "ingame_name": temp[2],
            "recruitment_date": temp[3],
            "grade": temp[4],
            "country": temp[5],
            "statut": temp[6],
            "age_badge": temp[7],
            "speaker_badge": temp[8],
            "dc_badge": temp[9],
            "schemalink_badge": temp[10],
            "soldat_badge": temp[11],
            "recruiter_badge": temp[12],
            "animator_badge": temp[13]
        }
    else:
        data = {
            "id": temp[0],
            "discord_id": temp[1],
            "ingame_name": temp[2]
        }
    return data
