import asyncio
import datetime
import json
import random
from datetime import date
from datetime import timedelta
from sqlite3 import IntegrityError

import discord
import pytz
import requests
from discord import Color, Option, DMChannel
from discord.ext import commands
from discord.ui import Modal, InputText, View
from discord.utils import get
from tqdm import tqdm

import utils
from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog dette')
    bot.add_cog(Dette(bot))


class dette(commands.Cog):
  
  def __init__(self, bot: GuyaBot):
    self.bot = bot

  create = discord.SlashCommandGroup("dette", "dette related commands")

  # Command /remove-user
  @commands.slash_command(name="ajout-dette", description="Ajoute une dette", default_permission=False)
  @commands.has_any_role(config["roles"]["grades"]["officier"])
  async def ajout_dette(self, ctx: discord.ApplicationContext, de: Option(str, "Entre le pseudo de la personne qui doit de l'argent"), a: Option(str, "Entrer le pseudo de la personne a qui l'argent est du"), montant: Option(int, "Entrer le montant de la dette")):
    
    await ctx.respond(f"ajout d'une dette de {de} a {a} d'un montant de {montant}")
