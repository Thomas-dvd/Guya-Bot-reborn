import json
from datetime import date, timedelta, datetime

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

    @commands.slash_command(name="rank-up", description=".", default_permission=True)
    @commands.has_any_role(config["grades"]["membre"])
    async def rank_up(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True)):

        if user.id == ctx.user.id:
            await ctx.respond("Impossible de faire la confirmation de votre propre rank-up. Elle doit être effectué par quelqu'un plus haut gradé que vous après une présentation de votre nouveau grade en vocal.")
            return

        guild = self.bot.get_guild(config["guild_id"])
        membre_confirme = guild.get_channel(config["channels"]["vote_membres_confirmés"])
        officier = guild.get_channel(config["channels"]["vote_officiers"])
        membre_confirme_messages = await membre_confirme.history().flatten()
        officier_messages = await officier.history().flatten()

        cur = self.bot.countrydb.cursor()
        cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
        temp = cur.fetchone()

        for message in officier_messages:
            if temp[2] == message.embeds[0].to_dict()["fields"][1]["value"]:

                if message.embeds[0].to_dict()["fields"][2]["value"] == "Recrue Confirmé":
                    channel_gg = guild.get_channel(config["channels"]["rank_uwu"])
                    await user.add_roles(guild.get_role(config["roles"]["grades"]["recrue_confirme"]))
                    msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Recrue confirmé. 🎉")
                    emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
                    await msg.add_reaction(emoji)
                    cur.execute("UPDATE recrutement SET grade = 2 WHERE id_discord=?", [user.id])
                    try:
                        await user.edit(nick=f"Recrue+ | {temp[2]}")
                    except discord.errors.Forbidden:
                        pass
                    cur.execute("UPDATE recrutement SET referent=? WHERE id_discord=?", [ctx.user.id, user.id])
                    await message.delete()
                    await ctx.respond(f"Rank-up de {user.mention} validé")
                    return

                elif message.embeds[0].to_dict()["fields"][2]["value"] == "Officier":
                    channel_gg = guild.get_channel(config["channels"]["rank_uwu"])
                    await user.add_roles(guild.get_role(config["roles"]["grades"]["officier"]))
                    msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Officier. 🎉")
                    emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
                    await msg.add_reaction(emoji)
                    cur.execute("UPDATE recrutement SET grade = 4 WHERE id_discord=?", [user.id])
                    try:
                        await user.edit(nick=f"Offi | {temp[2]}")
                    except discord.errors.Forbidden:
                        pass
                    cur.execute("UPDATE recrutement SET referent=? WHERE id_discord=?", [ctx.user.id, user.id])
                    await message.delete()
                    await ctx.respond(f"Rank-up de {user.mention} validé")
                    return

        for message in membre_confirme_messages:
            if temp[2] == message.embeds[0].to_dict()["fields"][1]["value"]:

                if message.embeds[0].to_dict()["fields"][2]["value"] == "Membre":
                    channel_gg = guild.get_channel(config["channels"]["rank_uwu"])
                    await user.add_roles(guild.get_role(config["roles"]["grades"]["membre"]))
                    msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre. 🎉")
                    emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
                    await msg.add_reaction(emoji)
                    cur.execute("UPDATE recrutement SET grade = 3 WHERE id_discord=?", [user.id])
                    try:
                        await user.edit(nick=f"Membre | {temp[2]}")
                    except discord.errors.Forbidden:
                        pass
                    cur.execute("UPDATE recrutement SET referent=? WHERE id_discord=?", [ctx.user.id, user.id])
                    await message.delete()
                    await ctx.respond(f"Rank-up de {user.mention} validé")
                    return

                elif message.embeds[0].to_dict()["fields"][2]["value"] == "Membre Confirmé":
                    channel_gg = guild.get_channel(config["channels"]["rank_uwu"])
                    await user.add_roles(guild.get_role(config["roles"]["grades"]["membre_confirme"]))
                    msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre Confirmé. 🎉")
                    emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
                    await msg.add_reaction(emoji)
                    cur.execute("UPDATE recrutement SET grade = 4 WHERE id_discord=?", [user.id])
                    try:
                        await user.edit(nick=f"Membre+ | {temp[2]}")
                    except discord.errors.Forbidden:
                        pass
                    cur.execute("UPDATE recrutement SET referent=? WHERE id_discord=?", [ctx.user.id, user.id])
                    await message.delete()
                    await ctx.respond(f"Rank-up de {user.mention} validé")
                    return

        await ctx.respond(f"Impossible de trouver une procédure de rank-up terminé sur {user.mention}.")

    @commands.slash_command(name="unrank", description="Permet de rétrograders une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def unrank(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.")):

        guild = self.bot.get_guild(config["guild_id"])
        cur = self.bot.countrydb.cursor()
        temp_data = cur.execute("SELECT grade FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if temp_data is None:
            await ctx.respond("Utilisateur absent de la base de données")
            return

        data = temp_data[0]
        if not 2 < data < 7:
            await ctx.respond("Cette personne n'est pas unrankable")
            return

        if data == 2:
            await user.remove_roles(guild.get_role(config["roles"]["grades"]["recrue_confirme"]))
            await user.add_roles(guild.get_role(config["roles"]["grades"]["nouvelle_recrue"]))
            await ctx.respond(f"{user.mention} est passé recrue")
            cur.execute("UPDATE recrutement SET grade = 1 WHERE id_discord=?", [user.id])
            grade = "Recrue"
        elif data == 3:
            await user.remove_roles(guild.get_role(config["roles"]["grades"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Recrue+")
            cur.execute("UPDATE recrutement SET grade = 2 WHERE id_discord=?", [user.id])
            grade = "Recrue+"
        elif data == 4:
            await user.remove_roles(guild.get_role(config["roles"]["grades"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            cur.execute("UPDATE recrutement SET grade = 3 WHERE id_discord=?", [user.id])
            grade = "Membre"
        elif data == 5:
            if not ctx.user.get_role(config["roles"]["grades"]["Gouverneur"]) and not ctx.user.get_role(config["roles"]["grades"]["gouverneur_sec"]):
                await ctx.respond("Seul un Gouverneur ou le leader peu unrank un Officier membre confirmé .")
                return
            else:
                await user.remove_roles(guild.get_role(config["roles"]["grades"]["officier"]))
                await user.remove_roles(guild.get_role(config["roles"]["deco"]["hauts_grader"]))
                await ctx.respond(f"{user.mention} est passé Membre confirmé")
                cur.execute("UPDATE recrutement SET grade = 4 WHERE id_discord=?", [user.id])
                grade = "Membre+"
        elif data == 6:
            if not ctx.user.get_role(config["roles"]["second"]):
                await ctx.respond("Seul le leader pour unrank les officiers")
                return
            else:
                await user.remove_roles(guild.get_role(config["roles"]["gouverneur"]))
                await ctx.respond(f"{user.mention} est passé Officier")
                cur.execute("UPDATE recrutement SET grade = 5 WHERE id_discord=?", [user.id])
                grade = "Offi"
        else:
            return

        ig_name = cur.execute("SELECT pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        try:
            await user.edit(nick=f"{grade} | {ig_name[0]}")
        except discord.errors.Forbidden:
            pass
        self.bot.countrydb.commit()
        cur.close()
