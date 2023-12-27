import json

import discord
from discord import Option, Color
from discord.ext import commands

import utils
from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog progressment')
    bot.add_cog(Progressment(bot))


class Progressment(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------
    #                                         Commands
    # ------------------------------------------------------------------------------------------

    # groupe elo
    elo = discord.SlashCommandGroup("elo", "elo related commands")

    # Command /rank
    @commands.slash_command(name="rank", description="Permet de rank-up une personne.", default_permission=True)
    @commands.has_any_role(config["grades"]["officier"])
    async def rank(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True)):

        guild = self.bot.get_guild(config["guild_id"])

        data = utils.database(self, "country", "discord_id", user.id)

        if data["grade"] >= 3:
            data_admin = utils.database(self, "country", "discord_id", ctx.user.id)
            if data["grade"] + 1 >= data_admin["grade"]:
                await ctx.respond(f"Impossible de rank-up {user.mention} vers un grade supérieur où égal au tien.")
                return

        cur = self.bot.players.cursor()
        cur.execute("UPDATE country SET grade = ? WHERE discord_id=?", [data["grade"]+1, user.id])
        self.bot.players.commit()
        cur.close()

        channel_gg = guild.get_channel(config["channels"]["rank_uwu"])

        if data["grade"] == 0:
            await user.add_roles(guild.get_role(config["grades"]["recrue_confirme"]))
            msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Recrue confirmé. 🎉")
            grade = "Recrue+"
        elif data["grade"] == 1:
            await user.add_roles(guild.get_role(config["grades"]["membre"]))
            msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre. 🎉")
            grade = "Membre"
        elif data["grade"] == 2:
            await user.add_roles(guild.get_role(config["grades"]["membre_confirme"]))
            msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre confirmé. 🎉")
            grade = "Membre+"
        elif data["grade"] == 3:
            await user.add_roles(guild.get_role(config["grades"]["officier"]))
            msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Officier. 🎉")
            grade = "Offi."
        elif data["grade"] == 4:
            await user.add_roles(guild.get_role(config["grades"]["gouverneur"]))
            msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Gouverneur. 🎉")
            grade = "Gouv."
        else:
            await ctx.respond(f"Impossible de rank-up {user.mention}. *code erreur: E-B-01*")
            return

        emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
        await msg.add_reaction(emoji)
        if len(f"{grade} | {data['ingame_name']}") <= 32:
            try:
                await user.edit(nick=f"{grade} | {data['ingame_name']}")
            except discord.errors.Forbidden:
                pass
        else:
            try:
                await user.edit(nick=f"{data['ingame_name']}")
            except discord.errors.Forbidden:
                pass
        await ctx.respond(f"Rank-up de {user.mention} effectué avec succès.")

    # Command /unrank
    @commands.slash_command(name="unrank", description="Permet de rétrograders une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def unrank(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.")):

        guild = self.bot.get_guild(config["guild_id"])

        data = utils.database(self, "country", "discord_id", user.id)

        if data["grade"] >= 4:
            data_admin = utils.database(self, "country", "discord_id", ctx.user.id)
            if data["grade"] >= data_admin["grade"]:
                await ctx.respond(
                    f"Impossible de unrank {user.mention}. Celui ci a un grade supérieur où égal au tien.")
                return

        cur = self.bot.players.cursor()
        cur.execute("UPDATE country SET grade = ? WHERE discord_id=?", [data["grade"] - 1, user.id])
        self.bot.players.commit()
        cur.close()

        if data["grade"] == 1:
            await user.remove_roles(guild.get_role(config["grades"]["recrue_confirme"]))
            grade = "Recrue"
        elif data["grade"] == 2:
            await user.remove_roles(guild.get_role(config["grades"]["membre"]))
            grade = "Recrue+"
        elif data["grade"] == 3:
            await user.remove_roles(guild.get_role(config["grades"]["membre_confirme"]))
            grade = "Membre"
        elif data["grade"] == 4:
            await user.remove_roles(guild.get_role(config["grades"]["officier"]))
            grade = "Membre+"
        elif data["grade"] == 5:
            await user.remove_roles(guild.get_role(config["grades"]["gouverneur"]))
            grade = "Offi."
        else:
            await ctx.respond(f"Impossible de unrank {user.mention}. *code erreur: E-B-02*")
            return

        if len(f"{grade} | {data['ingame_name']}") <= 32:
            try:
                await user.edit(nick=f"{grade} | {data['ingame_name']}")
            except discord.errors.Forbidden:
                pass
        else:
            try:
                await user.edit(nick=f"{data['ingame_name']}")
            except discord.errors.Forbidden:
                pass
        await ctx.respond(f"Unrank de {user.mention} effectué avec succès.")

    # Command /player-info
    @commands.slash_command(name="player-info", description="Permet de rank-up une personne.", default_permission=True)
    @commands.has_any_role(config["grades"]["officier"])
    async def player_info(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):

        if user is None:
            user = ctx.user

        data = utils.database(self, "country", "discord_id", user.id)
        if data is None:
            await ctx.respond("Utilisateur absent de la base de données de pays.")
            return
        embed = utils.create_embed(self.bot, title=f"Informations de {user.name}:", description=f"Voici toute les informations relatives à {user.name}.", color=Color.green())

        embed.add_field(name=f"Pseudo InGame:", value=f"{data['ingame_name']}")
        embed.add_field(name=f"Date de recrutement:", value=f"{data['recruitment_date']}")
        embed.add_field(name=f"ID système", value=f"{data['id']}")
        if data['country'] == "bypass":
            country_permission = f"<{config['emoji_yes']}>"
        else:
            country_permission = f"<{config['emoji_no']}>"
        if data['absence'] is not None:
            absence_permission = f"<{config['emoji_yes']}>"
        else:
            absence_permission = f"<{config['emoji_no']}>"
        embed.add_field(name=f"Permissions:", value=f"Sortie de territoire: {country_permission}\nAbsence: {absence_permission}")

        badges = utils.database_parametres(question="BadgesListe")
        text = ""
        for badge in badges:
            if data[badge[0]] != 0:
                if data[badge[0]] != badge[2]:
                    text += f"<{config[f'emoji_level_{data[badge[0]]}']}> {badge[1]} niveau {data[badge[0]]}\n"
                else:
                    text += f"<{config[f'emoji_level_5']}> {badge[1]} niveau max\n"
        if text == "":
            text = "*Il n'y a pas grand chose a afficher ici...*"
        embed.add_field(name=f"Badges:", value=f"{text}", inline=False)
        await ctx.respond(embed=embed)





    # Command /badges
    pass

    # Command /elo stats
    pass

    # Command /elo informations
    pass

    # Command /elo management
    pass

    # ------------------------------------------------------------------------------------------
    #                                         Player-info buttons
    # ------------------------------------------------------------------------------------------

# Rajouter un bouton information badges + rank-up
