import asyncio
import datetime
import json
from datetime import date, timedelta

import discord
import requests
from discord import Option, Forbidden, Color
from discord.ext import commands
from discord.ui import View
from tqdm import tqdm

import utils
from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog debug')
    bot.add_cog(Debug(bot))


NOMBRE_MEMBRE_PAR_STEP = config["force_check_actualisation"]


class Debug(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # Cooldown pour le Check de la db diplomatique et de pays
    async def start_check_loop(self):
        while True:
            await asyncio.create_task(self.recrutement_check())
            await asyncio.sleep(12 * 60 * 60)
            await asyncio.create_task(self.diplomatique_check())
            await asyncio.sleep(12 * 60 * 60)

    # ------------------------------------------------------------------------------------------
    #                                         Commands
    # ------------------------------------------------------------------------------------------

    # groupe create
    forcecheck = discord.SlashCommandGroup("forcecheck", "forcecheck related commands")

    # Command /informations
    @commands.slash_command(description="Donne toute les informations d'une personne.", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def informations(self, ctx: discord.ApplicationContext,user: Option(discord.User, "Entre un utilisateur.", required=True),de: Option(str, "db de pays ou de diplomatie.", choices=["Pays", "Diplomatie"],required=False, default="Pays")):

        if de == "Pays":
            cur = self.bot.countrydb.cursor()
            cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            if temp is None:
                await ctx.respond("Utilisateur absent de la base de donnée de pays")
                return
            cur.close()

            age = (date.today().year - temp[3]) if temp[3] != -1 else -1

            embed = utils.create_embed(self.bot, f"Informations de {user}", color=Color.brand_red())
            embed.add_field(name="ID Système :", value=f"{temp[0]}")
            embed.add_field(name="ID discord :", value=f"{temp[1]}")
            embed.add_field(name="Pseudo IG :", value=f"{temp[2]}")
            embed.add_field(name="Age :", value=f"{age}")
            embed.add_field(name="Experience :", value=f"{temp[4]}")
            embed.add_field(name="Grade :", value=f"{temp[5]}")
            embed.add_field(name="Pays :", value=f"{temp[6]}")
            embed.add_field(name="Peut quitter le pays :", value=f"{temp[7]}")
            embed.add_field(name="Date recrutement :", value=f"{temp[8]}")
            embed.add_field(name="Ancienneté :", value=f"{temp[9]}")
            embed.add_field(name="Schématique :", value=f"{temp[10]}")
            embed.add_field(name="Régiment :", value=f"{temp[11]}")
            embed.add_field(name="Dernière connexion :", value=f"{temp[12]}")
            embed.add_field(name="Fin d'absence :", value=f"{temp[13]}")
            embed.add_field(name="Référent :", value=f"{temp[14]}")

            await ctx.respond(embed=embed)

        else:
            cur = self.bot.worlddb.cursor()
            cur.execute("SELECT * FROM diplomatie WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            if temp is None:
                await ctx.respond("Utilisateur absent de la base de donnée diplomatique")
                return
            cur.close()

            embed = utils.create_embed(self.bot, f"Informations de {user}", color=Color.brand_red())
            embed.add_field(name="ID Système :", value=f"{temp[0]}")
            embed.add_field(name="ID discord :", value=f"{temp[1]}")
            embed.add_field(name="Pseudo IG :", value=f"{temp[2]}")

            await ctx.respond(embed=embed)

    # Command /edit
    @commands.slash_command(name="édit", description="Donne toute les informations d'une personne.", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def edit(self, ctx: discord.ApplicationContext,user: Option(discord.User, "Entre un utilisateur.", required=True), donnée: Option(str,"Paramètre a modifier (Ceux marquer d'une * sont disponible pour les diplomaties.", choices=["* ID Système","*ID Discord","*Pseudo IG","Age","Experience","Grade","Pays","Peut quitter le pays","Date recrutement","Ancienneté","Schématique","Régiment","Dernière connexion","Fin d'absence","Référent"]),valeur: Option(str, "Nouvelle valeur (None pour Null).", required=True),de: Option(str, "db de pays ou de diplomatie.", choices=["Pays", "Diplomatie"], required=False,default="Pays")):

        if donnée in ["*ID Système", "ID Discord", "Age", "Grade", "Peut quitter pays", "Ancienneté", "Dernière connexion"]:
            valeur = int(valeur)
        if valeur in ["None", "none"]:
            valeur = None
        if donnée == "Age":
            valeur2 = (date.today().year - valeur) if valeur != "-1" else -1


        if de == "Pays":
            cur = self.bot.countrydb.cursor()
            cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            if temp is None:
                await ctx.respond("Utilisateur absent de la base de donnée de pays")
                return
            if donnée == "*ID Système":
                cur.execute(f"UPDATE recrutement SET id_sys=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "*ID Discord":
                cur.execute(f"UPDATE recrutement SET id_discord=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "*Pseudo IG":
                cur.execute(f"UPDATE recrutement SET pseudo_ingame=? WHERE id_discord=?", [valeur, user.id])
                headers = {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {config["api_key"]}',
                }
                response = requests.get(f'https://publicapi.nationsglory.fr/user/{valeur}', headers=headers)

                if response.status_code != 200:
                    await ctx.respond(
                        f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
                    return

                if "error" in response.json():
                    try:
                        await user.edit(nick=f"{valeur}")
                    except discord.errors.Forbidden:
                        self.bot.worlddb.commit()
                        cur.close()
                        await ctx.respond(
                            f"La donnée {donnée} du joueur {user.mention} a bien été définit sur ``{valeur}``. **Impossible cependant pour le bot de le rename.**")
                        return
                else:
                    user_grade = \
                    cur.execute("SELECT grade FROM recrutement WHERE pseudo_ingame =?", [valeur]).fetchone()[0]
                    grade_list = ["Candidat", "Recrue", "Recrue+", "Membre", "Membre+", "Officier", "Gouverneur"]
                    user_grade = grade_list[user_grade]
                    try:
                        if len(f"{user_grade} | {valeur}") <= 32:
                            await user.edit(nick=f"{user_grade} | {valeur}")
                        else:
                            await user.edit(nick=f"{valeur}")
                    except discord.errors.Forbidden:
                        self.bot.worlddb.commit()
                        cur.close()
                        await ctx.respond(
                            f"La donnée {donnée} du joueur {user.mention} a bien été définit sur ``{valeur}``. **Impossible cependant pour le bot de le rename.**")
                        return

            if donnée == "Age":
                cur.execute(f"UPDATE recrutement SET annee_naissance=? WHERE id_discord=?", [valeur2, user.id])
            if donnée == "Experience":
                cur.execute(f"UPDATE recrutement SET experience=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Grade":
                cur.execute(f"UPDATE recrutement SET grade=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Pays":
                cur.execute(f"UPDATE recrutement SET pays=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Peut quitter pays":
                cur.execute(f"UPDATE recrutement SET peut_quitter_pays=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Date recrutement":
                cur.execute(f"UPDATE recrutement SET date_recrutement=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Ancienneté":
                cur.execute(f"UPDATE recrutement SET anciennete=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Schématique":
                cur.execute(f"UPDATE recrutement SET schematique=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Régiment":
                cur.execute(f"UPDATE recrutement SET regiment=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Dernière connexion":
                cur.execute(f"UPDATE recrutement SET last_connexion=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Fin d'absence":
                cur.execute(f"UPDATE recrutement SET absence_fin=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "Référent":
                cur.execute(f"UPDATE recrutement SET referent=? WHERE id_discord=?", [valeur, user.id])
            self.bot.countrydb.commit()
            cur.close()

        else:  # BDD diplomatie
            cur = self.bot.worlddb.cursor()
            cur.execute("SELECT * FROM diplomatie WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            if temp is None:
                await ctx.respond("Utilisateur absent de la base de donnée diplomatique")
                return
            if donnée == "*ID Système":
                cur.execute(f"UPDATE diplomatie SET id_sys=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "*ID Discord":
                cur.execute(f"UPDATE diplomatie SET id_discord=? WHERE id_discord=?", [valeur, user.id])
            if donnée == "*Pseudo IG":
                cur.execute(f"UPDATE diplomatie SET pseudo_ingame=? WHERE id_discord=?", [valeur, user.id])
                headers = {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {config["api_key"]}',
                }
                response = requests.get(f'https://publicapi.nationsglory.fr/user/{valeur}', headers=headers)

                if response.status_code != 200:
                    await ctx.respond(
                        f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
                    return

                if "error" in response.json():
                    if response.json()["error"] == "unknown.user":
                        try:
                            if len(f"Unlink | {valeur}") <= 32:
                                await user.edit(nick=f"Unlink | {valeur}")
                            elif len(f"{valeur}") <= 32:
                                await user.edit(nick=f"{valeur}")
                        except discord.errors.Forbidden:
                            self.bot.worlddb.commit()
                            cur.close()
                            await ctx.respond(
                                f"La donnée {donnée} du joueur {user.mention} a bien été définit sur ``{valeur}``. **Impossible cependant pour le bot de le rename.**")
                            return
                    else:
                        await ctx.respond(
                            f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
                        return

                else:
                    api_data = {
                        "username": response.json()["username"],
                        "country": response.json()["servers"]["green"]["country"],
                        "country_rank": response.json()["servers"]["green"]["country_rank"],
                    }
                    try:
                        if len(f"{api_data['country']} | {api_data['username']} ({api_data['country_rank']})") <= 32:
                            await user.edit(
                                nick=f"{api_data['country']} | {api_data['username']} ({api_data['country_rank']})")
                        elif len(f"{api_data['country']} | {api_data['username']}") <= 32:
                            await user.edit(nick=f"{api_data['country']} | {api_data['username']}")
                        else:
                            await user.edit(nick=f"{api_data['username']}")
                    except discord.errors.Forbidden:
                        self.bot.worlddb.commit()
                        cur.close()
                        await ctx.respond(
                            f"La donnée {donnée} du joueur {user.mention} a bien été définit sur ``{valeur}``. **Impossible cependant pour le bot de le rename.**")
                        return
            self.bot.worlddb.commit()
            cur.close()

        await ctx.respond(f"La donnée {donnée} du joueur {user.mention} a bien été définit sur ``{valeur}``.")

    # Command /transfert
    @commands.slash_command(description="Transfert un joueur de base de donnée.", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def transfert(self, ctx: discord.ApplicationContext,user: Option(discord.User, "Entre un utilisateur.", required=True)):

        cur = self.bot.countrydb.cursor()
        temp = cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if temp is None:

            # transfert de diplomatie a recrutement
            cur.close()
            cur = self.bot.worlddb.cursor()
            temp = cur.execute("SELECT * FROM diplomatie WHERE id_discord=?", [user.id]).fetchone()
            cur.execute("DELETE FROM diplomatie WHERE id_discord = ?", [user.id])
            self.bot.countrydb.commit()
            cur.close()
            if temp is None:
                await ctx.respond("Utilisateur absent des deux bases de données")
                return
            data = {
                "id_discord": temp[1],
                "pseudo_ingame": temp[2],
                "annee_naissance": "-1",
                "experience": "transfert",
                "date_recrutement": date.today()
            }
            cur = self.bot.countrydb.cursor()
            cur.execute(
                "INSERT INTO recrutement (id_discord, pseudo_ingame, annee_naissance, experience, date_recrutement) VALUES (:id_discord, :pseudo_ingame, :annee_naissance, :experience, :date_recrutement)",
                data)
            self.bot.countrydb.commit()
            cur.close()
            await ctx.respond(
                f"L'utilisateur {user.mention} a bien été transférer de la base de donnée diplomatique a celle du pays. Bienvenue a lui dans le pays :wave:")

        else:

            # transfert de recrutement a diplomatie
            data = {
                "id_discord": temp[1],
                "pseudo_ingame": temp[2]
            }
            cur = self.bot.worlddb.cursor()
            cur.execute("INSERT INTO diplomatie (id_discord, pseudo_ingame) VALUES (:id_discord, :pseudo_ingame)", data)
            self.bot.worlddb.commit()
            cur.close()
            cur = self.bot.countrydb.cursor()
            cur.execute("DELETE FROM recrutement WHERE id_discord = ?", [user.id])
            self.bot.countrydb.commit()
            cur.close()
            await ctx.respond(
                f"L'utilisateur {user.mention} a bien été transférer de la base de donnée de pays a celle de diplomatie.")

    # Command /create_user
    # @commands.slash_command(name="create-user", description="Crée un utilisateur.", default_permission=False)
    # async def create_user(self, ctx: discord.ApplicationContext,user: Option(discord.User, "Entre un utilisateur.", required=True),pseudo: Option(str, "pseudo IG.", required=True),dans: Option(str, "db de pays ou de diplomatie.", choices=["Pays", "Diplomatie"],required=False, default="Pays")):
    #
    #     if dans == "Pays":
    #         data = {
    #             "id_discord": user.id,
    #             "pseudo_ingame": pseudo,
    #             "experience": "create user",
    #             "annee_naissance": "-1",
    #             "date_recrutement": date.today()
    #         }
    #         cur = self.bot.countrydb.cursor()
    #         cur.execute(
    #             "INSERT INTO recrutement (id_discord, pseudo_ingame, annee_naissance, experience, date_recrutement) VALUES (:id_discord, :pseudo_ingame, :annee_naissance, :experience, :date_recrutement)",
    #             data)
    #         self.bot.countrydb.commit()
    #         cur.close()
    #         await ctx.respond(
    #             f"L'utilisateur {user.mention} a bien été enregistrer sous le pseudo ``{pseudo}`` dans la base de donnée de pays")
    #     else:
    #         data = {
    #             "id_discord": user.id,
    #             "pseudo_ingame": pseudo,
    #         }
    #         cur = self.bot.worlddb.cursor()
    #         cur.execute("INSERT INTO diplomatie (id_discord, pseudo_ingame) VALUES (:id_discord, :pseudo_ingame)",
    #                     data)
    #         self.bot.worlddb.commit()
    #         cur.close()
    #         await ctx.respond(
    #             f"L'utilisateur {user.mention} a bien été enregistrer sous le pseudo ``{pseudo}`` dans la base de donnée diplomatique")

    # Command /referent
    @commands.slash_command(name="référent",description="Informe sur son référent et les personnes donc on est référent.",default_permission=False)
    async def referent(self, ctx: discord.ApplicationContext,user: Option(discord.User, "Entre un utilisateur.", required=True)):

        cur = self.bot.countrydb.cursor()
        temp = cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if temp is None:
            await ctx.respond("Utilisateur absent de la base de donnée de pays")
            return

        embed = utils.create_embed(self.bot, f"Référent {user}", color=Color.green())
        if temp[14] is None:
            embed.add_field(name="Référent :", value=f"Pas de référent")
        else:
            if temp[5] >= 3:
                referent_tier_on = ""
            else:
                referent_tier_on = f"Membre référent :\n<@{temp[14]}>"

            temp2 = cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [temp[14]]).fetchone()
            if temp[5] >= 4:
                referent_tier_two = ""
            else:
                if temp2[5] >= 4:
                    referent_tier_two = f"Membre+ référent :\n<@{temp[14]}>"
                else:
                    referent_tier_two = f"Membre+ référent :\n<@{temp2[14]}>"

            temp3 = cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [temp2[14]]).fetchone()
            if temp[5] >= 5:
                referent_tier_three = ""
            else:
                if temp2[5] >= 5:
                    referent_tier_three = f"Officier référent :\n<@{temp[14]}>"
                elif temp3[5] >= 5:
                    referent_tier_three = f"Officier référent :\n<@{temp2[14]}>"
                else:
                    referent_tier_three = f"Officier référent :\n<@{temp3[14]}>"

            temp4 = cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [temp3[14]]).fetchone()
            referent_tier_four = f"Leader référent :\n<@{temp4[14]}>"

            embed.add_field(name="Référent :",
                            value=f"{referent_tier_on}\n{referent_tier_two}\n{referent_tier_three}\n{referent_tier_four}")

        temp = cur.execute("SELECT id_discord FROM recrutement WHERE referent=?", [user.id]).fetchall()

        text = ""
        for i in range(len(temp)):
            text += f"<@{temp[i][0]}> "

        if text == "":
            text = "Référent de personne"

        embed.add_field(name="Responsable de :", value=f"{text}")

        await ctx.respond(embed=embed)

    # Command /fc-recrutement
    @forcecheck.command(name="recrutement", description="Actualise le statut d'une personne.",
                            default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def force_check_recrutement(self, ctx: discord.ApplicationContext,
                                      user: Option(discord.User, "Entre un utilisateur.", required=False)):
        guild = self.bot.get_guild(config["guild_id"])

        if user is not None:
            cur = self.bot.countrydb.cursor()
            cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            cur.close()
            if temp is None:
                await ctx.respond("Joueur non enregistrer dans la db recrutement")
                return
            db_data = {
                "id_sys": temp[0],
                "id_discord": temp[1],
                "pseudo_ingame": temp[2],
                "annee_naissance": temp[3],
                "experience": temp[4],
                "grade": temp[5],
                "country": temp[6],
                "peut_quitter_pays": temp[7],
                "date_recrutement": temp[8],
                "anciennete": temp[9],
                "schematique": temp[10],
                "regiment": temp[11],
                "last_connexion": temp[12],
                "absence_fin": temp[13],
                "referent": temp[14]
            }

            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {config["api_key"]}',
            }
            response = requests.get(f'https://publicapi.nationsglory.fr/user/{db_data["pseudo_ingame"]}',
                                    headers=headers)
            if response.status_code != 200:
                await ctx.respond("Erreur de l'API NationsGlory")
                return
            if "error" in response.json():
                if response.json()["error"] == "unknown.user":  # Joueur non détecter
                    await user.remove_roles(guild.get_role(config["roles"]["grades"]["link"]))
                    await ctx.respond("Joueur non reconnu par l'API NationsGlory")
                    api_data = None
                else:
                    await ctx.respond("Erreur de l'API NationsGlory")
                    return
            else:
                await user.add_roles(guild.get_role(config["roles"]["grades"]["link"]))

                api_data = {
                    "country": response.json()["servers"]["green"]["country"],
                    "last_connection": response.json()["last_connection"],
                }

            await self.recrutement_check_user(db_data, api_data, user)
            await ctx.respond(f"Check sur {user.mention} effectuer avec succès")
        else:
            await ctx.respond(f"Check de pays général lancé !")
            await self.recrutement_check()

    # Command /fc-diplomatique
    @forcecheck.command(name="diplomatique", description="Actualise le statut d'une personne.",
                            default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def force_check_diplomatie(self, ctx: discord.ApplicationContext,
                                     user: Option(discord.User, "Entre un utilisateur.", required=False)):
        guild = self.bot.get_guild(config["guild_id"])

        if user is not None:
            cur = self.bot.worlddb.cursor()
            cur.execute("SELECT * FROM diplomatie WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            cur.close()
            if temp is None:
                await ctx.respond("Joueur non enregistrer dans la db de diplomatie")
                return
            db_data = {
                "id_sys": temp[0],
                "id_discord": temp[1],
                "pseudo_ingame": temp[2],
            }

            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {config["api_key"]}',
            }
            response = requests.get(f'https://publicapi.nationsglory.fr/user/{db_data["pseudo_ingame"]}',
                                    headers=headers)
            if response.status_code != 200:
                await ctx.respond("Erreur de l'API NationsGlory")
                return
            if (user.get_role(config["roles"]["grades"]["doyen"]) or user.get_role(
                    config["roles"]["grades"]["conseiller"])) is None:
                try:  # Rename suivant situation
                    if "error" in response.json():
                        if response.json()["error"] == "unknown.user":  # Joueur non détecter
                            if len(f"Unlink | {db_data['pseudo_ingame']}") <= 32:
                                await user.edit(nick=f"Unlink | {db_data['pseudo_ingame']}")
                            elif len(f"{db_data['pseudo_ingame']}") <= 32:
                                await user.edit(nick=f"{db_data['pseudo_ingame']}")
                            await user.remove_roles(guild.get_role(config["roles"]["grades"]["link"]))
                            await ctx.respond("Joueur non reconnu par l'API NationsGlory")
                        else:
                            await ctx.respond("Erreur de l'API NationsGlory")
                        return

                    api_data = {
                        "country": response.json()["servers"]["green"]["country"],
                        "country_rank": response.json()["servers"]["green"]["country_rank"],
                    }
                    if len(f"{api_data['country']} | {db_data['pseudo_ingame']} ({api_data['country_rank']})") <= 32:
                        await user.edit(nick=f"{api_data['country']} | {db_data['pseudo_ingame']} ({api_data['country_rank']})")
                    elif len(f"{api_data['country']} | {db_data['pseudo_ingame']}") <= 32:
                        await user.edit(nick=f"{api_data['country']} | {db_data['pseudo_ingame']}")
                    else:
                        await user.edit(nick=f"{db_data['pseudo_ingame']}")
                    await user.add_roles(guild.get_role(config["roles"]["grades"]["link"]))
                except discord.errors.Forbidden:
                    pass
            await ctx.respond(f"Check sur {user.mention} effectuer avec succès")
        else:
            await ctx.respond(f"Check diplomatique général lancé !")
            await self.diplomatique_check()

    # Command /goldpass-list
    @commands.slash_command(description="Donne la liste des absences longues durées.", default_permission=False, name="goldpass-list")
    @commands.has_any_role(config["roles"]["grades"]["gouverneur"])
    async def goldpass_list(self, ctx):
        special_date = "2050-01-01"
        cur = self.bot.countrydb.cursor()
        text = "__Liste des personnes sous GoldPass du check d'activité :__ ```"
        temp = cur.execute("SELECT pseudo_ingame FROM recrutement WHERE absence_fin=?", [special_date]).fetchall()
        text += ", ".join([x[0] for x in temp])
        await ctx.respond(f"{text}```")
        cur.close()

    # Command /pings
    @commands.slash_command(description="Pour modifier ses pings.", name="pings")
    async def pings(self, ctx):
        embed = utils.create_embed(self.bot, title="**Pings :**",
                                   description=f"Tu peux choisir des pings personnalisés :\n\n<@&{config['roles']['pings']['notations']}> : Pour être mentionné pour les notations du pays (une fois par semaine).\n\n<@&{config['roles']['pings']['discord']}> : Pour être mentionné pour les mises a jours du discord, les nouveautés.\n\n<@&{config['roles']['pings']['media']}> : Pour être mentionné pour les vidéos et lives des membres du pays.\n\n<@&{config['roles']['pings']['secondaire']}> : Pour être mentionné pour les informations secondaires, les événements auxquelles ont participe hors de NationsGlory.\n\nCes paramètres peuvent être modifiés avec la commande ``/pings``",
                                   color=Color.gold())

        await ctx.channel.send(embed=embed, view=PingCommandView(self.bot))

    # ------------------------------------------------------------------------------------------
    #                               Éléments supplémentaires
    # ------------------------------------------------------------------------------------------

    async def recrutement_check(self):
        guild = self.bot.get_guild(config["guild_id"])
        data_log = guild.get_channel(config["channels"]["data_log"])
        data_bot = guild.get_channel(config["channels"]["bot_data_channel"])
        API_error = 0
        Unrecognized = 0
        Leave = 0

        cur = self.bot.countrydb.cursor()
        cur.execute("SELECT count(*) FROM recrutement")
        data_number = int(cur.fetchone()[0])
        with tqdm(total=data_number, unit="member", ascii="⬡⬢", bar_format='{l_bar}{bar:25}{r_bar}{bar:-10b}',
                  desc="Check de la db recrutement ") as line1:
            await data_bot.send(
                "┌--------------------------------┫ Nouveau check de la db de pays ┠--------------------------------┐")
            message = await data_log.send(line1)
            for i in range(0, data_number, NOMBRE_MEMBRE_PAR_STEP):
                cur.execute(
                    "SELECT * FROM recrutement ORDER BY id_sys LIMIT " + str(NOMBRE_MEMBRE_PAR_STEP) + " OFFSET ?", [i])
                count = 0
                for temp in cur:
                    await asyncio.sleep(5.1)
                    count += 1
                    db_data = {
                        "id_sys": temp[0],
                        "id_discord": temp[1],
                        "pseudo_ingame": temp[2],
                        "annee_naissance": temp[3],
                        "experience": temp[4],
                        "grade": temp[5],
                        "country": temp[6],
                        "peut_quitter_pays": temp[7],
                        "date_recrutement": temp[8],
                        "anciennete": temp[9],
                        "schematique": temp[10],
                        "regiment": temp[11],
                        "last_connection": temp[12],
                        "absence_fin": temp[13],
                        "referent": temp[14]
                    }

                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {config["api_key"]}',
                    }
                    response = requests.get(f'https://publicapi.nationsglory.fr/user/{db_data["pseudo_ingame"]}',
                                            headers=headers)
                    user = guild.get_member(db_data["id_discord"])

                    if user is None:
                        await data_bot.send(
                            f"Le joueur <@{db_data['id_discord']}> ({db_data['pseudo_ingame']}) a quitté le discord.")
                        Leave += 1
                        user = None
                    elif user.get_role(config["roles"]["grades"]["reglement_valider"]) is None and (
                            db_data['grade'] != 0):
                        await data_bot.send(
                            f"Le joueur <@{db_data['id_discord']}> ({db_data['pseudo_ingame']}) a quitté le discord et est revenu.")
                        Leave += 1
                    if response.status_code != 200:
                        await data_bot.send(
                            f"Le joueur <@{db_data['id_discord']}> ({db_data['pseudo_ingame']}) provoque un crash de l'API NationsGlory.")
                        API_error += 1
                        api_data = None
                    elif "error" in response.json():
                        if response.json()["error"] == "unknown.user":  # Joueur non détecter
                            Unrecognized += 1
                            if user is not None:
                                await user.remove_roles(guild.get_role(config["roles"]["grades"]["link"]))
                        else:
                            await data_bot.send(
                                f"Le joueur <@{db_data['id_discord']}> ({db_data['pseudo_ingame']}) provoque un crash de l'API NationsGlory.")
                        api_data = None
                    else:
                        api_data = {
                            "country": response.json()["servers"]["green"]["country"],
                            "last_connection": response.json()["last_connection"],
                        }
                    await self.recrutement_check_user(db_data, api_data, user)
                line1.update(count)
                await message.edit(content=line1)
        cur.close()
        await data_log.send(
            f"Check de la db recrutement terminé ! Sur un total de ``{data_number}`` personnes, ``{Unrecognized}`` n'ont pas été reconnue (``{(Unrecognized / data_number) * 100}%``). ``{Leave}`` personnes ont quitté le discord (comprend aussi ceux revenus). Le bot a rencontré ``{API_error}`` erreurs d'API.")

    async def recrutement_check_user(self, db_data, api_data, user):

        cur = self.bot.countrydb.cursor()
        guild = self.bot.get_guild(config["guild_id"])
        data_bot = guild.get_channel(config["channels"]["bot_data_channel"])

        if user is None:
            return

        # vérifie si le joueur existe bien IG
        if api_data is None:
            await data_bot.send(
                f"L'utilisateur enregistrer sous le nom de {db_data['pseudo_ingame']} ({user.mention}) n'existe pas IG (ID: {db_data['id_sys']})")
            return

        # Actualisation pays
        if db_data["country"] != api_data["country"]:
            cur.execute("UPDATE recrutement SET pays=? WHERE id_discord=?",
                        [api_data["country"], db_data["id_discord"]])
            await user.remove_roles(guild.get_role(config["roles"]["pays"]["guyana"]))
            await user.remove_roles(guild.get_role(config["roles"]["pays"]["suriname"]))
            await user.remove_roles(guild.get_role(config["roles"]["pays"]["triniteettobago"]))
            await user.remove_roles(guild.get_role(config["roles"]["pays"]["venezuela"]))
            if api_data["country"] == "Guyana":
                await user.add_roles(guild.get_role(config["roles"]["pays"]["guyana"]))
            elif api_data["country"] == "Suriname":
                await user.add_roles(guild.get_role(config["roles"]["pays"]["suriname"]))
            elif api_data["country"] == "TriniteEtTobago":
                await user.add_roles(guild.get_role(config["roles"]["pays"]["triniteettobago"]))
            elif api_data["country"] == "Venezuela":
                await user.add_roles(guild.get_role(config["roles"]["pays"]["venezuela"]))

        # Inactivité
        if api_data is not None:
            jours_deco = (date.today() - datetime.datetime.fromisoformat(api_data["last_connection"]).date()).days
            cur.execute("UPDATE recrutement SET last_connection=? WHERE id_discord=?",
                        [jours_deco, db_data["id_discord"]])

            if jours_deco >= 10 and db_data["absence_fin"] is None:
                try:
                    await data_bot.send(
                        f"L'utilisateur {db_data['pseudo_ingame']} ({user.mention}) est absent depuis {jours_deco} jours.")
                except Forbidden:
                    pass

        # fin absence
        if db_data["absence_fin"] is not None and date.today() >= date.fromisoformat(db_data["absence_fin"]):
            cur.execute("UPDATE recrutement SET absence_fin=? WHERE id_discord=?", [None, db_data["id_discord"]])

            if db_data["grade"] == 1:
                grade = "Recrue"
            elif db_data["grade"] == 2:
                grade = "Recrue+"
            elif db_data["grade"] == 3:
                grade = "Membre"
            elif db_data["grade"] == 4:
                grade = "Membre+"
            elif db_data["grade"] == 5:
                grade = "Offi"
            elif db_data["grade"] == 6:
                grade = "Gouverneur"
            elif db_data["grade"] == 7:
                grade = "Second"
            else:
                grade = "Candidat"
            try:
                await user.edit(nick=f"{grade} | {db_data['pseudo_ingame']}")
            except AttributeError:
                pass

        # Ancienneté
        if date.today() - date.fromisoformat(db_data["date_recrutement"]) == timedelta(days=1) and db_data[
            "anciennete"] == 0:
            cur.execute("UPDATE recrutement SET anciennete=1 WHERE id_discord=?", [db_data["id_discord"]])
            try:
                referent = guild.get_member(db_data["referent"])
                await referent.send(
                    f"Le joueur {user.mention} donc tu es référent est maintenant dans le pays depuis 24h. Envois lui un message pour t'assurer que son intégration se passe bien")
            except Forbidden:
                pass
        if date.today() - date.fromisoformat(db_data["date_recrutement"]) == timedelta(days=3) and db_data[
            "anciennete"] <= 1:
            cur.execute("UPDATE recrutement SET anciennete=2 WHERE id_discord=?", [db_data["id_discord"]])
            try:
                referent = guild.get_member(db_data["referent"])
                await referent.send(
                    f"Le joueur {user.mention} donc tu es référent est maintenant dans le pays depuis 3 jours. Envois lui un message pour t'assurer que son intégration se passe bien")
            except Forbidden:
                pass
        if date.today() - date.fromisoformat(db_data["date_recrutement"]) == timedelta(days=5) and db_data[
            "anciennete"] <= 2:
            cur.execute("UPDATE recrutement SET anciennete=3 WHERE id_discord=?", [db_data["id_discord"]])
            try:
                referent = guild.get_member(db_data["referent"])
                await referent.send(
                    f"Le joueur {user.mention} donc tu es référent est maintenant dans le pays depuis 5 jours. Envois lui un message pour lui rappeler qu'il est maintenant assez ancien pour rank-up.")
            except Forbidden:
                pass
        # if date.today() - date.fromisoformat(db_data["date_recrutement"]) >= timedelta(days=31) and db_data[
        #     "anciennete"] <= 1:
        #     cur.execute("UPDATE recrutement SET anciennete=2 WHERE id_discord=?", [db_data["id_discord"]])
        #     # try:
        #     #     await member_guild.send(
        #     #         f"Félicitation, cela fait maintenant 1 mois que tu es dans le pays ! tu as automatiquement validé la condition \"ancienneté\" dans les conditions de ranks (plus d'info avec le /player-info)")
        #     # except Forbidden:
        #     #     pass
        # if date.today() - date.fromisoformat(db_data["date_recrutement"]) >= timedelta(days=5) and db_data[
        #     "anciennete"] == 0:
        #     cur.execute("UPDATE recrutement SET anciennete=2 WHERE id_discord=?", [db_data["id_discord"]])
        #     # try:
        #     #     await member_guild.send(
        #     #         f"Félicitation, cela fait maintenant 1 mois que tu es dans le pays ! tu as automatiquement validé la condition \"ancienneté\" dans les conditions de ranks (plus d'info avec le /player-info)")
        #     # except Forbidden:
        #     #     pass
        # if date.today() - date.fromisoformat(db_data["date_recrutement"]) >= timedelta(days=90) and db_data[
        #     "anciennete"] <= 2:
        #     cur.execute("UPDATE recrutement SET anciennete=3 WHERE id_discord=?", [db_data["id_discord"]])
        #     # try:
        #     #     await member_guild.send(
        #     #         f"Félicitation, cela fait maintenant 3 mois que tu es dans le pays ! tu as automatiquement validé la condition \"ancienneté\" dans les conditions de ranks (plus d'info avec le /player-info)")
        #     # except Forbidden:
        #     #     pass

        # Bon pays
        if (not api_data["country"] in config["list_pays"]) and (db_data["peut_quitter_pays"] is None):
            await data_bot.send(
                f"L'utilisateur {db_data['pseudo_ingame']} ({user.mention}) n'est plus dans l'un des pays GDE et ne dispose d'aucune autorisation a cette effet.")

        # 2 semaines nouvelle recrue
        # anciennete = date.today() - date.fromisoformat(bdd_data["date_recrutement"])
        # if anciennete >= timedelta(days=14) and bdd_data["grade"] == 1:
        #     await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} ({member_guild.mention}) est nouvelle recrue depuis {anciennete} jours.")
        #     return

        self.bot.countrydb.commit()
        cur.close()

    async def diplomatique_check(self):
        guild = self.bot.get_guild(config["guild_id"])
        data_log = guild.get_channel(config["channels"]["data_log"])
        API_error = 0
        Unrecognized = 0
        Delete = 0

        cur = self.bot.worlddb.cursor()
        cur.execute("SELECT count(*) FROM diplomatie")
        data_number = int(cur.fetchone()[0])
        with tqdm(total=data_number, unit="member", ascii="⬡⬢", bar_format='{l_bar}{bar:25}{r_bar}{bar:-10b}',
                  desc="Check de la db diplomatique ") as line1:
            message = await data_log.send(line1)
            for i in range(0, data_number, NOMBRE_MEMBRE_PAR_STEP):
                cur.execute(
                    "SELECT * FROM diplomatie ORDER BY id_sys LIMIT " + str(NOMBRE_MEMBRE_PAR_STEP) + " OFFSET ?",
                    [i - Delete])
                count = 0
                for temp in cur:
                    await asyncio.sleep(5.1)
                    count += 1
                    db_data = {
                        "id_sys": temp[0],
                        "id_discord": temp[1],
                        "pseudo_ingame": temp[2],
                    }

                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {config["api_key"]}',
                    }
                    response = requests.get(f'https://publicapi.nationsglory.fr/user/{db_data["pseudo_ingame"]}',
                                            headers=headers)
                    user = guild.get_member(db_data["id_discord"])

                    if user is None:
                        Delete += 1
                        cur.execute("DELETE FROM diplomatie WHERE id_discord = ?", [str(db_data["id_discord"])])
                        self.bot.worlddb.commit()
                    else:
                        if response.status_code != 200:
                            API_error += 1
                        if (user.get_role(config["roles"]["grades"]["doyen"]) or user.get_role(config["roles"]["grades"]["conseiller"])) is None:
                            try:  # Rename suivant situation
                                if "error" in response.json():
                                    if response.json()["error"] == "unknown.user":  # Joueur non détecter
                                        if len(f"Unlink | {db_data['pseudo_ingame']}") <= 32:
                                            await user.edit(nick=f"Unlink | {db_data['pseudo_ingame']}")
                                        elif len(f"{db_data['pseudo_ingame']}") <= 32:
                                            await user.edit(nick=f"{db_data['pseudo_ingame']}")
                                        await user.remove_roles(guild.get_role(config["roles"]["grades"]["link"]))
                                        Unrecognized += 0
                                    else:
                                        API_error += 1
                                else:
                                    api_data = {
                                        "country": response.json()["servers"]["green"]["country"],
                                        "country_rank": response.json()["servers"]["green"]["country_rank"],
                                    }
                                    await user.add_roles(guild.get_role(config["roles"]["grades"]["link"]))
                                    if len(f"{api_data['country']} | {db_data['pseudo_ingame']} ({api_data['country_rank']})") <= 32:
                                        await user.edit(
                                            nick=f"{api_data['country']} | {db_data['pseudo_ingame']} ({api_data['country_rank']})")
                                    elif len(f"{api_data['country']} | {db_data['pseudo_ingame']}") <= 32:
                                        await user.edit(nick=f"{api_data['country']} | {db_data['pseudo_ingame']}")
                                    else:
                                        await user.edit(nick=f"{db_data['pseudo_ingame']}")
                            except discord.errors.Forbidden:
                                pass
                line1.update(count)
                await message.edit(content=line1)

        cur.close()
        await data_log.send(
            f"Check de la db diplomatique terminé ! Sur un total de ``{data_number}`` personnes, ``{Unrecognized}`` n'ont pas été reconnue (``{(Unrecognized / data_number) * 100}%``). ``{Delete}`` personnes ont quitter le discord et ont donc été supprimer de la db diplomatique. Le bot a rencontré ``{API_error}`` erreurs d'API.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.start_check_loop()


class PingCommandView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Notations", style=discord.ButtonStyle.secondary, emoji="📙", custom_id="button-notations")
    async def notations_button_callback(self, button, interaction):
        guild = self.bot.get_guild(config["guild_id"])

        if button.style == discord.ButtonStyle.secondary:
            button.style = discord.ButtonStyle.green
            await interaction.user.add_roles(guild.get_role(config["roles"]["pings"]["notations"]))
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.secondary
            await interaction.user.remove_roles(guild.get_role(config["roles"]["pings"]["notations"]))
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Discord", style=discord.ButtonStyle.secondary, emoji="👾", custom_id="button-discord")
    async def discord_button_callback(self, button, interaction):
        guild = self.bot.get_guild(config["guild_id"])

        if button.style == discord.ButtonStyle.secondary:
            button.style = discord.ButtonStyle.green
            await interaction.user.add_roles(guild.get_role(config["roles"]["pings"]["discord"]))
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.secondary
            await interaction.user.remove_roles(guild.get_role(config["roles"]["pings"]["discord"]))
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Média", style=discord.ButtonStyle.secondary, emoji="🎥", custom_id="button-media")
    async def media_button_callback(self, button, interaction):
        guild = self.bot.get_guild(config["guild_id"])

        if button.style == discord.ButtonStyle.secondary:
            button.style = discord.ButtonStyle.green
            await interaction.user.add_roles(guild.get_role(config["roles"]["pings"]["media"]))
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.secondary
            await interaction.user.remove_roles(guild.get_role(config["roles"]["pings"]["media"]))
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Secondaire", style=discord.ButtonStyle.secondary, emoji="🧶",
                       custom_id="button-secondaire")
    async def secondaire_button_callback(self, button, interaction):
        guild = self.bot.get_guild(config["guild_id"])

        if button.style == discord.ButtonStyle.secondary:
            button.style = discord.ButtonStyle.green
            await interaction.user.add_roles(guild.get_role(config["roles"]["pings"]["secondaire"]))
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.secondary
            await interaction.user.remove_roles(guild.get_role(config["roles"]["pings"]["secondaire"]))
        await interaction.response.edit_message(view=self)
