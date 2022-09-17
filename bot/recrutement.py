import asyncio
import json
import random
from datetime import date
from sqlite3 import IntegrityError

import discord
from discord import Color, Option
from discord.ext import commands
from discord.ui import Modal, InputText, View, Button

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

    # Command /send-register
    @commands.slash_command(name="send-register", guild_ids=[config["secondary_guild_id"]], description="Commence ton recrutement !", default_permission=False)
    @commands.has_any_role(config["roles"]["officier_prim"], config["roles"]["officier_sec"])
    async def send_register(self, ctx: discord.ApplicationContext):
        await ctx.respond("En cas de difficulté avec la commands, tu peut utiliser le bouton si dessous :")
        await ctx.send(view=RegisterView(self.bot))

    # Command /register
    @commands.slash_command(guild_ids=[config["secondary_guild_id"]], description="Commence ton recrutement !")
    async def register(self, ctx: discord.ApplicationContext):
        cur = self.bot.db.cursor()
        if cur.execute("SELECT COUNT(*) FROM recrutement WHERE id_discord=?", [ctx.interaction.user.id]).fetchone()[0] != 0:
            await ctx.respond("Tu es déjà enregistrer")
            return
        cur.close()

        if not ctx.interaction.channel.name.startswith('ticket-'):
            await ctx.respond("Tu dois faire la commande dans ton ticket.")
            return

        await ctx.interaction.response.send_modal(RegisterModal(self.bot))

    # Command /bvn
    @commands.slash_command(description="Permet de finir le recrutement d'un candidat.", default_permission=False)
    @commands.has_any_role(config["roles"]["recruteur_prim"], config["roles"]["recruteur_sec"])
    async def bvn(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur."), regiment: Option(str, "Régiment du joueur.", choices=config["regiments"].keys()),
                  schematique: Option(str, "Schématique du joueur.", required=False)):
        cur = self.bot.db.cursor()
        data = cur.execute("SELECT grade, pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if data is None or data[0] != 0:
            await ctx.respond("L'utilisateur n'est pas candidat")
            return

        principal_guild = self.bot.get_guild(config["principal_guild_id"])
        secondary_guild = self.bot.get_guild(config["secondary_guild_id"])
        member_principal_guild = principal_guild.get_member(user.id)
        member_secondary_guild = secondary_guild.get_member(user.id)
        if member_principal_guild is None or member_secondary_guild is None:
            await ctx.respond("L'utilisateur a quitté un des discord")
            return

        cur.execute("UPDATE recrutement SET grade=1 WHERE id_discord=?", [user.id])
        cur.execute("UPDATE recrutement SET schematique=? WHERE id_discord=?", [schematique, user.id])

        self.bot.db.commit()
        cur.close()

        try:
            await member_principal_guild.edit(nick=f"Recrue | {data[1]}")
            await member_secondary_guild.edit(nick=f"Recrue | {data[1]}")
        except discord.errors.Forbidden:
            pass

        await member_secondary_guild.remove_roles(secondary_guild.get_role(config["roles"]["att_voc"]))
        for role in config["roles"]["deco"]:
            await member_principal_guild.add_roles(principal_guild.get_role(role))
        await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["nouvelle_recrue"]))
        await member_principal_guild.add_roles(principal_guild.get_role(config["regiments"][regiment]["role"]))

        channel_gg = principal_guild.get_channel(config["channels"]["rank_uwu"])
        msg = await channel_gg.send(f"Félicitaion à {user.mention} qui passe Nouvelle recrue. Bienvenue à lui dans le pays ! 🎉")
        emoji = self.bot.get_emoji(config["emoji_bellow_rank_message"])
        await msg.add_reaction(emoji)
        await ctx.respond(f"{user.name} est passé de Candidat à Nouvelle Recrue.")

        channel_regiment = principal_guild.get_channel(config["regiments"][regiment]["channel"])
        await channel_regiment.send(random.choice(config["welcome_message"]).format(name=user.mention, regi=regiment))

    # Command /cancel
    @commands.slash_command(description="Permet d'effacer un joueur de la base de données", default_permission=False)
    @commands.has_any_role(config["roles"]["officier_prim"], config["roles"]["officier_sec"])
    async def remove_user(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.")):
        cur = self.bot.db.cursor()

        try:
            cur.execute("DELETE FROM recrutement WHERE id_discord = ?", [str(user.id)])
            cur.execute("SELECT changes()")
            if cur.fetchone()[0] == 0:
                await ctx.respond("Utilisateur absent de la base de données")
            else:
                self.bot.db.commit()
                try:
                    await user.edit(nick=None)
                except discord.errors.Forbidden:
                    pass
                await ctx.respond(f"{user.mention} a correctement été supprimer de la base de données")
        except IntegrityError:
            await ctx.respond("Utilisateur absent de la base de données")
        finally:
            cur.close()

    # Message a la création d'un ticket
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if channel.name.startswith("ticket-") and channel.guild.id == config["secondary_guild_id"]:
            await asyncio.sleep(1)
            embed = utils.create_embed(self.bot, title="**Bonjour, bienvenue sur le discord de la Guyana !**", description=f"""Je suis le bot qui gère les recrutements et les relations internationals.
    Peu importe pour quoi tu vient, c'est par moi que tu passe. Je suis là pour que tout soit le plus simple possible ! Si à un moment, tu rencontre une quelconque difficulté, n"hésite pas à ping les <@&{config["roles"]["recruteur_sec"]}> (pour les recrutements) ou <@&{config["roles"]["officier_sec"]}> (pour les relations diplomatiques), ils sont la pour ça ! Clique sur le bouton ✅ si c'est bon pour toi.""",
                                       color=Color.gold())
            await channel.send(embed=embed, view=WelcomeConfirmeView(self.bot))

    # Détecte la réaction sous la vidéo
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.emoji.name == "💥" and message.content == "C'est bon tu as été enregistré, tu dois désormais regarder cette vidéo pour finir ton recrutement.":
            embed = utils.create_embed(
                self.bot,
                title="Félicitations 🎉 !",
                description=f"""Tu a finit ton enregistrement, on sais maintenant tout de toi 👀. Il vas maintenant falloir vocal avec un <@&{config['roles']['recruteur_sec']}> pour recevoir les accès sur le discord & In Game. 
                                👇 Écrit en dessous quand tu est disponible pour vocal avec les recruteurs.""",
                color=Color.gold())
            await message.channel.send(embed=embed)
            await message.channel.send(f"<@&{config['roles']['recruteur_sec']}>", delete_after=0)

    # Maintien des boutons
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(WelcomeConfirmeView(self.bot))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReglementConfirmeView(self.bot))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(DirectionSwitcherView(self.bot))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(RegisterView(self.bot))


class RegisterView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="/register", style=discord.ButtonStyle.grey, custom_id="register")
    async def button_callback(self, interaction):

        cur = self.bot.db.cursor()
        if cur.execute("SELECT COUNT(*) FROM recrutement WHERE id_discord=?", [interaction.user.id]).fetchone()[0] != 0:
            await interaction.channel.send("Tu es déjà enregistrer")
            return
        cur.close()

        if not interaction.channel.name.startswith('ticket-'):
            await interaction.channel.send("Tu dois faire la commande dans ton ticket.")
            return

        await interaction.response.send_modal(RegisterModal(self.bot))


# Setup le bouton "Confirmer"
class WelcomeConfirmeView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.green, emoji="✅", custom_id="button-confirm")
    async def button_callback(self, button, interaction):
        principal_guild = self.bot.get_guild(config["principal_guild_id"])
        member_principal_guild = principal_guild.get_member(interaction.user.id)

        if member_principal_guild is None:  # User pas dans la guild principal
            await interaction.response.send_message("Avant de continuer, tu dois rejoindre le discord principal de notre faction.\nhttps://discord.gg/7smZu3knk8", ephemeral=True)
            return

        button.disabled = True
        await interaction.response.edit_message(view=self)

        embed = utils.create_embed(self.bot, title="Règlement du discord.",
                                   description="En premier lieu, je t'invite a lire le règlement. Je pense qu'il n'y a pas raison de beaucoup écrire la dessus. Vous connaissez les normes \"classique\" :\n> ╰Toujours resté poli\n> ╰Pseudo et photo de profil correcte\n> ╰Pas de NSFW\n> ╰Respect des autres\n> ╰Pas de spam\n> ╰Pas de GhostPing. \n> ╰En cas de problème on vas voir les plus hauts grades\n \nUne autre règle importante a savoir :\n> ╰Vous ne vous prénomez pas \"moi\". En vocal, quand vous parlez et qu'on demande \"qui a parler/demandé de l'aide ?\", vous ne répondez pas \"moi\" à la question ! Moi n'est pas votre pseudo *et si \"moi\" est réellement votre pseudo, on avisera dans ce cas la*.\n \n**Si tout ceci est claire, je t'invite a cliqué sur le bouton si dessous**",
                                   color=Color.gold())
        await interaction.followup.send(embed=embed, view=ReglementConfirmeView(self.bot))


# Setup le bouton "Je valide le règlement"
class ReglementConfirmeView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Je valide le règlement", style=discord.ButtonStyle.green, emoji="✅", custom_id="button-reglement")
    async def button_callback(self, button, interaction):
        secondary_guild = self.bot.get_guild(config["secondary_guild_id"])
        principal_guild = self.bot.get_guild(config["principal_guild_id"])

        member_principal_guild = principal_guild.get_member(interaction.user.id)

        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.user.add_roles(secondary_guild.get_role(config["roles"]["verifie_sec"]))
        await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["verifie"]))
        await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["neutre"]))

        embed = utils.create_embed(self.bot, title="Maintenant, dit nous pourquoi tu viens :",
                                   description="- Si tu vient pour te faire recruté et nous rejoindre, click sur le bouton \"Recrutement\"\n- Si tu viens pour de la diplomatie (Joueur d'un autre pays, Modérateur, connaissance hors NG, etc), click sur le bouton \"Diplomatie\"",
                                   color=Color.gold())
        await interaction.followup.send(embed=embed, view=DirectionSwitcherView(self.bot))


# Setup le bouton "Recrutement" et "Diplomatie"
class DirectionSwitcherView(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Recrutement", style=discord.ButtonStyle.green, emoji="📑", custom_id="button-recrutement")
    async def recrutement_button_callback(self, button, interaction):
        button.disabled = True
        button2 = [x for x in self.children if x.custom_id == "button-diplomatie"][0]
        button2.disabled = True
        await interaction.response.edit_message(view=self)

        embed = utils.create_embed(self.bot, title="Avant de te présenter le pays, je vais te demander quelques informations.",
                                   description="Merci de faire la commande `/register` puis de compléter les champs.\nEn faisant cette commande, et en continuant ton recrutement, tu confirme :\n- Avoir plus de 10 ans\n- Avoir un micro (et pouvoir vocal sur discord)\n- Être intéressé pour jouer à NationsGlory sur le serveur Java GREEN.",
                                   color=Color.gold())
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Diplomatie", style=discord.ButtonStyle.blurple, emoji="🕊️", custom_id="button-diplomatie")
    async def diplomatie_button_callback(self, button, interaction):
        button.disabled = True
        button2 = [x for x in self.children if x.custom_id == "button-recrutement"][0]
        button2.disabled = True
        await interaction.response.edit_message(view=self)

        embed = utils.create_embed(self.bot, title="Demande de Grade :",
                                   description=f"**En tante que personne extérieur au pays, tu pouvez récupérer différents rôles qui te permettrons plusieurs niveau d'accès sur le discord.**\n \nGrades relations :\n> ╰Vérifié : Grade de base, il t'a été mis automatiquement.\n> ╰Neutre : Grade de base, il t'a été mis automatiquement.\n> ╰Allié : Si tu est en bon terme avec notre faction, tu peu récupérer ce grade pour obtenir les accès sur l'espace publique GDE.\n> ╰Colonie : Si tu a été coloniser par un de nos pays, tu peu demander ce grade, purement décoratif.\n> ╰Amis : Pour les amis __proches__ des gouverneurs, donne des accès sur le discord semblable a une recrue confirmé.\n> ╰Confiance : Pour les personne de toute confiance (anciens officiers, etc), donne des accès sur le discord semblable a un officier.\n \nGrades médailles :\n> ╰Stp drop un red (alias OP green) : Pour les Super-Modo et Administrateurs du Green.\n> ╰Modo : Pour les Modo du Green.\n> ╰Guide : Pour les Guides du Green.\n \nSi tu pense mérité un de ces grades, n'hésite pas a en faire la demande si dessous 👇.",
                                   color=Color.gold())
        await interaction.followup.send(embed=embed)


# Setup le formulaire de la modal
class RegisterModal(Modal):
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

        # TODO: Check mc pseudo

        if len({data['pseudo_ingame']}) > 20:
            await interaction.followup.send("Ce pseudo ingame est trop long !")
            return

        cur = self.bot.db.cursor()
        try:
            cur.execute(
                "INSERT INTO recrutement (id_discord, pseudo_ingame, annee_naissance, experience, date_recrutement) VALUES (:id_discord, :pseudo_ingame, :annee_naissance, :experience, :date_recrutement)",
                data)
            recrue_id = cur.lastrowid
        except IntegrityError:
            await interaction.followup.send("Ce pseudo ingame est déjà utilisé !")
            return

        self.bot.db.commit()
        cur.close()

        # Rename user + add role + rename channel
        member_principal_guild = self.bot.get_guild(config["principal_guild_id"]).get_member(interaction.user.id)
        try:
            await member_principal_guild.edit(nick=f"Candidat | {data['pseudo_ingame']}")
            await interaction.user.edit(nick=f"Candidat | {data['pseudo_ingame']}")
        except discord.errors.Forbidden:
            pass
        await interaction.channel.edit(name=data['pseudo_ingame'])
        await interaction.user.add_roles(interaction.guild.get_role(config["roles"]["att_voc"]))

        view = View()
        view.add_item(Button(label="Lien de la vidéo", url=config["video_url"]))
        embed = utils.create_embed(self.bot, title="Données :", color=Color.gold())
        embed.add_field(name="Pseudo en jeu", value=data["pseudo_ingame"], inline=True)
        embed.add_field(name="ID système", value=recrue_id, inline=True)
        embed.add_field(name="Âge", value=date.today().year - data["annee_naissance"] if data["annee_naissance"] != -1 else -1, inline=False)
        embed.add_field(name="Expérience", value=data["experience"], inline=False)
        await interaction.followup.send(embeds=[embed])
        await interaction.channel.send("C'est bon tu as été enregistré, tu dois désormais regarder cette vidéo pour finir ton recrutement.", view=view)
