import json

import discord
from discord import Option, Color
from discord.ext import commands
from discord.ui import View, Button

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
            msg = await channel_gg.send(f"Félicitation à {user.mention} qui passe Recrue confirmé. 🎉")
            grade = "Recrue+"
        elif data["grade"] == 1:
            await user.add_roles(guild.get_role(config["grades"]["membre"]))
            msg = await channel_gg.send(f"Félicitation à {user.mention} qui passe Membre. 🎉")
            grade = "Membre"
        elif data["grade"] == 2:
            await user.add_roles(guild.get_role(config["grades"]["membre_confirme"]))
            msg = await channel_gg.send(f"Félicitation à {user.mention} qui passe Membre confirmé. 🎉")
            grade = "Membre+"
        elif data["grade"] == 3:
            await user.add_roles(guild.get_role(config["grades"]["officier"]))
            await user.add_roles(guild.get_role(config["grades"]["deco"]["hauts_grader"]))
            msg = await channel_gg.send(f"Félicitation à {user.mention} qui passe Officier. 🎉")
            grade = "Offi."
        elif data["grade"] == 4:
            await user.add_roles(guild.get_role(config["grades"]["gouverneur"]))
            msg = await channel_gg.send(f"Félicitation à {user.mention} qui passe Gouverneur. 🎉")
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
    @commands.slash_command(name="player-info", description="Permet de rank-up une personne.")
    async def player_info(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):

        if user is None:
            user = ctx.user

        data = utils.database(self, "country", "discord_id", user.id)
        if data is None:
            await ctx.respond("Utilisateur absent de la base de données de pays.")
            return

        data = utils.database(self, "country", "discord_id", user.id)
        embed = utils.create_embed(self.bot, title=f"Informations de {user.name}:",
                                   description=f"Voici toute les informations relatives à {data['ingame_name']}.",
                                   color=Color.green())

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
        embed.add_field(name=f"Permissions:",
                        value=f"Sortie de territoire: {country_permission}\nAbsence: {absence_permission}")

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

        button_rank = Button(label="Rank", style=discord.ButtonStyle.secondary, emoji="👨")
        button_badges = Button(label="Badges", style=discord.ButtonStyle.secondary, emoji="🆙")

        async def button_rank_callback(interaction):
            temp = utils.database(self, "country", "ingame_name",
                                  interaction.message.embeds[0].to_dict()["fields"][0]["value"])
            player = self.bot.get_user(temp["discord_id"])
            await PlayerInfoButtons.rank_embed(self, player, interaction)

        async def button_badges_callback(interaction):
            temp = utils.database(self, "country", "ingame_name",
                                  interaction.message.embeds[0].to_dict()["fields"][0]["value"])
            player = self.bot.get_user(temp["discord_id"])
            await PlayerInfoButtons.badges_embed(self, player, interaction)

        button_rank.callback = button_rank_callback
        button_badges.callback = button_badges_callback

        view = View()
        view.add_item(button_rank)
        view.add_item(button_badges)
        await ctx.respond(embed=embed, view=view)

    # TODO: Command /elo stats
    # Command /elo stats
    @elo.command(name="stats", description="Affiche les classements et les statistiques.")
    async def stats(self, ctx: discord.ApplicationContext):
        await ctx.respond("Une très vieille légende racompte qu'en des temps anciens...un certain leader n'a pas eu le temps de finir sa mise a jour pour 16h30 et donc qu'il n'y a rien a afficher ici")

    # TODO: Command /elo informations
    # Command /elo informations
    @elo.command(name="informations", description="Donne les informations sur le système d'elo.")
    async def elo_informations(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            "Une très vieille légende racompte qu'en des temps anciens...un certain leader n'a pas eu le temps de finir sa mise a jour pour 16h30 et donc qu'il n'y a rien a afficher ici")

    # TODO: Command /elo management
    # Command /elo management
    @elo.command(name="management", description="Permet de rank-up une personne.", default_permission=False)
    @commands.has_any_role(config["grades"]["officier"])
    async def elo_management(self, ctx: discord.ApplicationContext,
                          user: Option(discord.User, "Entre un utilisateur.", required=False)):
        await ctx.respond(
            "Une très vieille légende racompte qu'en des temps anciens...un certain leader n'a pas eu le temps de finir sa mise a jour pour 16h30 et donc qu'il n'y a rien a afficher ici")


class PlayerInfoButtons(View):

    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    # ------------------------------------------------------------------------------------------
    #                                         Player-info buttons
    # ------------------------------------------------------------------------------------------

    async def player_embed(self, user, interaction):

        data = utils.database(self, "country", "discord_id", user.id)
        embed = utils.create_embed(self.bot, title=f"Informations de {user.name}:",
                                   description=f"Voici toute les informations relatives à {data['ingame_name']}.",
                                   color=Color.green())

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
        embed.add_field(name=f"Permissions:",
                        value=f"Sortie de territoire: {country_permission}\nAbsence: {absence_permission}")

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

        button_rank = Button(label="Rank", style=discord.ButtonStyle.secondary, emoji="👨")
        button_badges = Button(label="Badges", style=discord.ButtonStyle.secondary, emoji="🆙")

        async def button_rank_callback(back):
            await PlayerInfoButtons.rank_embed(self, back.user, back)

        async def button_badges_callback(back):
            await PlayerInfoButtons.badges_embed(self, back.user, back)

        button_rank.callback = button_rank_callback
        button_badges.callback = button_badges_callback

        view = View()
        view.add_item(button_rank)
        view.add_item(button_badges)
        await interaction.response.edit_message(embed=embed, view=view)

    async def rank_embed(self, user, interaction):
        data = utils.database(self, "country", "discord_id", user.id)
        embed = utils.create_embed(self.bot, title=f"Conditions de rank de {user.name}:",
                                   description=f"Voici toute les conditions à valider restante par {data['ingame_name']} pour rank-up.",
                                   color=Color.green())

        if data["grade"] == 0:
            if data["age_badge"] < 1:
                embed.add_field(name=f"Anciennté:", value=f"Tu doit avoir 5 jours d'anciennté dans le pays pour rank-up.")
            if data["speaker_badge"] < 1:
                embed.add_field(name=f"Discussion:", value=f"Tu doit être au niveau 3 d'XP DraftBot.")
        elif data["grade"] == 1:
            if data["age_badge"] < 2:
                embed.add_field(name=f"Anciennté:", value=f"Tu doit avoir 14 jours d'anciennté dans le pays pour rank-up.")
            if data["speaker_badge"] < 2:
                embed.add_field(name=f"Discussion:", value=f"Tu doit être au niveau 6 d'XP DraftBot.")
            if data["money_badge"] < 1:
                embed.add_field(name=f"Donation:", value=f"Tu doit mettre 1.000$ dans la banque du pays. Si tu l'a fait, MP un officier pour qu'il vérifie et te donne ton badge")
        elif data["grade"] == 2:
            if data["dc_badge"] < 1:
                embed.add_field(name=f"Doubles comptes:", value=f"Tu doit avoir mis un double compte dans le pays. Mp un officier pour plus d'informations")
            if data["age_badge"] < 3:
                embed.add_field(name=f"Anciennté:", value=f"Tu doit avoir 30 jours d'anciennté dans le pays pour rank-up.")
            if data["speaker_badge"] < 3:
                embed.add_field(name=f"Discussion:", value=f"Tu doit être au niveau 10 d'XP DraftBot.")
            if data["money_badge"] < 3:
                embed.add_field(name=f"Donation:", value=f"Tu doit mettre 10.000$ dans la banque du pays. Si tu l'a fait, MP un officier pour qu'il vérifie et te donne ton badge")
        elif data["grade"] == 3:
            if data["age_badge"] < 4:
                embed.add_field(name=f"Anciennté:", value=f"Tu doit avoir 90 jours d'anciennté dans le pays pour rank-up.")
            if data["speaker_badge"] < 4:
                embed.add_field(name=f"Discussion:", value=f"Tu doit être au niveau 15 d'XP DraftBot.")
            if data["money_badge"] < 4:
                embed.add_field(name=f"Donation:", value=f"Tu doit mettre 25.000$ dans la banque du pays. Si tu l'a fait, MP un officier pour qu'il vérifie et te donne ton badge")
        else:
            embed.add_field(name=f"C'est non", value=f"C'est hors de question !")

        button_player = Button(label="Player", style=discord.ButtonStyle.secondary, emoji="👨")
        button_badges = Button(label="Badges", style=discord.ButtonStyle.secondary, emoji="🆙")

        async def button_player_callback(back):
            await PlayerInfoButtons.player_embed(self, back.user, back)

        async def button_badges_callback(back):
            await PlayerInfoButtons.badges_embed(self, back.user, back)

        button_player.callback = button_player_callback
        button_badges.callback = button_badges_callback

        view = View()
        view.add_item(button_player)
        view.add_item(button_badges)
        await interaction.response.edit_message(embed=embed, view=view)

    async def badges_embed(self, user, interaction):
        data = utils.database(self, "country", "discord_id", user.id)
        embed = utils.create_embed(self.bot, title=f"Listes de tout les badges",
                                   description=f"Voici la liste de tout les badges disponibles.",
                                   color=Color.green())

        embed.add_field(name=f"Une drôle d'histoire", value=f"Une très vieille légende racompte qu'en des temps anciens...un certain leader n'a pas eu le temps de finir sa mise a jour pour 16h30 et donc qu'il n'y a rien a afficher ici")
        # TODO: Affichage

        button_player = Button(label="Player", style=discord.ButtonStyle.secondary, emoji="👨")
        button_rank = Button(label="Badges", style=discord.ButtonStyle.secondary, emoji="🆙")

        async def button_player_callback(back):
            await PlayerInfoButtons.player_embed(self, back.user, back)

        async def button_rank_callback(back):
            await PlayerInfoButtons.rank_embed(self, back.user, back)

        button_player.callback = button_player_callback
        button_rank.callback = button_rank_callback

        view = View()
        view.add_item(button_player)
        view.add_item(button_rank)
        await interaction.response.edit_message(embed=embed, view=view)

