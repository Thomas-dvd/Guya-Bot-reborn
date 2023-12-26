import json

import discord
from discord import Option
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

    # groupe progressment
    progressment = discord.SlashCommandGroup("progressment", "progressment related commands")

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
    pass

    # Command /elo stats
    pass

    # Command /elo informations
    pass

    # Command /progressment badges
    pass

    # Command /progressment elo
    pass
