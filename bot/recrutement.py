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
    print('Loading cog recrutement')
    bot.add_cog(Recrutement(bot))


class Recrutement(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # Cooldown pour Check des salons discord AFK
    async def start_check_loop(self):
        while True:
            await asyncio.sleep(6 * 60 * 60)
            await asyncio.create_task(self.discord_channel_check())

    # ------------------------------------------------------------------------------------------
    #                                         Commands
    # ------------------------------------------------------------------------------------------

    # Command /bvn
    @commands.slash_command(description="Permet de finir le recrutement d'un candidat.", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["recruteur"])
    async def bvn(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur."), referent: Option(discord.User, "Référent du joueur", required=False), schematique: Option(str, "Schématique du joueur.", required=False),
                  regiment: Option(str, "Régiment du joueur.", choices=config["regiments"], required=False)):

        cur = self.bot.countrydb.cursor()
        data = cur.execute("SELECT grade, pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if regiment is None:
            regiment = "Frontaliers"
        if data is None or data[0] != 0:
            await ctx.respond("L'utilisateur n'est pas candidat")
            return

        guild = self.bot.get_guild(config["guild_id"])
        member_guild = guild.get_member(user.id)

        if referent is None:
            referent = ctx.user

        await ctx.respond(f"{user.name} est passé de Candidat à Nouvelle Recrue.")

        cur.execute("UPDATE recrutement SET grade=1 WHERE id_discord=?", [user.id])
        cur.execute("UPDATE recrutement SET schematique=? WHERE id_discord=?", [schematique, user.id])
        cur.execute("UPDATE recrutement SET regiment=? WHERE id_discord=?", [regiment, user.id])
        cur.execute("UPDATE recrutement SET referent=? WHERE id_discord=?", [referent.id, user.id])

        self.bot.countrydb.commit()
        cur.close()

        if len(f"Recrue | {data[1]}") <= 32:
            await member_guild.edit(nick=f"Recrue | {data[1]}")

        await member_guild.add_roles(guild.get_role(config["roles"]["grades"]["nouvelle_recrue"]))
        text = f"<@&{config['roles']['grades']['nouvelle_recrue']}>"
        for role in config["roles"]["deco"]["pays"]:
            await member_guild.add_roles(guild.get_role(role))
            text += f", <@&{role}>"
        await member_guild.add_roles(guild.get_role(config["roles"]["regiments"][regiment]))
        text += f"<@&{config['roles']['regiments'][regiment]}>"

        await member_guild.remove_roles(guild.get_role((config["roles"]["grades"]["frontier_recrutement"])))

        embed = utils.create_embed(self.bot, title="Rôles obtenus :", description=f"{text}", color=Color.gold())
        await ctx.channel.send(embed=embed)

        channel_gg = guild.get_channel(config["channels"]["rank_uwu"])
        msg = await channel_gg.send(f"Félicitation à {user.mention} qui passe Nouvelle recrue. Bienvenue à lui dans le pays ! 🎉")
        emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
        await msg.add_reaction(emoji)

        channel_general = guild.get_channel(config["channels"]["general"])
        await channel_general.send(random.choice(config["welcome_message"]).format(name=user.mention))
        await channel_general.send(f"La personne qui ce chargera de le guider au sain du pays est {referent.mention}")

    # Command /remove-user
    @commands.slash_command(name="remove-user", description="Permet d'effacer un joueur de la base de données", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def remove_user(self, ctx: discord.ApplicationContext, pseudo: Option(str, "Entre un pseudo IG."),
                          de: Option(str, "db de pays ou de diplomatie.", choices=["Pays", "Diplomatie"], required=False, default="Pays")):

        if de == "Pays":
            cur = self.bot.countrydb.cursor()
            try:
                temp = cur.execute("SELECT id_discord FROM recrutement WHERE pseudo_ingame=?", [pseudo]).fetchone()
                if temp is None:
                    await ctx.respond("Utilisateur absent de la base de donnée de pays")
                    return
                user_id = temp[0]
                user = ctx.guild.get_member(user_id)
                cur.execute("DELETE FROM recrutement WHERE pseudo_ingame = ?", [str(pseudo)])
                cur.execute("SELECT changes()")
                if cur.fetchone()[0] == 0:
                    await ctx.respond("Utilisateur absent de la base de données")
                else:
                    self.bot.countrydb.commit()
                    if user is not None:
                        try:
                            await user.edit(nick=None)
                        except discord.errors.Forbidden:
                            pass
                    await ctx.respond(f"<@{user_id}> a correctement été supprimer de la base de données. **Ces grades ne lui pas été retirés !**")
            except IntegrityError or TypeError or discord.errors.ApplicationCommandInvokeError:
                await ctx.respond("Utilisateur absent de la base de données")
            finally:
                cur.close()
        else:
            cur = self.bot.worlddb.cursor()
            try:
                temp = cur.execute("SELECT id_discord FROM diplomatie WHERE pseudo_ingame=?", [pseudo]).fetchone()
                if temp is None:
                    await ctx.respond("Utilisateur absent de la base de donnée diplomatique")
                    return
                user_id = temp[0]
                user = ctx.guild.get_member(user_id)
                cur.execute("DELETE FROM diplomatie WHERE pseudo_ingame = ?", [str(pseudo)])
                cur.execute("SELECT changes()")
                if cur.fetchone()[0] == 0:
                    await ctx.respond("Utilisateur absent de la base de données")
                else:
                    self.bot.worlddb.commit()
                    if user is not None:
                        try:
                            await user.edit(nick=None)
                        except discord.errors.Forbidden:
                            pass
                    await ctx.respond(f"<@{user_id}> a correctement été supprimer de la base de données. **Ces grades ne lui pas été retirés !**")
            except IntegrityError or TypeError or discord.errors.ApplicationCommandInvokeError:
                await ctx.respond("Utilisateur absent de la base de données")
            finally:
                cur.close()

    # Command /confirme-diplomate
    @commands.slash_command(name="confirme-diplomate", description="Permet de terminer l'enregistrement d'un diplomate", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def confirme_diplomate(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un pseudo.")):

        if ctx.channel.category.id != config["recrutement_category"]:
            await ctx.respond("Ce channel n'est pas un ticket de diplomatie !", ephemeral=True)
            return

        await user.add_roles(ctx.guild.get_role(config["roles"]["grades"]["confirmed"]))
        await user.remove_roles(ctx.guild.get_role(config["roles"]["grades"]["unconfirmed"]))
        await ctx.channel.delete()

    # Command /start-register
    @commands.slash_command(name="start-register", description="Commencer un enregistrement comme si on venait de rejoindre le discord")
    async def start_register(self, ctx: discord.ApplicationContext):
        if ctx.channel.id != config["channels"]["unregister"]:
            await ctx.respond(f"Cette commande ne peu pas être faite ici !")
            return
        member = ctx.user
        await ctx.respond(f"Enregistrement lancé {member.mention} !", delete_after=10)

        guild = self.bot.get_guild(config["guild_id"])
        recrutement_category = guild.get_channel(config["recrutement_category"])

        overwrites = {
            guild.me: discord.PermissionOverwrite(view_channel=True),
            member: discord.PermissionOverwrite(view_channel=True),
            guild.get_role(config["roles"]["grades"]["recruteur"]): discord.PermissionOverwrite(view_channel=True)
        }
        channel = await guild.create_text_channel(name=f"{member.display_name}", category=recrutement_category, overwrites=overwrites)

        embed = utils.create_embed(self.bot, title="**Bonjour, bienvenue sur le discord de la GDE !**",
                                   description=f"Je suis le bot en charge du discord. C'est dans ce channel que tu vas te faire enregistrer. Après 48h d'inactivité, ce channel sera automatiquement supprimer.\n\nEn premier lieu, je t'invite a lire le règlement. Je pense qu'il n'y a pas raison de beaucoup écrire la dessus. Vous connaissez les normes \"classique\" :\n> ╰Toujours resté poli\n> ╰Pseudo et photo de profil correcte\n> ╰Pas de NSFW\n> ╰Respect des autres\n> ╰Pas de spam\n> ╰Pas de GhostPing. \n> ╰En cas de problème on vas voir les plus hauts grades\n \n**Si tout ceci est claire, je t'invite a cliqué sur le bouton ci-dessous**",
                                   color=Color.gold())
        await channel.send(embed=embed, view=ReglementView(self.bot))
        await channel.send(f"{member.mention}", delete_after=0)

    # Command /fc-channels-recrutements
    @commands.slash_command(description="Lance immédiatement le check des salons de recrutement inactifs", default_permission=False, name="fc-channels-recrutements")
    @commands.has_any_role(config["roles"]["grades"]["officier"])
    async def force_check_channels_recrutements(self, ctx: discord.ApplicationContext):
        await ctx.respond("Check des salons de recrutements afk lancer")
        await self.discord_channel_check()

    # ------------------------------------------------------------------------------------------
    #                               Éléments supplémentaires
    # ------------------------------------------------------------------------------------------

    # Détection arriver nouveau membre
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(config["guild_id"])
        recrutement_category = guild.get_channel(config["recrutement_category"])

        overwrites = {
            guild.me: discord.PermissionOverwrite(view_channel=True),
            member: discord.PermissionOverwrite(view_channel=True),
            guild.get_role(config["roles"]["grades"]["recruteur"]): discord.PermissionOverwrite(view_channel=True)
        }
        channel = await guild.create_text_channel(name=f"{member.display_name}", category=recrutement_category, overwrites=overwrites)

        embed = utils.create_embed(self.bot, title="**Bonjour, bienvenue sur le discord de la GDE !**",
                                   description=f"Je suis le bot en charge du discord. C'est dans ce channel que tu vas te faire enregistrer. Après 48h d'inactivité, ce channel sera automatiquement supprimer.\n\nEn premier lieu, je t'invite a lire le règlement. Je pense qu'il n'y a pas raison de beaucoup écrire la dessus. Vous connaissez les normes \"classique\" :\n> ╰Toujours resté poli\n> ╰Pseudo et photo de profil correcte\n> ╰Pas de NSFW\n> ╰Respect des autres\n> ╰Pas de spam\n> ╰Pas de GhostPing. \n> ╰En cas de problème on vas voir les plus hauts grades\n \n**Si tout ceci est claire, je t'invite a cliqué sur le bouton ci-dessous**",
                                   color=Color.gold())
        await channel.send(embed=embed, view=ReglementView(self.bot))
        await channel.send(f"{member.mention}", delete_after=0)

    # Quand mp
    @commands.Cog.listener()
    async def on_message(self, msg):
        if isinstance(msg.channel, DMChannel) and msg.author.id != self.bot.user.id:
            await msg.channel.send("Voici notre discord : https://discord.gg/7smZu3knk8")

    # Check des salons discord AFK
    async def discord_channel_check(self):
        guild = self.bot.get_guild(config["guild_id"])
        recrutement_category = get(guild.categories, id=config["recrutement_category"])
        channels = recrutement_category.channels
        data_log = guild.get_channel(config["channels"]["data_log"])
        supprimer = 0
        afk = 0
        with tqdm(total=len(channels), unit="member", ascii="⬡⬢", bar_format='{l_bar}{bar:25}{r_bar}{bar:-10b}', desc="Vérification des channels inactifs ") as line1:
            bar = await data_log.send(line1)
            for category in channels:
                channel = guild.get_channel(category.id)
                if channel.type == discord.ChannelType.text:
                    messages = await channel.history(limit=1).flatten()
                    last_message_date = messages[0].created_at.astimezone(pytz.utc)
                    delay = datetime.datetime.now(pytz.utc) - last_message_date
                    if delay >= timedelta(days=1) and (channel.id not in config["channels"]["admin_channels_from_recrutement_category"]):
                        try:
                            if (messages[0].author.id != self.bot.user.id) or (messages[0].embeds[0].to_dict()["fields"][0]["value"] != "AFK depuis 24h"):
                                embed = utils.create_embed(self.bot, title="**Channel inactif !**",
                                                           description=f"Aucun message n'a été envoyer dans ce channel depuis 24h, Si aucun message n'est envoyé dans les 24h prochaines heures, ce channel sera supprimer.",
                                                           color=Color.gold())
                                embed.add_field(name=f"Statut :", value="AFK depuis 24h", inline=True)
                                await channel.send(embed=embed)
                                afk += 1
                            else:
                                await channel.delete()
                                supprimer += 1
                        except IndexError:
                            embed = utils.create_embed(self.bot, title="**Channel inactif !**",
                                                       description=f"Aucun message n'a été envoyer dans ce channel depuis 24h, Si aucun message n'est envoyé dans les 24h prochaines heures, ce channel sera supprimer.",
                                                       color=Color.gold())
                            embed.add_field(name=f"Statut :", value="AFK depuis 24h", inline=True)
                            await channel.send(embed=embed)
                            afk += 1

                line1.update(1)
                await bar.edit(content=line1)
        await data_log.send(f"Vérification des channels inactifs terminé ! ``{afk}`` salons supplémentaires ont été mis comme AFK et ``{supprimer}`` ont été supprimés !")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.start_check_loop()


# Setup le bouton "Valider le règlement"
class ReglementView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Valider le règlement", style=discord.ButtonStyle.green, emoji="✅", custom_id="button-confirm")
    async def button_callback(self, button, interaction):
        guild = self.bot.get_guild(config["guild_id"])

        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.user.add_roles(guild.get_role(config["roles"]["grades"]["reglement_valider"]))

        embed = utils.create_embed(self.bot, title="Rôle obtenu :",
                                   description=f"<@&{config['roles']['grades']['reglement_valider']}>",
                                   color=Color.gold())
        await interaction.followup.send(embed=embed)

        embed = utils.create_embed(self.bot, title="Maintenant, dit nous pourquoi tu viens :",
                                   description=f"- Si tu vient pour te faire recruter, click sur le bouton \"Recrutement\".\n- Si tu vient en temps que représentant d'un autre pays, click sur le bouton \"Diplomatie\".",
                                   color=Color.gold())
        await interaction.followup.send(embed=embed, view=DirectionSwitcherView(self.bot))


# Setup les boutons "Recrutement" et "Diplomatie"
class DirectionSwitcherView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Recrutement", style=discord.ButtonStyle.secondary, emoji="📑", custom_id="button-recrutement")
    async def recrutement_button_callback(self, button, interaction):
        await interaction.response.send_modal(RecrutementRegisterModal(self.bot))

    @discord.ui.button(label="Diplomatie", style=discord.ButtonStyle.secondary, emoji="🕊️", custom_id="button-diplomatie")
    async def diplomatie_button_callback(self, button, interaction):
        await interaction.response.send_modal(DiplomatieRegisterModal(self.bot))


class ConfirmePseudoDiplomatieView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="C'est bien moi", style=discord.ButtonStyle.green, emoji="✔️", custom_id="button-confirmepseudodiplomatie")
    async def confirme_pseudo_button_callback(self, button, interaction):

        # Récup le pseudo du joueur et son pays
        if interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Joueur non reconnu":
            data = {
                "pseudo": interaction.message.embeds[0].to_dict()["fields"][1]["value"],
                "id_discord": interaction.user.id,
            }
            api_ok = 0

        elif interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Joueur reconnu":
            data = {
                "pseudo": interaction.message.embeds[0].to_dict()["fields"][1]["value"],
                "id_discord": interaction.user.id,
                "country": interaction.message.embeds[0].to_dict()["fields"][2]["value"],
                "country_rank": interaction.message.embeds[0].to_dict()["fields"][3]["value"]
            }
            api_ok = 1

            if (data["country"] == "") or (data["country"] is None):
                data["country"] = "Wilderness"
                data["country_rank"] = " "

        else:
            embed = utils.create_embed(self.bot, f"**Erreur technique**", description=f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
            await interaction.channel.send(embed=embed)
            return

        # Enregistre + check pas de contradiction avec world db
        cur = self.bot.worlddb.cursor()
        temp = cur.execute("SELECT * FROM diplomatie WHERE id_discord=?", [data["id_discord"]]).fetchone()

        if temp is not None:
            cur.execute("DELETE FROM diplomatie WHERE id_discord=?", [data["id_discord"]])
            cur.close()

        cur.execute("INSERT INTO diplomatie (id_discord, pseudo_ingame) VALUES (:id_discord, :pseudo)", data)
        self.bot.worlddb.commit()
        cur.close()

        # Rename user + add role
        await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["unconfirmed"]))
        await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["neutre"]))
        text = f"<@&{config['roles']['grades']['unconfirmed']}>, <@&{config['roles']['grades']['neutre']}>"

        for role in config["roles"]["deco"]["global"]:
            await interaction.user.add_roles(interaction.guild.get_role(role))
            text += f", <@&{role}>"

        if interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Joueur reconnu":
            await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["link"]))
            text += f", <@&{config['roles']['grades']['link']}>"

        button.disabled = True
        button_edit = [x for x in self.children if x.custom_id == "button-editDiplomatie"][0]
        button_edit.disabled = True
        await interaction.response.edit_message(view=self)

        if api_ok == 0:
            if len(f"Unlink | {data['pseudo']}") <= 32:
                await interaction.user.edit(nick=f"Unlink | {data['pseudo']}")
            elif len(f"{data['pseudo']}") <= 32:
                await interaction.user.edit(nick=f"{data['pseudo']}")
        else:
            if len(f"{data['country']} | {data['pseudo']} ({data['country_rank']})") <= 32:
                await interaction.user.edit(nick=f"{data['country']} | {data['pseudo']} ({data['country_rank']})")
            elif len(f"{data['country']} | {data['pseudo']}") <= 32:
                await interaction.user.edit(nick=f"{data['country']} | {data['pseudo']}")
            else:
                await interaction.user.edit(nick=f"{data['pseudo']}")

        embed = utils.create_embed(self.bot, title="Rôles obtenus :", description=f"{text}", color=Color.gold())
        await interaction.channel.send(embed=embed)

        embed = utils.create_embed(self.bot, title="**Pings :**",
                                   description=f"Tu peux maintenant choisir des pings personnalisés :\n\n<@&{config['roles']['pings']['notations']}> : Pour être mentionné pour les notations du pays (une fois par semaine).\n\n<@&{config['roles']['pings']['discord']}> : Pour être mentionné pour les mises a jours du discord, les nouveautés.\n\n<@&{config['roles']['pings']['media']}> : Pour être mentionné pour les vidéos et lives des membres du pays.\n\n<@&{config['roles']['pings']['secondaire']}> : Pour être mentionné pour les informations secondaires, les événements auxquelles ont participe hors de NationsGlory.\n\nCes paramètres peuvent être modifiés avec la commande /ping",
                                   color=Color.gold())
        embed.add_field(name=f"Statut :", value="Diplomate", inline=True)
        await interaction.channel.send(embed=embed, view=PingView(self.bot))

    @discord.ui.button(label="Entrée un autre pseudo", style=discord.ButtonStyle.danger, emoji="✏️", custom_id="button-editDiplomatie")
    async def edit_diplomatie_button_callback(self, button, interaction):
        await interaction.response.send_modal(DiplomatieRegisterModal(self.bot))


class ConfirmePseudoRecrutementView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="C'est bien moi", style=discord.ButtonStyle.green, emoji="✔️", custom_id="button-confirmepseudorecrutement")
    async def confirme_pseudo_recru_button_callback(self, button, interaction):

        # Récup le pseudo du joueur et son pays
        if interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Joueur non reconnu":
            data = {
                "pseudo_ingame": interaction.message.embeds[0].to_dict()["fields"][1]["value"],
                "annee_naissance": interaction.message.embeds[0].to_dict()["fields"][2]["value"],
                "experience": interaction.message.embeds[0].to_dict()["fields"][3]["value"],
                "pays": " ",
                "id_discord": interaction.user.id,
                "date_recrutement": date.today()
            }

        else:
            data = {
                "pseudo_ingame": interaction.message.embeds[0].to_dict()["fields"][1]["value"],
                "annee_naissance": interaction.message.embeds[0].to_dict()["fields"][2]["value"],
                "experience": interaction.message.embeds[0].to_dict()["fields"][3]["value"],
                "pays": interaction.message.embeds[0].to_dict()["fields"][4]["value"],
                "id_discord": interaction.user.id,
                "date_recrutement": date.today()
            }

        # Enregistre + check pas de contradiction avec country db
        cur = self.bot.countrydb.cursor()
        temp = cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [data["id_discord"]]).fetchone()

        if temp is not None:
            cur.execute("DELETE FROM recrutement WHERE id_discord=?", [data["id_discord"]])
            self.bot.countrydb.commit()

        cur.execute(
            "INSERT INTO recrutement (id_discord, pseudo_ingame, annee_naissance, experience, pays, date_recrutement) VALUES (:id_discord, :pseudo_ingame, :annee_naissance, :experience, :pays, :date_recrutement)", data)
        self.bot.countrydb.commit()
        cur.close()

        # Rename user + add role
        await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["confirmed"]))
        await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["neutre"]))
        text = f"<@&{config['roles']['grades']['unconfirmed']}>, <@&{config['roles']['grades']['neutre']}>"

        for role in config["roles"]["deco"]["global"]:
            await interaction.user.add_roles(interaction.guild.get_role(role))
            text += f", <@&{role}>"

        if interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Joueur reconnu":
            await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["link"]))
            text += f", <@&{config['roles']['grades']['link']}>"

        button.disabled = True
        button_edit = [x for x in self.children if x.custom_id == "button-editRecrutement"][0]
        button_edit.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.user.edit(nick=f"Candidat | {data['pseudo_ingame']}")

        embed = utils.create_embed(self.bot, title="Rôles obtenus :", description=f"{text}", color=Color.gold())
        await interaction.channel.send(embed=embed)

        embed = utils.create_embed(self.bot, title="**Pings :**",
                                   description=f"Tu peux maintenant choisir des pings personnalisés :\n\n<@&{config['roles']['pings']['notations']}> : Pour être mentionné pour les notations du pays (une fois par semaine).\n\n<@&{config['roles']['pings']['discord']}> : Pour être mentionné pour les mises a jours du discord, les nouveautés.\n\n<@&{config['roles']['pings']['media']}> : Pour être mentionné pour les vidéos et lives des membres du pays.\n\n<@&{config['roles']['pings']['secondaire']}> : Pour être mentionné pour les informations secondaires, les événements auxquelles ont participe hors de NationsGlory.\n\nCes paramètres peuvent être modifiés avec la commande ``/pings``",
                                   color=Color.gold())
        embed.add_field(name=f"Statut :", value="Candidat", inline=True)
        await interaction.channel.send(embed=embed, view=PingView(self.bot))

    @discord.ui.button(label="Entrée un autre pseudo", style=discord.ButtonStyle.danger, emoji="✏️", custom_id="button-editRecrutement")
    async def edit_recrutement_button_callback(self, button, interaction):
        await interaction.response.send_modal(RecrutementRegisterModal(self.bot))


class PingView(View):
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

    @discord.ui.button(label="Secondaire", style=discord.ButtonStyle.secondary, emoji="🧶", custom_id="button-secondaire")
    async def secondaire_button_callback(self, button, interaction):
        guild = self.bot.get_guild(config["guild_id"])

        if button.style == discord.ButtonStyle.secondary:
            button.style = discord.ButtonStyle.green
            await interaction.user.add_roles(guild.get_role(config["roles"]["pings"]["secondaire"]))
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.secondary
            await interaction.user.remove_roles(guild.get_role(config["roles"]["pings"]["secondaire"]))
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Confirme", style=discord.ButtonStyle.red, emoji="✔️", custom_id="button-confirme")
    async def confirme_button_callback(self, button, interaction):
        button.disabled = True
        button_notations = [x for x in self.children if x.custom_id == "button-notations"][0]
        button_discord = [x for x in self.children if x.custom_id == "button-discord"][0]
        button_media = [x for x in self.children if x.custom_id == "button-media"][0]
        button_secondaire = [x for x in self.children if x.custom_id == "button-secondaire"][0]
        button_notations.disabled = True
        button_discord.disabled = True
        button_media.disabled = True
        button_secondaire.disabled = True
        await interaction.response.edit_message(view=self)

        if interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Diplomate":
            embed = utils.create_embed(self.bot, title="Dernière étape :",
                                       description=f"Tu a finit de te faire enregistrer. Tu peu maintenant demander ici les grades que tu souhaite obtenir, n'hésite pas a en faire la demande si dessous 👇.",
                                       color=Color.gold())
            embed.add_field(name="Grades relations que tu peu obtenir :",
                            value="> ╰Allié : Si tu est en bon terme avec notre faction, tu peu récupérer ce grade pour obtenir les accès sur l'espace publique GDE.\n> ╰Colonie : Si tu a été coloniser par un de nos pays, tu peu demander ce grade, purement décoratif.\n> ╰Amis : Pour les amis des membres du pays, sort de grade Allié++, donne des accès sur le discord semblable a une recrue confirmé.\n> ╰Confiance : Pour les personne de toute confiance (anciens officiers, etc), donne des accès sur le discord semblable a un officier.",
                            inline=True)
            embed.add_field(name="Grades médailles que tu peu obtenir :",
                            value="> ╰Stp drop un red (alias OP green) : Pour les Super-Modo et Administrateurs du Green.\n> ╰Modo : Pour les Modo du Green.\n> ╰Guide : Pour les Guides du Green.", inline=True)
            await interaction.channel.send(embed=embed)

        if interaction.message.embeds[0].to_dict()["fields"][0]["value"] == "Candidat":
            await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["grades"]["frontier_recrutement"]))
            hub_recrutement = interaction.guild.get_channel(config["channels"]["hub_recrutement"])
            await hub_recrutement.send(
                f"Tu a finit de te faire enregistrer {interaction.user.mention}. Tu va maintenant devoir vocal avec un <@&{config['roles']['grades']['recruteur']}>, n'hésite pas a dire quand tu est disponible ci-dessous 👇.")
            await interaction.channel.delete()


# Setup le formulaire recrutement de la modale
class RecrutementRegisterModal(Modal):
    def __init__(self, bot: GuyaBot) -> None:
        self.bot = bot
        super().__init__(title="Enregistrement")
        self.add_item(InputText(label="Pseudo en jeu", placeholder="Tominix356"))
        self.add_item(InputText(label="Âge (\"-1\" pour ne pas le donner)", placeholder="18", style=discord.InputTextStyle.short, min_length=1, max_length=3))
        self.add_item(InputText(label="Expérience sur NG", placeholder="Mon expérience...", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = {
            "id_discord": interaction.user.id,
            "pseudo_ingame": self.children[0].value,
            "annee_naissance": (date.today().year - int(self.children[1].value)) if self.children[1].value.isnumeric() and self.children[1].value != "-1" else -1,
            "experience": self.children[2].value,
            "date_recrutement": date.today()
        }

        if len({data['pseudo_ingame']}) > 20:
            await interaction.followup.send("Ce pseudo ingame est trop long !")
            return

        # Vérifie si pas de contradiction avec la world db
        cur = self.bot.worlddb.cursor()

        cur.execute("SELECT count(*) FROM diplomatie WHERE id_discord=?", [data["id_discord"]])
        find = cur.fetchone()
        if not find[0] == 0:
            await interaction.followup.send("Ce compte discord est déjà enregistré dans nos registre de diplomatie ! Merci de prendre contacte avec un officier.")
            cur.close()
            return

        cur.execute("SELECT count(*) FROM diplomatie WHERE pseudo_ingame=?", [data["pseudo_ingame"]])
        find = cur.fetchone()
        if not find[0] == 0:
            await interaction.followup.send("Ce pseudo IG est déjà enregistré dans nos registre de diplomatie ! Merci de prendre contacte avec un officier.")
            cur.close()
            return

        cur.close()

        cur = self.bot.countrydb.cursor()

        cur.execute("SELECT count(*) FROM recrutement WHERE pseudo_ingame=?", [data["pseudo_ingame"]])
        find = cur.fetchone()
        if not find[0] == 0:
            await interaction.followup.send("Ce pseudo ingame est déjà enregistré dans nos registre de recrutement ! Merci de prendre contacte avec un officier.")
            cur.close()
            return

        cur.close()

        # Prend les infos de l'API
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {config["api_key"]}',
        }
        response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["pseudo_ingame"]}', headers=headers)

        if response.status_code != 200:
            embed = utils.create_embed(self.bot, f"**Erreur technique**", description=f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
            await interaction.followup.send(embed=embed)
            return

        if "error" in response.json():
            if response.json()["error"] == "unknown.user":
                embed = utils.create_embed(self.bot, title="**Problème !**",
                                           description=f"Après vérification, nous n'avons détecter aucun joueur portant le pseudo ``{data['pseudo_ingame']}`` sur le serveur Green. Es tu sûr de n'avoir fait aucune erreur en l'écrivant ? Les majuscules sont importantes ! Si tu ne t'es encore jamais connecter sur le Green, alors c'est normal, sinon merci d'entrée un autre pseudo.",
                                           color=Color.gold())
                embed.add_field(name="Statut :", value=f"Joueur non reconnu")
                embed.add_field(name="Pseudo IG :", value=f"{data['pseudo_ingame']}")
                embed.add_field(name="Année :", value=f"{data['annee_naissance']}")
                embed.add_field(name="Experience :", value=f"{data['experience']}")
                await interaction.followup.send(embed=embed, view=ConfirmePseudoRecrutementView(self.bot))
            else:
                embed = utils.create_embed(self.bot, f"**Erreur technique**", description=f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
                await interaction.followup.send(embed=embed)
            return

        api_data = {
            "username": response.json()["username"],
            "country": response.json()["servers"]["green"]["country"],
            "country_rank": response.json()["servers"]["green"]["country_rank"],
        }

        embed = utils.create_embed(self.bot, f"**Vérification**", description=f"Es ce bien toi ?")
        embed.add_field(name="Statut :", value=f"Joueur reconnu")
        embed.add_field(name="Pseudo IG :", value=f"{api_data['username']}")
        embed.add_field(name="Age :", value=f"{int(self.children[1].value) if self.children[1].value.isnumeric() and self.children[1].value != '-1' else -1}")
        embed.add_field(name="Experience :", value=f"{data['experience']}")
        embed.add_field(name="Pays :", value=f"{api_data['country']}")
        embed.add_field(name="Grade :", value=f"{api_data['country_rank']}")
        await interaction.followup.send(embed=embed, view=ConfirmePseudoRecrutementView(self.bot))


# Setup le formulaire diplomatie de la modale
class DiplomatieRegisterModal(Modal):
    def __init__(self, bot: GuyaBot) -> None:
        self.bot = bot
        super().__init__(title="Enregistrement")
        self.add_item(InputText(label="Pseudo en jeu", placeholder="Tominix356"))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = {
            "id_discord": interaction.user.id,
            "pseudo_ingame": self.children[0].value,
        }

        if len({data['pseudo_ingame']}) > 20:
            await interaction.followup.send("Ce pseudo ingame est trop long !")
            return

        # Vérifie si pas de contradiction avec la country db
        cur = self.bot.countrydb.cursor()

        cur.execute("SELECT count(*) FROM recrutement WHERE id_discord=?", [data["id_discord"]])
        find = cur.fetchone()
        if not find[0] == 0:
            await interaction.followup.send("Ce compte discord est déjà enregistré dans nos registre de pays ! Merci de prendre contacte avec un officier.")
            cur.close()
            return

        cur.execute("SELECT count(*) FROM recrutement WHERE pseudo_ingame=?", [data["pseudo_ingame"]])
        find = cur.fetchone()
        if not find[0] == 0:
            await interaction.followup.send("Ce pseudo IG est déjà enregistré dans nos registre de pays ! Merci de prendre contacte avec un officier.")
            cur.close()
            return

        cur.close()

        # Prend les infos de l'API
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {config["api_key"]}',
        }
        response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["pseudo_ingame"]}', headers=headers)

        if response.status_code != 200:
            embed = utils.create_embed(self.bot, f"**Erreur technique**", description=f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
            await interaction.followup.send(embed=embed)
            return

        if "error" in response.json():
            if response.json()["error"] == "unknown.user":
                embed = utils.create_embed(self.bot, title="**Problème !**",
                                           description=f"Après vérification, nous n'avons détecter aucun joueur portant le pseudo ``{data['pseudo_ingame']}`` sur le serveur Green. Es tu sûr de n'avoir fait aucune erreur en l'écrivant ? Les majuscules sont importantes ! Si tu ne t'es encore jamais connecter sur le Green, alors c'est normal, sinon merci d'entrée un autre pseudo.",
                                           color=Color.gold())
                embed.add_field(name="Statut :", value=f"Joueur non reconnu")
                embed.add_field(name="Pseudo IG :", value=f"{data['pseudo_ingame']}")
                await interaction.followup.send(embed=embed, view=ConfirmePseudoDiplomatieView(self.bot))
            else:
                embed = utils.create_embed(self.bot, f"**Erreur technique**", description=f"Nous avons rencontrer une erreur technique, nous somme navré du désagrément, tu veut bien re essayer s'il te plait ?")
                await interaction.followup.send(embed=embed)
            return

        api_data = {
            "username": response.json()["username"],
            "country": response.json()["servers"]["green"]["country"],
            "country_rank": response.json()["servers"]["green"]["country_rank"],
        }

        embed = utils.create_embed(self.bot, f"**Vérification**", description=f"Es ce bien toi ?")
        embed.add_field(name="Statut :", value=f"Joueur reconnu")
        embed.add_field(name="Pseudo IG :", value=f"{api_data['username']}")
        embed.add_field(name="Pays :", value=f"{api_data['country']}")
        embed.add_field(name="Grade :", value=f"{api_data['country_rank']}")
        await interaction.followup.send(embed=embed, view=ConfirmePseudoDiplomatieView(self.bot))
