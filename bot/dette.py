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
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dette (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_debiteur TEXT NOT NULL,
            id_crediteur TEXT NOT NULL,
            montant INTEGER NOT NULL,
            description TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
        ''')

        conn.commit()
        conn.close()

    def add_dette(self, id_debiteur, id_crediteur, montant, description):
        conn = sqlite3.connect('votre_base_de_donnees.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO dette (id_debiteur, id_crediteur, montant, description, active) VALUES (?, ?, ?, ?, 1)",
                       (id_debiteur, id_crediteur, montant, description))

        conn.commit()
        conn.close()

    @commands.slash_command(name="ajout-dette", description="Ajoute une dette", default_permission=False)
    async def ajout_dette(self, ctx: ApplicationContext, 
                          de: Option(Member, "Sélectionnez la personne qui doit de l'argent"), 
                          a: Option(Member, "Sélectionnez la personne à qui l'argent est dû"), 
                          montant: Option(int, "Entrez le montant de la dette"),
                          description: Option(str, "Entrez une description de la dette", required=False)):
        
        self.add_dette(de.id, a.id, montant, description)
        await ctx.respond(f"Ajout d'une dette de {de.mention} à {a.mention} d'un montant de {montant}. Description: {description}")

    def get_dettes_debiteur(self, id_debiteur):
        conn = sqlite3.connect('votre_base_de_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dette WHERE id_debiteur = ? AND active = 1", (id_debiteur,))
        dettes = cursor.fetchall()
        conn.close()
        return dettes

    def get_dettes_crediteur(self, id_crediteur):
        conn = sqlite3.connect('votre_base_de_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dette WHERE id_crediteur = ? AND active = 1", (id_crediteur,))
        dettes = cursor.fetchall()
        conn.close()
        return dettes

    def get_resume_dettes(self):
        conn = sqlite3.connect('votre_base_de_donnees.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id_debiteur, id_crediteur, SUM(montant) as total FROM dette WHERE active = 1 GROUP BY id_debiteur, id_crediteur")
        dettes = cursor.fetchall()

        resume = {}
        for dette in dettes:
            debiteur, crediteur, montant = dette
            if debiteur not in resume:
                resume[debiteur] = {}
            if crediteur not in resume[debiteur]:
                resume[debiteur][crediteur] = 0
            resume[debiteur][crediteur] += montant
            if crediteur in resume and debiteur in resume[crediteur]:
                if resume[debiteur][crediteur] > resume[crediteur][debiteur]:
                    resume[debiteur][crediteur] -= resume[crediteur][debiteur]
                    del resume[crediteur][debiteur]
                else:
                    resume[crediteur][debiteur] -= resume[debiteur][crediteur]
                    del resume[debiteur][crediteur]

        conn.close()
        return resume

    @commands.slash_command(name="mes_dettes", description="Affiche les dettes que j'ai envers d'autres personnes")
    async def mes_dettes(self, ctx: ApplicationContext):
        dettes = self.get_dettes_debiteur(str(ctx.author.id))
        embed = Embed(title="Mes Dettes", color=0x00ff00)
        for dette in dettes:
            _, id_crediteur, montant, description, _ = dette
            embed.add_field(name=f"Créditeur: {id_crediteur}", value=f"Montant: {montant}\nDescription: {description}", inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="dettes_envers_moi", description="Affiche les dettes que d'autres ont envers moi")
    async def dettes_envers_moi(self, ctx: ApplicationContext):
        dettes = self.get_dettes_crediteur(str(ctx.author.id))
        embed = Embed(title="Dettes envers Moi", color=0x00ff00)
        for dette in dettes:
            id_debiteur, _, montant, description, _ = dette
            embed.add_field(name=f"Débiteur: {id_debiteur}", value=f"Montant: {montant}\nDescription: {description}", inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="resume_dettes", description="Affiche un résumé de toutes les dettes")
    async def resume_dettes(self, ctx: ApplicationContext):
        resume = self.get_resume_dettes()
        embed = Embed(title="Résumé des Dettes", color=0x00ff00)
        for debiteur in resume:
            for crediteur in resume[debiteur]:
                montant = resume[debiteur][crediteur]
                embed.add_field(name=f"Débiteur: {debiteur} → Créditeur: {crediteur}", value=f"Montant: {montant}", inline=False)
        await ctx.respond(embed=embed)
