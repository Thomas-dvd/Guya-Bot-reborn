import asyncio
import datetime
import json
import random
from datetime import date
from datetime import timedelta
import sqlite3
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


class Dette(commands.Cog):

    def __init__(self, bot: GuyaBot):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dette (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_debiteur INTEGER NOT NULL,
            id_crediteur INTEGER NOT NULL,
            name_debiteur TEXT NOT NULL,
            name_crediteur TEST NOT NULL,
            montant INTEGER NOT NULL,
            description TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
        ''')

        conn.commit()
        conn.close()

    def add_dette(self, id_debiteur, id_crediteur, name_debiteur, name_crediteur, montant, description):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO dette (id_debiteur, id_crediteur, name_debiteur, name_crediteur, montant, description, active) VALUES (?, ?, ?, ?, ?, ?, 1)",
                       (id_debiteur, id_crediteur, name_debiteur, name_crediteur, montant, description))

        conn.commit()
        conn.close()

    @commands.slash_command(name="ajout-dette", description="Ajoute une dette", default_permission=False)
    async def ajout_dette(self, ctx: discord.ApplicationContext, 
                          de: Option(discord.User, "Sélectionnez la personne qui doit de l'argent"), 
                          a: Option(discord.User, "Sélectionnez la personne à qui l'argent est dû"), 
                          montant: Option(int, "Entrez le montant de la dette"),
                          description: Option(str, "Entrez une description de la dette", required=False)):
        
        self.add_dette(de.id, a.id, de.name, a.name, montant, description)
        await ctx.respond(f"Ajout d'une dette de {de.mention} à {a.mention} d'un montant de {montant}. Description: {description}")

    def get_dettes_debiteur(self, id_debiteur):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dette WHERE id_debiteur = ? AND active = 1", (id_debiteur,))
        dettes = cursor.fetchall()
        conn.close()
        return dettes

    def get_dettes_crediteur(self, id_crediteur):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dette WHERE id_crediteur = ? AND active = 1", (id_crediteur,))
        dettes = cursor.fetchall()
        conn.close()
        return dettes

   
    def get_resume_dettes(self):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, id_debiteur, id_crediteur, name_debiteur, name_crediteur, montant, description FROM dette WHERE active = 1")
        dettes = cursor.fetchall()

        resume = {}
        for dette in dettes:
            id_dette, id_debiteur, id_crediteur, name_debiteur, name_crediteur, montant, description = dette
            key = (name_debiteur, name_crediteur)

            if key not in resume:
                resume[key] = {'total': 0, 'dettes': []}

            resume[key]['total'] += montant
            resume[key]['dettes'].append(f"{id_dette}: {description} - {montant}")

        # Compensation des dettes réciproques
        keys_a_traiter = list(resume.keys())
        for key in keys_a_traiter:
            if key in resume and key[::-1] in resume:
                debiteur, crediteur = key
                inverse_key = (crediteur, debiteur)

                if resume[key]['total'] > resume[inverse_key]['total']:
                    montant_compensation = resume[inverse_key]['total']
                    dettes_compensées = '\n'.join(f"        {dette}" for dette in resume[inverse_key]['dettes'])
                    resume[key]['total'] -= montant_compensation
                    resume[key]['dettes'].append(f"    Compensation pour dette inverse de {montant_compensation}:\n{dettes_compensées}")
                    del resume[inverse_key]
                elif resume[key]['total'] < resume[inverse_key]['total']:
                    montant_compensation = resume[key]['total']
                    dettes_compensées = '\n'.join(f"        {dette}" for dette in resume[key]['dettes'])
                    resume[inverse_key]['total'] -= montant_compensation
                    resume[inverse_key]['dettes'].append(f"    Compensation pour dette inverse de {montant_compensation}:\n{dettes_compensées}")
                    del resume[key]
                else:
                    del resume[key]
                    del resume[inverse_key]

        conn.close()
        return resume


    def supprimer_dette_in_database(self, id_dette):
        conn = sqlite3.connect('dette.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE dette SET active = 0 WHERE id = ?", (id_dette,))

        conn.commit()
        conn.close()
        return None



    @commands.slash_command(name="mes_dettes", description="Affiche les dettes que j'ai envers d'autres personnes")
    async def mes_dettes(self, ctx: discord.ApplicationContext):
        dettes = self.get_dettes_debiteur(str(ctx.author.id))
        embed = discord.Embed(title="Mes Dettes", color=0x00ff00)
        for dette in dettes:
            _, _, _, _, name_crediteur, montant, description, _ = dette
            embed.add_field(name=f"Créditeur: {name_crediteur}", value=f"Montant: {montant}\nDescription: {description}", inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="dettes_envers_moi", description="Affiche les dettes que d'autres ont envers moi")
    async def dettes_envers_moi(self, ctx: discord.ApplicationContext):
        dettes = self.get_dettes_crediteur(str(ctx.author.id))
        embed = discord.Embed(title="Dettes envers Moi", color=0x00ff00)
        for dette in dettes:
            _, _, _, name_debiteur, _, montant, description, _ = dette
            embed.add_field(name=f"Débiteur: {name_debiteur}", value=f"Montant: {montant}\nDescription: {description}", inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="resume_dettes", description="Affiche un résumé de toutes les dettes")
    async def resume_dettes(self, ctx: discord.ApplicationContext):
        resume = self.get_resume_dettes()
        embed = discord.Embed(title="Résumé des Dettes", color=0x00ff00)

        for key, value in resume.items():
            debiteur, crediteur = key
            dettes_info = '\n'.join(f"    {dette}" for dette in value['dettes'])  # Indentation pour chaque dette
            embed.add_field(name=f"{debiteur} → {crediteur}", value=f"Montant total dû: {value['total']}\nDettes:\n{dettes_info}\n", inline=False)

        await ctx.respond(embed=embed)

    @commands.slash_command(name="supprimer_dette", description="Supprimer une dette une fois remboursé")
    async def supprimer_dette(self, ctx: discord.ApplicationContext, id_dette: Option(int, "ID de la dette a supprimer")):
        self.supprimer_dette_in_database(id_dette)
        await ctx.respond(f"Dette ID {id_dette} a été remboursée.")
