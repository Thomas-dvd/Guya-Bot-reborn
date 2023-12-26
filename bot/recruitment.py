import json
import os
import random
from datetime import date

import discord
import requests
from discord import Color, Option, DMChannel
from discord.ext import commands

import utils
from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog recruitment')
    bot.add_cog(Recruitment(bot))


class Recruitment(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------
    #                                         Commands
    # ------------------------------------------------------------------------------------------

    # groupe create
    create = discord.SlashCommandGroup("create", "create related commands")

    # Command /create recrue
    @create.command(name="recrue", description="Enregistrer une nouvelle recrue.", default_permission=False)
    @commands.has_any_role(config["grades"]["recruteur"])
    async def create_recrue(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True), pseudo: Option(str, "pseudo IG.", required=True)):

        data = {
            "discord_id": user.id,
            "ingame_name": pseudo,
            "recruitment_date": date.today(),
            "grade": 0
        }

        await ctx.defer()

        cur = self.bot.players.cursor()
        temp = cur.execute("SELECT * FROM diplomacy WHERE discord_id=?", [data["discord_id"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données diplomatique.")
            cur.close()
            return
        temp = cur.execute("SELECT * FROM diplomacy WHERE ingame_name=?", [data["ingame_name"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données diplomatique.")
            cur.close()
            return
        temp = cur.execute("SELECT * FROM country WHERE discord_id=?", [data["discord_id"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données de pays.")
            cur.close()
            return
        temp = cur.execute("SELECT * FROM country WHERE ingame_name=?", [data["ingame_name"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données de pays.")
            cur.close()
            return

        cur.execute("INSERT INTO country (discord_id, ingame_name, recruitment_date, grade) VALUES (:discord_id, "
                    ":ingame_name, :recruitment_date, :grade)", data)
        self.bot.players.commit()
        cur.close()

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
        await ctx.respond(f"{user.name} est passé Nouvelle Recrue.")

    # Command /create diplomate
    @create.command(name="diplomate", description="Enregistrer un nouveau diplomate.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def create_diplomate(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True), pseudo: Option(str, "pseudo IG.", required=True), relation: Option(str, "Niveau de relation.", choices=["Neutre", "Allié", "Colonie", "Alliance", "Ami", "Confiance"], required=False, default="Neutre"), medal: Option(str, "Grades médailles.", choices=["Guide", "Modo", "OP (SuperModo/Admin)"], required=False, name="médailles")):

        data = {
            "discord_id": user.id,
            "ingame_name": pseudo,
        }

        await ctx.defer()

        cur = self.bot.players.cursor()
        temp = cur.execute("SELECT * FROM diplomacy WHERE discord_id=?", [data["discord_id"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données diplomatique.")
            cur.close()
            return
        temp = cur.execute("SELECT * FROM diplomacy WHERE ingame_name=?", [data["ingame_name"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données diplomatique.")
            cur.close()
            return
        temp = cur.execute("SELECT * FROM country WHERE discord_id=?", [data["discord_id"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données de pays.")
            cur.close()
            return
        temp = cur.execute("SELECT * FROM country WHERE ingame_name=?", [data["ingame_name"]]).fetchone()
        if temp is not None:
            await ctx.respond(f"{user.mention} est déjà dans la base de données de pays.")
            cur.close()
            return

        api_ok = 0
        text = ""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.environ.get("NATIONSGLORY_API_KEY")}',
        }
        response = requests.get(f'https://publicapi.nationsglory.fr/user/{data["ingame_name"]}',
                                headers=headers)
        print(response.json())
        if response.status_code != 200:
            await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-01*")
            return
        if "error" in response.json():
            if response.json()["error"] == "unknown.user":  # Joueur non détecter
                api_ok = 1
            else:
                await ctx.respond("Erreur de l'API NationsGlory. *code erreur: E-N-02*")
                return
        else:
            await user.add_roles(ctx.guild.get_role(config["grades"]["link"]))
            text += f"<@&{config['grades']['link']}>"

        cur = self.bot.players.cursor()
        cur.execute(
            "INSERT INTO diplomacy (discord_id, ingame_name) VALUES (:discord_id, :ingame_name)",
            data)
        self.bot.players.commit()
        cur.close()

        await user.remove_roles(ctx.guild.get_role((config["grades"]["frontiere"])))

        # Rename user + add role
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
            await ctx.respond(f"{user.mention} a bien été enregistré.")
        else:
            await ctx.respond(f"{user.mention} a bien été enregistré. **Impossible de trouver un joueur NG avec ce nom.** *code erreur: E-N-03*")

    # Command /create non-joueur
    @create.command(name="non-joueur", description="Enregistrer une personne ne jouant pas a NationsGlory.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def create_non_joueur(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True), relation: Option(str, "Niveau de relation.", choices=["Neutre", "Allié", "Ami", "Confiance"], required=False, default="Neutre")):

        await ctx.defer()

        await user.remove_roles(ctx.guild.get_role((config["grades"]["frontiere"])))

        text = ""

        # Grades
        if relation == "Neutre":
            await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
            text += f" <@&{config['grades']['neutre']}>"

        elif relation == "Allié":
            await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
            text += f" <@&{config['grades']['neutre']}>"
            await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
            text += f", <@&{config['grades']['allié']}>"

        elif relation == "Ami":
            await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
            text += f" <@&{config['grades']['neutre']}>"
            await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
            text += f", <@&{config['grades']['allié']}>"
            await user.add_roles(ctx.guild.get_role(config["grades"]["ami"]))
            text += f", <@&{config['grades']['ami']}>"

        elif relation == "Confiance":
            await user.add_roles(ctx.guild.get_role(config["grades"]["neutre"]))
            text += f" <@&{config['grades']['neutre']}>"
            await user.add_roles(ctx.guild.get_role(config["grades"]["allié"]))
            text += f", <@&{config['grades']['allié']}>"
            await user.add_roles(ctx.guild.get_role(config["grades"]["ami"]))
            text += f", <@&{config['grades']['ami']}>"
            await user.add_roles(ctx.guild.get_role(config["grades"]["confiance"]))
            text += f", <@&{config['grades']['confiance']}>"

        for role in config["grades"]["deco"]["global"]:
            await user.add_roles(ctx.guild.get_role(role))
            text += f", <@&{role}>"

        embed = utils.create_embed(self.bot, title="Rôles obtenus :", description=f"{text}", color=Color.gold())
        await ctx.channel.send(embed=embed)
        await ctx.respond(f"{user.mention} a bien été enregistré.")

    # Command /remove-user
    @commands.slash_command(name="remove-user", description="Permet d'effacer un joueur de la base de données.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def remove_user(self, ctx: discord.ApplicationContext, pseudo: Option(str, "Entre un pseudo IG.")):

        await ctx.defer()
        if utils.database(self, "country", "ingame_name", pseudo) is None:
            if utils.database(self, "diplomacy", "ingame_name", pseudo) is None:
                await ctx.respond("Utilisateur absent de la base de données.")
                return
            table = "diplomacy"
        else:
            table = "country"

        data = utils.database(self, table, "ingame_name", pseudo)

        user = ctx.guild.get_member(data["discord_id"])
        cur = self.bot.players.cursor()
        cur.execute(f"DELETE FROM {table} WHERE ingame_name = ?", [str(pseudo)])
        self.bot.players.commit()

        if user is not None:
            await utils.default_grades(self, ctx, user)

        await ctx.respond("Utilisateur supprimer de la base de données. Il dispose maintenant du statut __non-joueur__ avec le niveau d'accès __neutre__. Il est possible de lui en accordé davantage via la commande /create.")

    # ------------------------------------------------------------------------------------------
    #                               Éléments supplémentaires
    # ------------------------------------------------------------------------------------------

    # Détection arriver nouveau membre
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(config["guild_id"])
        channel = guild.get_channel(config["channels"]["hub_recrutement"])
        await channel.send(f"# Bienvenue sur le discord {member.mention} :wave:\nLe Guyana :flag_gy: est ravi de t'accueillir. Pour accéder au reste du discord, tu vas devoir vocal avec un responsable :\n\n> - Si tu viens pour rejoindre le pays, il faut que tu vocal avec un <@&{config['grades']['recruteur']}>.\n> - Si tu viens pour autre chose, il faut que tu vocal avec un <@&{config['grades']['officier']}>.\n\n:point_down: Précise ci-dessous pourquoi tu es là et quand es-tu disponible pour vocal. Si tu as le moindre problème, demande nous ! On est là pour ça.\nhttps://discord.gg/Gsvx5X75fd")
        await member.add_roles(guild.get_role(config["grades"]["frontiere"]))

    # Quand mp
    @commands.Cog.listener()
    async def on_message(self, msg):
        if isinstance(msg.channel, DMChannel) and msg.author.id != self.bot.user.id:
            await msg.channel.send("Voici notre discord : https://discord.gg/7smZu3knk8")
