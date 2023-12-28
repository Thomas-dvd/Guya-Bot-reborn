import asyncio
import datetime
import json
import os
import random
from datetime import date, timedelta, datetime

import discord
import requests
from discord import Option, Color
from discord.ext import commands
from tqdm import tqdm

import utils
from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog management')
    bot.add_cog(Management(bot))


NOMBRE_MEMBRE_PAR_STEP = config["force_check_actualisation"]


class Management(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # Cooldown pour le Check de la db diplomatique et de pays
    async def start_check_loop(self):
        while True:
            await asyncio.create_task(self.country_check())
            await asyncio.sleep(12 * 60 * 60)
            await asyncio.create_task(self.diplomatic_check())
            await asyncio.sleep(12 * 60 * 60)

    # ------------------------------------------------------------------------------------------
    #                                         Commands
    # ------------------------------------------------------------------------------------------

    # groupe forcecheck
    forcecheck = discord.SlashCommandGroup("forcecheck", "forcecheck related commands")

    # Command /informations
    @commands.slash_command(description="Donne toute les informations d'une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def informations(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True)):

        data = utils.database(self, "country", "discord_id", user.id)
        if data is None:
            data = utils.database(self, "diplomacy", "discord_id", user.id)
            if data is None:
                await ctx.respond("Utilisateur absent de la base de données.")
                return

        total_pack = len(data) // 20
        if len(data) % 20 != 0:
            total_pack += 1

        for i in range(1, total_pack + 1):
            embed = utils.create_embed(self.bot, f"Informations de {user.name}, partie {i}/{total_pack}",
                                       color=Color.brand_red())
            for name, value in data.items():
                embed.add_field(name=f"{name} :", value=f"{value}")

            if i == 1:
                await ctx.respond(embed=embed)
            else:
                await ctx.channel.send(embed=embed)

    # Command /edit
    @commands.slash_command(name="édit", description="Donne toute les informations d'une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["gouverneur"])
    async def edit(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True), setting: Option(str, "paramètre a modifier", choices=utils.database_parametres(question="EditParametres"), name="paramètre", required=True), value: Option(str, "nouvelle valeur", required=True, default=None, name="valeur")):

        if utils.database(self, "country", "discord_id", user.id) is None:
            if utils.database(self, "diplomacy", "discord_id", user.id) is None:
                await ctx.respond("Utilisateur absent de la base de données.")
                return
            if utils.database_parametres(setting, "IsInDiplomacyDB") is False:
                await ctx.respond(
                    "Ce paramètre n'est pas disponible pour les utilisateurs de la base de donnée diplomatique")
                return
            table = "diplomacy"
        else:
            table = "country"

        if value in ["None", "Null", "none", "null", ""]:
            value = None
        value = utils.database_parametres(setting, "NeedFormat", value)

        cur = self.bot.players.cursor()
        cur.execute(f"UPDATE {table} SET {setting}=? WHERE discord_id=?", [value, user.id])
        self.bot.players.commit()
        cur.close()
        data = utils.database(self, table, "discord_id", user.id)

        # rename en cas de changement de pseudo
        if setting == "ingame_name":
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
            }
            response = requests.get(f'https://publicapi.nationsglory.fr/user/{value}', headers=headers)

            if response.status_code != 200:
                await ctx.respond(
                    f"Le nouveau nom d'utilisateur a bien été enregistrer. Cependant, une erreur a été rencomptré lors de la liaison avec l'API NationsGlory. Rename de l'utilisateur impossible. *code erreur: E-N-01*")
                return

            if table == "country":
                try:
                    if len(f"Recrue | {value}") <= 32 and data['grade'] == 0:
                        await user.edit(nick=f"Recrue | {value}")
                    elif len(f"Recrue+ | {value}") <= 32 and data['grade'] == 1:
                        await user.edit(nick=f"Recrue+ | {value}")
                    elif len(f"Membre | {value}") <= 32 and data['grade'] == 2:
                        await user.edit(nick=f"Membre | {value}")
                    elif len(f"Membre+ | {value}") <= 32 and data['grade'] == 3:
                        await user.edit(nick=f"Membre+ | {value}")
                    elif len(f"Offi. | {value}") <= 32 and data['grade'] == 4:
                        await user.edit(nick=f"Offi. | {value}")
                    elif len(f"Gouv. | {value}") <= 32 and data['grade'] == 5:
                        await user.edit(nick=f"Gouv. | {value}")
                    elif len(f"Sec. | {value}") <= 32 and data['grade'] == 6:
                        await user.edit(nick=f"Sec. | {value}")
                    else:
                        await user.edit(nick=f"{value}")
                except discord.errors.Forbidden:
                    await ctx.respond(
                        f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``. Cependant, une erreur a été rencomptré lors du rename. *code erreur: E-D-01*")
                    return
            else:
                if "error" in response.json():
                    try:
                        if len(f"Unlink | {data['ingame_name']}") <= 32:
                            await user.edit(nick=f"Unlink | {data['ingame_name']}")
                        else:
                            await user.edit(nick=f"{data['ingame_name']}")
                    except discord.errors.Forbidden:
                        await ctx.respond(
                            f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``. Cependant, une erreur a été rencomptré lors du rename. *code erreur: E-D-01*")
                        return
                else:
                    try:
                        api_data = {
                            "username": response.json()["username"],
                            "country": response.json()["servers"]["green"]["country"],
                            "country_rank": response.json()["servers"]["green"]["country_rank"],
                        }

                        if str(api_data['country']) != ("0" or "None" or ""):
                            api_data['country'] = "Wilderness"
                            api_data['country_rank'] = ""

                        if len(f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})") <= 32:
                            await user.edit(
                                nick=f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})")
                        elif len(f"{api_data['country']} | {data['ingame_name']}") <= 32:
                            await user.edit(nick=f"{api_data['country']} | {data['ingame_name']}")
                        else:
                            await user.edit(nick=f"{data['ingame_name']}")
                    except discord.errors.Forbidden:
                        await ctx.respond(
                            f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``. Cependant, une erreur a été rencomptré lors du rename. *code erreur: E-D-01*")
                        return

            await ctx.respond(
                f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``. Rename automatique effectuer")
            return

        # rename en cas de changement de grade
        if setting == "grade":
            try:
                if len(f"Recrue | {data['ingame_name']}") <= 32 and data['grade'] == 0:
                    await user.edit(nick=f"Recrue | {data['ingame_name']}")
                elif len(f"Recrue+ | {data['ingame_name']}") <= 32 and data['grade'] == 1:
                    await user.edit(nick=f"Recrue+ | {data['ingame_name']}")
                elif len(f"Membre | {data['ingame_name']}") <= 32 and data['grade'] == 2:
                    await user.edit(nick=f"Membre | {data['ingame_name']}")
                elif len(f"Membre+ | {data['ingame_name']}") <= 32 and data['grade'] == 3:
                    await user.edit(nick=f"Membre+ | {data['ingame_name']}")
                elif len(f"Offi. | {data['ingame_name']}") <= 32 and data['grade'] == 4:
                    await user.edit(nick=f"Offi. | {data['ingame_name']}")
                elif len(f"Gouv. | {data['ingame_name']}") <= 32 and data['grade'] == 5:
                    await user.edit(nick=f"Gouv. | {data['ingame_name']}")
                elif len(f"Sec. | {data['ingame_name']}") <= 32 and data['grade'] == 6:
                    await user.edit(nick=f"Sec. | {data['ingame_name']}")
                else:
                    await user.edit(nick=f"{data['ingame_name']}")
            except discord.errors.Forbidden:
                await ctx.respond(
                    f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``. Cependant, une erreur a été rencomptré lors du rename. *code erreur: E-D-01*")
                return
            await ctx.respond(
                f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``. Rename automatique effectuer")
            return

        await ctx.respond(f"La donnée {setting} du joueur {user.mention} a bien été définit sur ``{value}``.")

    # Command /transfert
    @commands.slash_command(description="Transfert un joueur de base de données.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def transfert(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True), relation: Option(str, "Niveau de relation.", choices=["Neutre", "Allié", "Colonie", "Alliance", "Ami", "Confiance"], required=False, default="Neutre"), medal: Option(str, "Grades médailles.", choices=["Guide", "Modo", "OP (SuperModo/Admin)"], required=False, name="médailles")):

        await ctx.defer()

        data = utils.database(self, "country", "discord_id", user.id)
        if data is None:
            data = utils.database(self, "diplomacy", "discord_id", user.id)
            if data is None:
                await ctx.respond("Utilisateur absent de la base de données.")
                return

            cur = self.bot.players.cursor()
            cur.execute("DELETE FROM diplomacy WHERE discord_id = ?", [user.id])

            data['recruitment_date'] = date.today()
            data['grade'] = 0

            cur.execute("INSERT INTO country (discord_id, ingame_name, recruitment_date, grade) VALUES (:discord_id, "
                        ":ingame_name, :recruitment_date, :grade)", data)
            self.bot.players.commit()
            cur.close()

            for role in user.roles:
                try:
                    if role.name != "@everyone":
                        await user.remove_roles(ctx.guild.get_role(role.id))
                except discord.errors.Forbidden or discord.errors.NotFound:
                    pass

            if len(f"Recrue | {data['ingame_name']}") <= 32:
                await user.edit(nick=f"Recrue | {data['ingame_name']}")

            await user.add_roles(ctx.guild.get_role(config["grades"]["nouvelle_recrue"]))
            text = f"<@&{config['grades']['nouvelle_recrue']}>"

            for role in config["grades"]["deco"]["pays"]:
                await user.add_roles(ctx.guild.get_role(role))
                text += f", <@&{role}>"

            for role in config["grades"]["deco"]["global"]:
                await user.add_roles(ctx.guild.get_role(role))
                text += f", <@&{role}>"

            await user.remove_roles(ctx.guild.get_role((config["grades"]["frontiere"])))

            await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
            text += f", <@&{config['grades']['neutre']}>"

            embed = utils.create_embed(self.bot, title="Rôles obtenus :", description=f"{text}", color=Color.gold())
            await ctx.channel.send(embed=embed)

            channel_gg = ctx.guild.get_channel(config["channels"]["rank_uwu"])
            msg = await channel_gg.send(
                f"Félicitation à {user.mention} qui passe Nouvelle recrue. Bienvenue à lui dans le pays ! 🎉")
            emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
            await msg.add_reaction(emoji)

            channel_general = ctx.guild.get_channel(config["channels"]["general"])
            await channel_general.send(random.choice(config["welcome_message"]).format(name=user.mention))
            await ctx.respond(f"{user.name} est passé Nouvelle Recrue. Transfert réussi.")

        else:

            api_ok = 0
            text = ""
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
            }
            response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["ingame_name"]}',
                                    headers=headers)

            if response.status_code != 200:
                await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-01*")
                return
            if "error" in response.json():
                if response.json()["error"] == "unknown.user":  # Joueur non détecter
                    api_ok = 1
                else:
                    await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-02*")
                    return

            cur = self.bot.players.cursor()
            cur.execute("DELETE FROM country WHERE discord_id = ?", [user.id])
            cur.execute(
                "INSERT INTO diplomacy (discord_id, ingame_name) VALUES (:discord_id, :ingame_name)",
                data)
            self.bot.players.commit()
            cur.close()

            for role in user.roles:
                try:
                    if role.name != "@everyone":
                        await user.remove_roles(ctx.guild.get_role(role.id))
                except discord.errors.Forbidden or discord.errors.NotFound:
                    pass

            # Rename user + add role
            await user.add_roles(ctx.guild.get_role(config["grades"]["link"]))
            text += f"<@&{config['grades']['link']}>"

            for role in config["grades"]["deco"]["global"]:
                await user.add_roles(ctx.guild.get_role(role))
                text += f", <@&{role}>"

            if api_ok == 1:
                if len(f"Unlink | {data['ingame_name']}") <= 32:
                    await user.edit(nick=f"Unlink | {data['ingame_name']}")
                elif len(f"{data['ingame_name']}") <= 32:
                    await user.edit(nick=f"{data['ingame_name']}")

            else:
                api_data = {
                    "username": response.json()["username"],
                    "country": response.json()["servers"]["green"]["country"],
                    "country_rank": response.json()["servers"]["green"]["country_rank"],
                }

                if str(api_data['country']) != ("0" or "None" or ""):
                    api_data['country'] = "Wilderness"
                    api_data['country_rank'] = ""

                if len(f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})") <= 32:
                    await user.edit(nick=f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})")
                elif len(f"{api_data['country']} | {data['ingame_name']}") <= 32:
                    await user.edit(nick=f"{api_data['country']} | {data['ingame_name']}")
                else:
                    await user.edit(nick=f"{data['ingame_name']}")

            if relation == "Neutre":
                await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
                text += f", <@&{config['grades']['neutre']}>"

            elif relation == "Allié":
                await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
                text += f", <@&{config['grades']['neutre']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
                text += f", <@&{config['grades']['allié']}>"

            elif relation == "Ami":
                await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
                text += f", <@&{config['grades']['neutre']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
                text += f", <@&{config['grades']['allié']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["ami"]))
                text += f", <@&{config['grades']['ami']}>"

            elif relation == "Confiance":
                await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
                text += f", <@&{config['grades']['neutre']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
                text += f", <@&{config['grades']['allié']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["ami"]))
                text += f", <@&{config['grades']['ami']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["confiance"]))
                text += f", <@&{config['grades']['confiance']}>"

            elif relation == "Alliance":
                await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
                text += f", <@&{config['grades']['neutre']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
                text += f", <@&{config['grades']['allié']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["alliance"]))
                text += f", <@&{config['grades']['alliance']}>"

            elif relation == "Colonie":
                await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
                text += f", <@&{config['grades']['neutre']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
                text += f", <@&{config['grades']['allié']}>"
                await user.add_roles(ctx.guild.get_role(config["grades"]["colonie"]))
                text += f", <@&{config['grades']['colonie']}>"

            if medal == "Guide":
                await user.add_roles(ctx.guild.get_role(config["grades"]["guide"]))
                text += f", <@&{config['grades']['guide']}>"

            elif medal == "Modo":
                await user.add_roles(ctx.guild.get_role(config["grades"]["modo"]))
                text += f", <@&{config['grades']['modo']}>"

            elif medal == "OP (SuperModo/Admin)":
                await user.add_roles(ctx.guild.get_role(config["grades"]["op_sm_admin"]))
                text += f", <@&{config['grades']['op_sm_admin']}>"

            embed = utils.create_embed(self.bot, title="Rôles obtenus :", description=f"{text}", color=Color.gold())
            await ctx.channel.send(embed=embed)
            if api_ok == 0:
                await ctx.respond(f"{user.mention} a bien été transféré.")
            else:
                await ctx.respond(
                    f"{user.mention} a bien été transféré. **Impossible de trouver un joueur NG avec ce nom.** *code erreur: E-N-03*")

    # Command /fc-pays
    @forcecheck.command(name="pays", description="Actualise le statut d'une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def force_check_country(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):
        guild = self.bot.get_guild(config["guild_id"])

        if user is not None:
            data = utils.database(self, "country", "discord_id", user.id)
            if data is None:
                await ctx.respond("Joueur non enregistrer dans la db de pays")
                return

            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
            }
            response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["ingame_name"]}',
                                    headers=headers)
            if response.status_code != 200:
                await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-01*")
                return
            if "error" in response.json():
                if response.json()["error"] == "unknown.user":  # Joueur non détecter
                    await user.remove_roles(guild.get_role(config["grades"]["link"]))
                    api_data = None
                else:
                    await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-02*")
                    return
            else:
                await user.add_roles(guild.get_role(config["grades"]["link"]))

                api_data = {
                    "country": response.json()["servers"]["green"]["country"],
                    "last_connection": response.json()["last_connection"],
                }

            await self.country_check_user(data, api_data, user)
            await ctx.respond(f"Check sur {user.mention} effectué avec succès.")
        else:
            await ctx.respond(f"Check de pays général lancé !")
            await self.country_check()

    # Command /fc-diplomatique
    @forcecheck.command(name="diplomatique", description="Actualise le statut d'une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def force_check_diplomatie(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):
        guild = self.bot.get_guild(config["guild_id"])

        if user is not None:
            cur = self.bot.players.cursor()
            data = utils.database(self, "diplomacy", "discord_id", user.id)
            cur.close()
            if data is None:
                await ctx.respond("Joueur non enregistrer dans la db de diplomatie")
                return

            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
            }
            response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["ingame_name"]}',
                                    headers=headers)
            if response.status_code != 200:
                await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-01*")
                return
            if (user.get_role(config["grades"]["doyen"]) or user.get_role(
                    config["grades"]["conseiller"])) is None:
                try:  # Rename suivant situation
                    if "error" in response.json():
                        if response.json()["error"] == "unknown.user":  # Joueur non détecter
                            if len(f"Unlink | {data['ingame_name']}") <= 32:
                                await user.edit(nick=f"Unlink | {data['ingame_name']}")
                            elif len(f"{data['ingame_name']}") <= 32:
                                await user.edit(nick=f"{data['ingame_name']}")
                            await user.remove_roles(guild.get_role(config["grades"]["link"]))
                            await ctx.respond("Joueur non reconnu par l'API NationsGlory. Pseudo a vérifier.")
                        else:
                            await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-02*")
                        return

                    api_data = {
                        "country": response.json()["servers"]["green"]["country"],
                        "country_rank": response.json()["servers"]["green"]["country_rank"],
                    }
                    if len(f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})") <= 32:
                        await user.edit(
                            nick=f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})")
                    elif len(f"{api_data['country']} | {data['ingame_name']}") <= 32:
                        await user.edit(nick=f"{api_data['country']} | {data['ingame_name']}")
                    else:
                        await user.edit(nick=f"{data['ingame_name']}")
                    await user.add_roles(guild.get_role(config["grades"]["link"]))
                except discord.errors.Forbidden:
                    pass
            await ctx.respond(f"Check sur {user.mention} effectuer avec succès.")
        else:
            await ctx.respond(f"Check diplomatique général lancé !")
            await self.diplomatic_check()

    # Command /absence
    @commands.slash_command(description="Pour noter l'absence de quelqu'un.")
    @commands.has_any_role(config["grades"]["officier"])
    async def absence(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur."), end: Option(str, "Entre une date de fin", required=True, name="fin")):

        try:
            end = date.fromisoformat(end)
        except ValueError:
            await ctx.respond(
                "Format de l'absence invalide ! Écrit sous la forme AAAA-MM-JJ (Année, puis un tiret du 6, Mois, re un tiret et enfin le jour), comme par exemple : 2023-05-25")
            return
        cur = self.bot.players.cursor()
        cur.execute("UPDATE country SET absence = ? WHERE discord_id=?", [end, user.id])
        ingame_name = cur.execute("SELECT ingame_name FROM country WHERE discord_id=?", [user.id]).fetchone()
        self.bot.players.commit()

        guild = self.bot.get_guild(config["guild_id"])
        member_guild = guild.get_member(user.id)
        try:
            await member_guild.edit(nick=f"AFK | {ingame_name[0]}")
        except AttributeError:
            pass
        await ctx.respond(f"L'absence de {user.mention} jusqu'au {end} a bien été enregistrer")

    # Command /expatriation
    @commands.slash_command(name="expatriation", description="Permet un bypass du joueur indiqué lors du check des joueurs hors du pays par le bot.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def expatriation(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True)):
        if utils.database(self, "country", "discord_id", user.id) is None:
            await ctx.respond(f"{user.mention} ne fait pas partie de la base de données de pays.")
            return
        cur = self.bot.players.cursor()
        cur.execute("UPDATE country SET country=? WHERE discord_id=?", ["bypass", user.id])
        self.bot.players.commit()
        cur.close()
        await ctx.respond(f"{user.mention} dispose maintenant d'une autorisation de sortie du territoire.")

    # TODO: Command /badges
    pass

    # ------------------------------------------------------------------------------------------
    #                                   Loops check
    # ------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_ready(self):
        await self.start_check_loop()

    # ------------------------------------------------------------------------------------------
    #                               Pays et diplomatique check
    # ------------------------------------------------------------------------------------------

    async def country_check(self):
        guild = self.bot.get_guild(config["guild_id"])
        data_log = guild.get_channel(config["channels"]["data_log"])
        data_bot = guild.get_channel(config["channels"]["data_bot"])
        api_error = 0
        unrecognized = 0
        leave = 0

        cur = self.bot.players.cursor()
        cur.execute("SELECT count(*) FROM country")
        data_number = int(cur.fetchone()[0])
        with tqdm(total=data_number, unit="member", ascii="⬡⬢", bar_format='{l_bar}{bar:25}{r_bar}{bar:-10b}',
                  desc="Check de la db de pays ") as line1:
            await data_bot.send(
                "┌--------------------------------┫ Nouveau check de la db de pays ┠--------------------------------┐")
            message = await data_log.send(str(line1))
            for i in range(0, data_number, NOMBRE_MEMBRE_PAR_STEP):

                cur.execute(
                    "SELECT discord_id FROM country ORDER BY id LIMIT " + str(NOMBRE_MEMBRE_PAR_STEP) + " OFFSET ?",
                    [i])
                count = 0
                for discord_id in cur:
                    await asyncio.sleep(5.1)
                    count += 1
                    data = utils.database(self, "country", "discord_id", discord_id[0])

                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
                    }
                    response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["ingame_name"]}',
                                            headers=headers)
                    user = guild.get_member(data["discord_id"])

                    if user is None:
                        await data_bot.send(
                            f"Le joueur <@{data['discord_id']}> ({data['ingame_name']}) a quitté le discord.")
                        leave += 1
                        user = None
                    if response.status_code != 200:
                        await data_bot.send(
                            f"Le joueur <@{data['discord_id']}> ({data['ingame_name']}) provoque un crash de l'API NationsGlory. *code erreur: E-N-01*")
                        api_error += 1
                        api_data = None
                    elif "error" in response.json():
                        if response.json()["error"] == "unknown.user":  # Joueur non détecter
                            unrecognized += 1
                            if user is not None:
                                await user.remove_roles(guild.get_role(config["grades"]["link"]))
                        else:
                            await data_bot.send(
                                f"Le joueur <@{data['discord_id']}> ({data['ingame_name']}) provoque un crash de l'API NationsGlory. *code erreur: E-N-02*")
                        api_data = None
                    else:
                        api_data = {
                            "country": response.json()["servers"]["green"]["country"],
                            "last_connection": response.json()["last_connection"],
                        }
                    await self.country_check_user(data, api_data, user)
                line1.update(count)
                await message.edit(content=str(line1))
        cur.close()
        await data_bot.send("└--------------------------------┫ Arrêt du check de la db de pays ┠--------------------------------┘")
        await data_log.send(
            f"Check de la db de pays terminé ! Sur un total de ``{data_number}`` personnes, ``{unrecognized}`` n'ont pas été reconnue (``{(unrecognized / data_number) * 100}%``). ``{leave}`` personnes ont quitté le discord (comprend aussi ceux revenus). Le bot a rencontré ``{api_error}`` erreurs d'API.")

    async def country_check_user(self, data, api_data, user):

        cur = self.bot.players.cursor()
        guild = self.bot.get_guild(config["guild_id"])
        data_bot = guild.get_channel(config["channels"]["data_bot"])

        if user is None:
            return

        # vérifie si le joueur existe bien IG
        if api_data is None:
            await data_bot.send(
                f"L'utilisateur enregistrer sous le nom de {data['ingame_name']} ({user.mention}) n'existe pas IG (ID: {data['id']})")
            return

        if user.get_role(config["grades"]["nouvelle_recrue"]) is None:
            await data_bot.send(
                f"Le joueur <@{data['discord_id']}> ({data['ingame_name']}) a quitté le discord et est revenu.")

        # Actualisation pays
        if data["country"] != api_data["country"] and (data["country"] != "bypass"):
            cur.execute("UPDATE country SET country=? WHERE discord_id=?", [api_data["country"], data["discord_id"]])

            # TODO: Système qui retire les grades liés aux pays. Actuellement hardcodé. A lié au variable_config dans une futur version avec une commande sur discord pour modifier la dite-config
            await user.remove_roles(guild.get_role(config["grades"]["pays"]["guyana"]))
            await user.remove_roles(guild.get_role(config["grades"]["pays"]["venezuela"]))

            if api_data["country"] == "Guyana":
                await user.add_roles(guild.get_role(config["grades"]["pays"]["guyana"]))
            elif api_data["country"] == "Venezuela":
                await user.add_roles(guild.get_role(config["grades"]["pays"]["venezuela"]))

        if (not api_data["country"] in ["Guyana", "Venezuela"]) and (data["country"] != "bypass"):
            await data_bot.send(
                f"L'utilisateur {data['ingame_name']} ({user.mention}) n'est plus dans l'un des pays GDE et ne dispose d'aucune autorisation a cette effet.")

        # Inactivité
        if api_data is not None:
            jours_deco = (date.today() - datetime.fromisoformat(api_data["last_connection"]).date()).days
            cur.execute("UPDATE country SET last_connection=? WHERE discord_id=?",
                        [jours_deco, data["discord_id"]])

            if jours_deco >= 3 and (data["absence"] is None) and data["grade"] == 0:
                await data_bot.send(
                    f"L'utilisateur {data['ingame_name']} ({user.mention}) est absent depuis {jours_deco} jours.")
            elif jours_deco >= 5 and (data["absence"] is None) and data["grade"] == 1:
                await data_bot.send(
                    f"L'utilisateur {data['ingame_name']} ({user.mention}) est absent depuis {jours_deco} jours.")
            elif jours_deco >= 7 and (data["absence"] is None) and data["grade"] == 2:
                await data_bot.send(
                    f"L'utilisateur {data['ingame_name']} ({user.mention}) est absent depuis {jours_deco} jours.")
            elif jours_deco >= 14 and (data["absence"] is None) and data["grade"] == 3:
                await data_bot.send(
                    f"L'utilisateur {data['ingame_name']} ({user.mention}) est absent depuis {jours_deco} jours.")
            elif jours_deco >= 31 and (data["absence"] is None) and data["grade"] >= 4:
                await data_bot.send(
                    f"L'utilisateur {data['ingame_name']} ({user.mention}) est absent depuis {jours_deco} jours.")

        # fin absence
        if data["absence"] is not None and date.today() >= date.fromisoformat(data["absence"]):
            cur.execute("UPDATE country SET absence=? WHERE discord_id=?", [None, data["discord_id"]])

            if data["grade"] == 1:
                grade = "Recrue+"
            elif data["grade"] == 2:
                grade = "Membre"
            elif data["grade"] == 3:
                grade = "Membre+"
            elif data["grade"] == 4:
                grade = "Offi"
            elif data["grade"] == 5:
                grade = "Gouverneur"
            elif data["grade"] == 6:
                grade = "Second"
            else:
                grade = "Recrue"
            try:
                await user.edit(nick=f"{grade} | {data['ingame_name']}")
            except AttributeError:
                pass

        # Ancienneté
        if date.today() - date.fromisoformat(data["recruitment_date"]) >= timedelta(days=5) and data["age_badge"] != 1:
            cur.execute("UPDATE country SET age_badge=1 WHERE discord_id=?", [data["discord_id"]])
        if date.today() - date.fromisoformat(data["recruitment_date"]) >= timedelta(days=14) and data["age_badge"] != 2:
            cur.execute("UPDATE country SET age_badge=2 WHERE discord_id=?", [data["discord_id"]])
        if date.today() - date.fromisoformat(data["recruitment_date"]) >= timedelta(days=30) and data["age_badge"] != 3:
            cur.execute("UPDATE country SET age_badge=3 WHERE discord_id=?", [data["discord_id"]])
        if date.today() - date.fromisoformat(data["recruitment_date"]) >= timedelta(days=90) and data["age_badge"] != 4:
            cur.execute("UPDATE country SET age_badge=4 WHERE discord_id=?", [data["discord_id"]])
        if date.today() - date.fromisoformat(data["recruitment_date"]) >= timedelta(days=365) and data["age_badge"] != 5:
            cur.execute("UPDATE country SET age_badge=5 WHERE discord_id=?", [data["discord_id"]])

        self.bot.players.commit()
        cur.close()

    async def diplomatic_check(self):
        guild = self.bot.get_guild(config["guild_id"])
        data_log = guild.get_channel(config["channels"]["data_log"])
        api_error = []
        unrecognized = 0
        delete = 0

        cur = self.bot.players.cursor()
        cur.execute("SELECT count(*) FROM diplomacy")
        data_number = int(cur.fetchone()[0])
        with tqdm(total=data_number, unit="member", ascii="⬡⬢", bar_format='{l_bar}{bar:25}{r_bar}{bar:-10b}',
                  desc="Check de la db diplomacy ") as line1:
            message = await data_log.send(str(line1))
            for i in range(0, data_number, NOMBRE_MEMBRE_PAR_STEP):
                cur.execute(
                    "SELECT discord_id FROM diplomacy ORDER BY id LIMIT " + str(NOMBRE_MEMBRE_PAR_STEP) + " OFFSET ?",
                    [i - delete])
                count = 0
                for discord_id in cur:
                    await asyncio.sleep(5.1)
                    count += 1
                    data = utils.database(self, "diplomacy", "discord_id", discord_id[0])

                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
                    }
                    response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["ingame_name"]}',
                                            headers=headers)
                    user = guild.get_member(data["discord_id"])

                    if user is None:
                        delete += 1
                        cur.execute("DELETE FROM diplomacy WHERE discord_id = ?", [discord_id])
                        self.bot.players.commit()
                    else:
                        if response.status_code != 200:
                            api_error.append(discord_id)
                        if (user.get_role(config["grades"]["doyen"]) or user.get_role(
                                config["grades"]["conseiller"])) is None:
                            try:  # Rename suivant situation
                                if "error" in response.json():
                                    if response.json()["error"] == "unknown.user":  # Joueur non détecter
                                        if len(f"Unlink | {data['ingame_name']}") <= 32:
                                            await user.edit(nick=f"Unlink | {data['ingame_name']}")
                                        elif len(f"{data['ingame_name']}") <= 32:
                                            await user.edit(nick=f"{data['ingame_name']}")
                                        await user.remove_roles(guild.get_role(config["grades"]["link"]))
                                        unrecognized += 0
                                    else:
                                        api_error.append(discord_id)
                                else:
                                    api_data = {
                                        "country": response.json()["servers"]["green"]["country"],
                                        "country_rank": response.json()["servers"]["green"]["country_rank"],
                                    }
                                    await user.add_roles(guild.get_role(config["grades"]["link"]))
                                    if len(f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})") <= 32:
                                        await user.edit(
                                            nick=f"{api_data['country']} | {data['ingame_name']} ({api_data['country_rank']})")
                                    elif len(f"{api_data['country']} | {data['ingame_name']}") <= 32:
                                        await user.edit(nick=f"{api_data['country']} | {data['ingame_name']}")
                                    else:
                                        await user.edit(nick=f"{data['ingame_name']}")
                            except discord.errors.Forbidden:
                                pass
                line1.update(count)
                await message.edit(content=str(line1))

        cur.close()
        if not api_error:
            text = "."
        else:
            text = " sur les personnes suivantes:"
            for discord_id in api_error:
                text += f" <@{discord_id}>"
            text += "."
        await data_log.send(
            f"Check de la db diplomatique terminé ! Sur un total de ``{data_number}`` personnes, ``{unrecognized}`` n'ont pas été reconnue (``{(unrecognized / data_number) * 100}%``). ``{delete}`` personnes ont quitter le discord et ont donc été supprimer de la db diplomatique. Le bot a rencontré ``{api_error}`` erreurs d'API{text}")
