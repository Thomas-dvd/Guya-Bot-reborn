import json

from dotenv import load_dotenv
import os
import sqlite3

import discord
from discord.ext import commands

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


class GuyaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", case_insensitive=True, intents=discord.Intents.all())

        self.load_extensions("recruitement")

        self.players = sqlite3.connect("players.db")

    async def on_ready(self):
        print(f"{self.user.name}#{self.user.discriminator} is online !")
        game = discord.Streaming(name="un drop de T4", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        await self.change_presence(activity=game)
        guild = self.get_guild(config["guild_id"])
        data_log = guild.get_channel(config["channels"]["data_log"])
        await data_log.send("Bot démarré !")

    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, (commands.MissingAnyRole, commands.MissingRole)):
            await ctx.respond("Tu n'as pas la permission d'exécuter cette commande, réessaye et je te supprime 🔫")
        else:
            await ctx.respond("Une erreur est survenue, on est foutuuuuuuuu 💥")
            raise error


if __name__ == '__main__':
    load_dotenv()

    guyabot = GuyaBot()
    guyabot.run(os.environ.get("TOKEN"))
