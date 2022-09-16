import discord
from discord import Color

from main import GuyaBot


def create_embed(bot: GuyaBot, title=None, description=None, color: Color = None):
    embed = discord.Embed(title=title, description=description, color=color or Color.embed_background())
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.set_footer(text="Bot by Mattyee#0001, Tominix356#8302 & DenisD3D#6912")
    embed.set_thumbnail(url=bot.user.avatar.url)
    return embed
