import json
from datetime import date, timedelta

import discord
from discord import Option, Forbidden
from discord.ext import commands
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

    # Command /informations
    @commands.slash_command(description="Donne toute les informations d'une personne", default_permission=False)
    @commands.has_any_role(config["roles"]["gouverneur"], config["roles"]["gouverneur_sec"])
    async def informations(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True)):

        cur = self.bot.db.cursor()
        cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
        temp = cur.fetchone()
        cur.close()

        age = (date.today().year - temp[3]) if temp[3] != -1 else -1

        embed = utils.create_embed(self.bot, f"Informations de {user}")
        embed.add_field(name="ID :", value=f"{temp[0]}")
        embed.add_field(name="ID discord :", value=f"{temp[1]}")
        embed.add_field(name="Pseudo IG :", value=f"{temp[2]}")
        embed.add_field(name="Age :", value=f"{age}")
        embed.add_field(name="Experience :", value=f"{temp[4]}")
        embed.add_field(name="Grade :", value=f"{temp[5]}")
        embed.add_field(name="Pays :", value=f"{temp[6]}")
        embed.add_field(name="Date recrutement :", value=f"{temp[7]}")
        embed.add_field(name="Has done player info :", value=f"{temp[8]}")
        embed.add_field(name="Statut maison :", value=f"{temp[9]}")
        embed.add_field(name="Donations :", value=f"{temp[10]}")
        embed.add_field(name="Constructions :", value=f"{temp[11]}")
        embed.add_field(name="Double compte :", value=f"{temp[12]}")
        embed.add_field(name="Participation animation :", value=f"{temp[13]}")
        embed.add_field(name="Créer animation :", value=f"{temp[14]}")
        embed.add_field(name="Nombre recrutement :", value=f"{temp[15]}")
        embed.add_field(name="Fin d'absence :", value=f"{temp[16]}")
        embed.add_field(name="Dernière connexion :", value=f"{temp[17]}")
        embed.add_field(name="Ancienneté :", value=f"{temp[18]}")
        embed.add_field(name="Schématique :", value=f"{temp[19]}")
        embed.add_field(name="Peut quitter le pays :", value=f"{temp[20]}")

        await ctx.respond(embed=embed)

    # Command /edit
    @commands.slash_command(description="Donne toute les informations d'une personne", default_permission=False)
    @commands.has_any_role(config["roles"]["gouverneur"], config["roles"]["gouverneur_sec"])
    async def edit(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=True), donnees: Option(str, "Condition a valider.", choices=["ID", "ID discord", "Pseudo IG", "Age", "Experience", "Grade", "Pays", "Date de recrutement", "Has done player info", "Statut maison", "Donations", "Constructions", "Double compte", "Participation animation", "Créer animation", "Nombre recrutement", "Fin d'absence", "Dernière connexion", "Ancienneté", "Schématique", "Peut quitter le pays"]), valeur: Option(str, "Nouvelle valeur (None pour Null).", required=True)):

        if donnees in ["pseudo_ingame" or "experience" or "date_recrutement" or "absence_fin" or "peut_quitter_pays"]:
            valeur = int(valeur)
        if valeur in ["None", "none"]:
            valeur = None

        await ctx.respond(f"La donnée {donnees} du joueur {user.mention} a bien été définit sur {valeur}")
        if donnees == "Age":
            valeur = (date.today().year - valeur) if valeur != "-1" else -1
        cur = self.bot.db.cursor()
        if donnees == "ID":
            cur.execute(f"UPDATE recrutement SET id=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "ID discord":
            cur.execute(f"UPDATE recrutement SET id_discord=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Pseudo IG":
            cur.execute(f"UPDATE recrutement SET pseudo_ingame=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Age":
            cur.execute(f"UPDATE recrutement SET annee_naissance=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Experience":
            cur.execute(f"UPDATE recrutement SET experience=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Grade":
            cur.execute(f"UPDATE recrutement SET grade=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Pays":
            cur.execute(f"UPDATE recrutement SET pays=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Date de recrutement":
            cur.execute(f"UPDATE recrutement SET date_recrutement=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Has done player info":
            cur.execute(f"UPDATE recrutement SET has_done_player_info=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Statut maison":
            cur.execute(f"UPDATE recrutement SET statut_maison=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Donations":
            cur.execute(f"UPDATE recrutement SET donations=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Constructions":
            cur.execute(f"UPDATE recrutement SET constructions=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Double compte":
            cur.execute(f"UPDATE recrutement SET double_compte=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Participation animation":
            cur.execute(f"UPDATE recrutement SET participation_animation=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Créer animation":
            cur.execute(f"UPDATE recrutement SET creer__animation=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Nombre recrutement":
            cur.execute(f"UPDATE recrutement SET nb_recrutement=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Fin d'absence":
            cur.execute(f"UPDATE recrutement SET absence_fin=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Dernière connexion":
            cur.execute(f"UPDATE recrutement SET last_connection=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Ancienneté":
            cur.execute(f"UPDATE recrutement SET anciennete=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Schématique":
            cur.execute(f"UPDATE recrutement SET schematique=? WHERE id_discord=?", [valeur, user.id])
        if donnees == "Peut quitter le pays":
            cur.execute(f"UPDATE recrutement SET peut_quitter_pays=? WHERE id_discord=?", [valeur, user.id])
        self.bot.db.commit()
        cur.close()

    # Command /force-check
    @commands.slash_command(name="force-check", description="Actualise le statut d'une personne")
    async def force_check(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):
        if user is not None:
            cur = self.bot.db.cursor()
            cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
            temp = cur.fetchone()
            bdd_data = {
                "id": temp[0],
                "id_discord": user.id,
                "pseudo_ingame": temp[2],
                "grade": temp[5],
                "pays": temp[6],
                "date_recrutement": temp[7],
                "has_done_player_info": temp[8],
                "statut_maison": temp[9],
                "donations": temp[10],
                "constructions": temp[11],
                "double_compte": temp[12],
                "participation_animation": temp[13],
                "creer_animation": temp[14],
                "nb_recrutement": temp[15],
                "absence_fin": temp[16],
                "last_connection": temp[17],
                "anciennete": temp[18],
                "schematique": temp[19],
                "peut_quitter_pays": temp[20]
            }
            aaron_data = self.bot.aaron.get_user(bdd_data["pseudo_ingame"])
            cur.close()
            await self.force_check_user(bdd_data, aaron_data)
            await ctx.respond(f"ForceCheck sur le joueur {user.mention} lancé !")
        else:
            await ctx.respond(f"ForceCheck général lancé !")
            cur = self.bot.db.cursor()
            cur.execute("SELECT count(*) FROM recrutement")
            data_number = cur.fetchone()
            data_number = int(data_number[0])
            with tqdm(total=data_number, unit="member", ascii="⬡⬢", bar_format='{l_bar}{bar:25}{r_bar}{bar:-10b}', desc="Force check en cours ") as line1:
                message = await ctx.send(line1)
                for i in range(0, data_number, NOMBRE_MEMBRE_PAR_STEP):
                    cur.execute("SELECT * FROM recrutement ORDER BY id LIMIT " + str(NOMBRE_MEMBRE_PAR_STEP) + " OFFSET ?", [i])
                    count = 0
                    for temp in cur:
                        count += 1
                        if temp is not None:
                            bdd_data = {
                                "id": temp[0],
                                "id_discord": temp[1],
                                "pseudo_ingame": temp[2],
                                "grade": temp[5],
                                "pays": temp[6],
                                "date_recrutement": temp[7],
                                "has_done_player_info": temp[8],
                                "statut_maison": temp[9],
                                "donations": temp[10],
                                "constructions": temp[11],
                                "double_compte": temp[12],
                                "participation_animation": temp[13],
                                "creer_animation": temp[14],
                                "nb_recrutement": temp[15],
                                "absence_fin": temp[16],
                                "last_connection": temp[17],
                                "anciennete": temp[18],
                                "schematique": temp[19],
                                "peut_quitter_pays": temp[20]
                            }
                            aaron_data = self.bot.aaron.get_user(bdd_data["pseudo_ingame"])
                            await self.force_check_user(bdd_data, aaron_data)
                    line1.update(count)
                    await message.edit(content=line1)

            cur.close()
            await ctx.send("Force check général terminé")

    # TODO: Check journalier

    # ForceCheck (par personne)
    async def force_check_user(self, bdd_data, aaron_data):
        # print(bdd_data, aaron_data)
        cur = self.bot.db.cursor()
        principal_guild = self.bot.get_guild(config["principal_guild_id"])
        secondary_guild = self.bot.get_guild(config["secondary_guild_id"])
        member_principal_guild = principal_guild.get_member(bdd_data["id_discord"])
        member_secondary_guild = secondary_guild.get_member(bdd_data["id_discord"])
        bot_channel = principal_guild.get_channel(config["channels"]["bot_data_channel"])

        # vérifie si le joueur existe bien IG
        if not aaron_data["exist"]:
            await bot_channel.send(f"L'utilisateur enregistrer sous le nom de {bdd_data['pseudo_ingame']} n'existe pas (ID: {bdd_data['id']})")
            return

        # Actualisation pays
        if aaron_data["country"] != bdd_data["pays"]:
            cur.execute("UPDATE recrutement SET pays=? WHERE id_discord=?", [aaron_data["country"], bdd_data["id_discord"]])

        # Inactivité
        jours_deco = (date.today() - date.fromtimestamp(int(aaron_data["last_connection"]))).days
        cur.execute("UPDATE recrutement SET last_connection=? WHERE id_discord=?", [jours_deco, bdd_data["id_discord"]])
        if jours_deco == 7 and bdd_data["absence_fin"] is None:
            try:
                await member_principal_guild.send(
                    f"Salut {member_principal_guild.mention} 👋. Je t'envoie un message car cela fait 7 jours que tu ne t'es pas co sur NationsGlory, tu nous manques :( !\n\n**N'oublie pas que :**\n- Si tu ne peux plus te connecter car tu n'as pas le temps (ou l'envie), il n'y a pas de problème, prévient nous juste sur ton ticket qu'on sache que tu n'as pas arrêter le jeu\n- Si tu ne te co plus car tu ne sais pas quoi faire sur le jeu, tu peux demander aux officiers et recruteurs quels sont les différents projets du pays (Mon /player-info peu également t'être utile !)\n- Si tu ass décidé d'arrêter NationsGlory, il n'y a pas de problème, prévient nous juste qu'on sache qui est actif et qui ne l'est pas dans le pays ;) Et n'oublie pas : tu seras toujours le bienvenue.\n- Si tu t'es bien co ces derniers temps et que ce message est une erreur...il doit y avoir un bug dans mon code. Envoie un message sur ton ticket pour prévenir dû soucie")
                msg = await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} est absent depuis 7 jours. Un message lui a bien été envoyé 👍")
                await msg.add_reaction("✅")
            except Forbidden or AttributeError:
                pass
        if jours_deco == 14 and bdd_data["absence_fin"] is None:
            await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} est absent depuis 14 jours.")

        # fin absence
        if bdd_data["absence_fin"] is not None and date.today() >= date.fromisoformat(bdd_data["absence_fin"]):
            cur.execute("UPDATE recrutement SET absence_fin=? WHERE id_discord=?", [None, bdd_data["id_discord"]])

        # Ancienneté
        if date.today() - date.fromisoformat(bdd_data["date_recrutement"]) >= timedelta(days=7) and bdd_data["anciennete"] == 0:
            cur.execute("UPDATE recrutement SET anciennete=1 WHERE id_discord=?", [bdd_data["id_discord"]])
            try:
                await member_principal_guild.send(
                    f"Félicitation, cela fait maintenant 1 semaine que tu est dans le pays ! tu as automatiquement validé la condition \"ancienneté\" dans les conditions de ranks (plus d'info avec le /player-info)")
            except Forbidden or AttributeError:
                pass
        if date.today() - date.fromisoformat(bdd_data["date_recrutement"]) >= timedelta(days=31) and bdd_data["anciennete"] <= 1:
            cur.execute("UPDATE recrutement SET anciennete=2 WHERE id_discord=?", [bdd_data["id_discord"]])
            try:
                await member_principal_guild.send(
                    f"Félicitation, cela fait maintenant 1 mois que tu est dans le pays ! tu as automatiquement validé la condition \"ancienneté\" dans les conditions de ranks (plus d'info avec le /player-info)")
            except Forbidden or AttributeError:
                pass
        if date.today() - date.fromisoformat(bdd_data["date_recrutement"]) >= timedelta(days=90) and bdd_data["anciennete"] <= 2:
            cur.execute("UPDATE recrutement SET anciennete=3 WHERE id_discord=?", [bdd_data["id_discord"]])
            try:
                await member_principal_guild.send(
                    f"Félicitation, cela fait maintenant 3 mois que tu est dans le pays ! tu as automatiquement validé la condition \"ancienneté\" dans les conditions de ranks (plus d'info avec le /player-info)")
            except Forbidden or AttributeError:
                pass

        # Bon pays
        if not aaron_data["country"] in config["list_pays"] and bdd_data["peut_quitter_pays"] is None:
            await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} n'est plus dans l'un des pays GDE et ne dispose d'aucune autorisation a cette effet.")

        # Leave discord
        try:
            if not member_principal_guild.get_role(config["roles"]["verifie"]):
                await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} n'est plus vérifié sur le discord principal.")
        except AttributeError:
            await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} n'est plus sur le discord principal.")
        try:
            if not member_secondary_guild.get_role(config["roles"]["verifie_sec"]):
                await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} n'est plus vérifié sur le discord secondaire.")
        except AttributeError:
            await bot_channel.send(f"L'utilisateur {bdd_data['pseudo_ingame']} n'est plus sur le discord secondaire.")

        self.bot.db.commit()
        cur.close()
