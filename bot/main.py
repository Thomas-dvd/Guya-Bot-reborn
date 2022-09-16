from dotenv import load_dotenv
import os
import sqlite3

import discord
from discord.ext import commands

import aaron
import threading

class GuyaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", case_insensitive=True, intents=discord.Intents.all())

        self.load_extensions("recrutement", "rank", "debug")

        self.db = sqlite3.connect("database.db")
        threading.Thread(target=self.start_aaron, daemon=True).start()

    def start_aaron(self):
        self.aaron = aaron.AaronApi()

    async def on_ready(self):
        print(f"{self.user.name}#{self.user.discriminator} is online !")
        game = discord.Streaming(name="un drop de T4", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        await self.change_presence(activity=game)

    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, (commands.MissingAnyRole, commands.MissingRole)):
            await ctx.respond("Tu n'a pas la permission d'executé cette commands, re-essaye et je te supprimer 🔫")
        else:
            await ctx.respond("Une erreur est survenue, on est foutuuuuuuuu 💥")
            raise error


if __name__ == '__main__':
    load_dotenv()

    guyabot = GuyaBot()
    guyabot.run(os.environ.get("TOKEN"))
