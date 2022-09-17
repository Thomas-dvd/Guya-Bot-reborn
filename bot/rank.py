import json
from datetime import date, timedelta

import discord
from discord import Option
from discord.ext import commands

import utils
from main import GuyaBot

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog rank')
    bot.add_cog(Rank(bot))


class Rank(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # Command /player-info
    @commands.slash_command(name="player-info", description="Donne toute les informations publique sur une personne")
    async def player_info(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):
        if user is None:
            user = ctx.user

        cur = self.bot.db.cursor()
        cur.execute("UPDATE recrutement SET has_done_player_info = 1 WHERE id_discord=?", [ctx.user.id])
        self.bot.db.commit()
        cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
        temp = cur.fetchone()
        if temp is None:
            await ctx.respond("Utilisateur absent de la base de données")
            return
        data = {
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
            "last_connection": temp[17],
            "anciennete": temp[18],
            "schematique": temp[19]
        }

        embed = utils.create_embed(self.bot, f"Stats de {user}")
        embed.add_field(name="Nom en jeu :", value=f"{data['pseudo_ingame']}")
        embed.add_field(name="ID système :", value=f"{data['id']}")
        embed.add_field(name="Pays :", value=f"{data['pays']}")
        embed.add_field(name="Dernière connexion :", value=f"{data['last_connection']}")
        embed.add_field(name="Date de recrutement :", value=f"{data['date_recrutement']}")
        embed.add_field(name="Schematic :",
                        value=f"[{data['schematique']}]({config['schematics'][data['schematique']] if data['schematique'] in config['schematics'] else 'https://www.youtube.com/c/Tominix356?sub_confirmation=1'})")
        text = ""

        if data["grade"] == 0:  # Candidat
            embed.add_field(name="Grade :", value="Candidat")

            text += "Tu doit finir ton recrutement"

        elif data["grade"] == 1:  # Nouvelle recrue
            embed.add_field(name="Grade :", value="Nouvelle recrue")

            pays = data["pays"] in config["list_pays"]
            maison = data["statut_maison"] >= 1
            time = data["anciennete"] >= 1
            do_player_info = data["has_done_player_info"] == 1

            if maison and time and do_player_info:
                text += f"**Condition intégration :** ✅\n"
            else:
                text += f"**Condition intégration :** ❌\n"
            if pays:
                if maison:
                    text += "__Maison :__ ✅\n"
                else:
                    text += f"__Maison :__ ❌ Tu doit encore finir ta maison et la faire validé, pour plus d'information, consulte le #build. [?]({config['links_doc']['maison_1']})\n"
            else:
                text += f"__Pays :__ ❌ Tu doit encore rejoindre le pays. [?]({config['links_doc']['pays']})\n"
            if time:
                text += "__Ancienneté :__ ✅\n"
            else:
                text += "__Ancienneté :__ ❌ Tu doit avoir une semaine d'ancienneté.\n"
            if do_player_info:
                text += "__Utilisation du bot :__ ✅\n"
            else:
                text += f"__Utilisation du bot :__ ❌ Tu doit t'être renseigné au moins une fois sur tes conditions de rank. [?]({config['links_doc']['utilisation_bot']})\n"

            grade_farm = user.get_role(config["roles"]["farmer"]) is not None
            donation = data["donations"] >= 5000

            if grade_farm and donation:
                text += f"\n**Pôle économique :** ✅\n"
            else:
                text += f"\n**Pôle économique :** ❌\n"
            if grade_farm:
                if donation:
                    text += "__Contribution économique :__ ✅\n"
                else:
                    text += f"__Contribution économique :__ ❌ Tu doit encore farmer {5000 - data['donations']}$. [?]({config['links_doc']['donation_1']})\n"
            else:
                text += "__Farming :__ ❌ Pour rejoindre le pôle économique, tu doit récupérer le grade @Farmer dans #pole.\n"

            grade_const = user.get_role(config["roles"]["constructeur"]) is not None
            projet = data["constructions"] >= 1

            if grade_const and projet:
                text += f"\n**Pôle build :** ✅\n"
            else:
                text += f"\n**Pôle build :** ❌\n"
            if grade_const:
                if projet:
                    text += "__Contribution de build :__ ✅\n"
                else:
                    text += f"__Contribution de build :__ ❌ Tu doit participer a encore au moins {1 - data['constructions']} chantier de build. [?]({config['links_doc']['construction_1']})\n"
            else:
                text += "__Constructeur :__ ❌ Pour rejoindre le pôle build, tu doit récupérer le grade @Constructeur dans #pole.\n"

            text += f"\n**Récompense de rank :** Full prototype sombre"

        elif data["grade"] == 2:  # Recrue confirmé
            embed.add_field(name="Grade :", value="Recrue confirmé")

            maison = data["statut_maison"] >= 2
            double_compte = data["double_compte"] >= 1
            time = data["anciennete"] >= 2

            if maison and time and double_compte:
                text += f"**Condition intégration :** ✅\n"
            else:
                text += f"**Condition intégration :** ❌\n"
            if maison:
                text += "__Maison :__ ✅\n"
            else:
                text += f"__Maison :__ ❌ Tu doit encore finir ta maison de membre. [?]({config['links_doc']['maison_2']})\n"
            if double_compte:
                text += "__Double compte :__ ✅\n"
            else:
                text += f"__Double compte :__ ❌ Tu doit mettre un DC dans le trinité-et-tobago, contacte les officiers pour te faire invité. [?]({config['links_doc']['double_compte']})\n"
            if time:
                text += "__Ancienneté :__ ✅\n"
            else:
                text += "__Ancienneté :__ ❌ Tu doit avoir un mois d'ancienneté.\n"

            donation = data["donations"] >= 20000

            if donation:
                text += f"\n**Pôle économique :** ✅\n"
            else:
                text += f"\n**Pôle économique :** ❌\n"
            if donation:
                text += "__Contribution économique :__ ✅\n"
            else:
                text += f"__Contribution économique :__ ❌ Tu doit encore farmer {20000 - data['donations']}$\n"

            projet = data["constructions"] >= 4

            if projet:
                text += f"\n**Pôle build :** ✅\n"
            else:
                text += f"\n**Pôle build :** ❌\n"
            if projet:
                text += "__Contribution de build :__ ✅\n"
            else:
                text += f"__Contribution de build :__ ❌ Tu doit participer a encore au moins {4 - data['constructions']} chantier de build\n"

            animation = data["participation_animation"] == 1

            if animation:
                text += f"\n**Pôle animation :** ✅\n"
            else:
                text += f"\n**Pôle animation :** ❌\n"
            if animation:
                text += "__Participation a une animation :__ ✅\n"
            else:
                text += f"__Participation a une animation :__ ❌ Tu doit participer a une animation (demander aux animateur de noté ta participation)\n"

            text += f"\n**Récompense de rank :** Jump boots (immunise contre les dégâts de chute et permet des sauts de 5 blocs)"

        elif data["grade"] == 3:  # Membre
            embed.add_field(name="Grade :", value="Membre")

            time = data["anciennete"] == 3

            if time:
                text += f"**Condition intégration :** ✅\n"
            else:
                text += f"**Condition intégration :** ❌\n"
            if time:
                text += "__Ancienneté :__ ✅\n\n"
            else:
                text += "__Ancienneté :__ ❌ Tu doit avoir 3 mois d'ancienneté.\n\n"

            donation = data["donations"] >= 70000
            projet = data["constructions"] >= 9
            grade_archi = user.get_role(config["roles"]["architecte"]) is not None
            grade_builder = user.get_role(config["roles"]["builder"]) is not None
            grade_archi_builder = grade_builder is True or grade_archi is True
            grade_anim = user.get_role(config["roles"]["animateur"]) is not None
            animation = data["creer_animation"] >= 3
            grade_recru = user.get_role(config["roles"]["recruteur_prim"]) is not None
            nb_recrutement = data["nb_recrutement"] >= 10

            optionnel = 0
            if grade_archi and projet:
                optionnel += 1
            if grade_recru and nb_recrutement:
                optionnel += 1
            if grade_anim and animation:
                optionnel += 1
            if donation:
                optionnel += 1

            if optionnel >= 3:
                text += f"**Condition optionnelle :** {optionnel}/3 ✅\n"
            else:
                text += f"**Condition optionnelle :** {optionnel}/3 ❌\n"

            if donation:
                text += f"|\n| **Pôle économique :** ✅\n"
                text += "| __Contribution :__ ✅\n"
            else:
                text += f"|\n| **Pôle économique :** ❌\n"
                text += f"| __Contribution :__ ❌ Tu doit encore farmer {70000 - data['donations']}$\n"

            if projet and grade_archi_builder:
                text += f"|\n| **Pôle build :** ✅\n"
            else:
                text += f"|\n| **Pôle build :** ❌\n"
            if projet:
                text += "| __Contribution de build :__ ✅\n"
            else:
                text += f"| __Contribution de build :__ ❌ Tu doit participer a encore au moins {9 - data['constructions']} chantier de build\n"
            if grade_archi_builder:
                text += "| __Gestion de build :__ ✅\n"
            else:
                text += f"| __Gestion de build :__ ❌ Tu doit candidaté pour devenir @Architecte ou @Builder\n"

            if grade_anim and animation:
                text += f"|\n| **Pôle animation :** ✅\n"
            else:
                text += f"|\n| **Pôle animation :** ❌\n"
            if grade_anim:
                if animation:
                    text += "| __Animation :__ ✅\n"
                else:
                    text += f"| __Animation :__ ❌ Tu doit encore organiser au moins {9 - data['creer_animation']} animations\n"
            else:
                text += f"| __Animation :__ ❌ Tu doit candidaté pour devenir @Animateur\n"

            if grade_recru and nb_recrutement:
                text += f"|\n| **Pôle recrutement :** ✅\n"
            else:
                text += f"|\n| **Pôle recrutement :** ❌\n"
            if grade_recru:
                if nb_recrutement:
                    text += "| __Recrutement :__ ✅\n"
                else:
                    text += f"| __Recrutement :__ ❌ Tu doit encore recruter au moins {10 - data['nb_recrutement']} joueurs\n"
            else:
                text += f"| __Recrutement :__ ❌ Tu doit candidaté pour devenir @Recruteur\n"

            text += "\n**Récompense de rank :** Speed Leg (+40% de vitesse de déplacement)"

        elif data["grade"] == 4:  # Membre confirmé
            embed.add_field(name="Grade :", value="Membre confirmé")
            text += "Pour continuer à progresser dans le pays, il n'y a plus de conditions de rank précises. Le rank officier ou gouverneur, est rare, il faut valider de nombreuses conditions. Le meilleur moyen de passé officier, c'es-t-en continuant, tous les jours à t'investir pour le pays, à être présent et à l'écoute des autres, et ainsi permettre à notre nation d'avancer"

        elif data["grade"] == 5:  # Officier
            embed.add_field(name="Grade :", value="Officier")
            text += "Pour continuer à progresser dans le pays, il n'y a plus de conditions de rank précises. Le rank officier ou gouverneur, est rare, il faut valider de nombreuses critères. Le meilleur moyen de passé officier, c'es-t-en continuant, tous les jours à t'investir pour le pays, à être présent et à l'écoute des autres, et ainsi permettre à notre nation d'avancer"

        elif data["grade"] == 6:  # Gouverneur
            embed.add_field(name="Grade :", value="Gouverneur")
            text += "Le grade de leader n'est pas négotiable"

        elif data["grade"] == 7:  # Leader
            embed.add_field(name="Grade :", value="Leader")
            text += "Oui alors... Que dire ici... En soit on dit que la vie c'est de ne jamais arrêter d'apprendre, donc on peu toujours s'élever nan ? Bon ca répond pas la question... Que dire ici ? On a qu'a dire que c'est un easter egg. Ouais c'est une bonne idée, donc \"Ouais GG t'a trouver un easter egg !\" Voila, c'est tout, donc retourne bossé maintenant au lieu de lire ce genre de message"

        embed.add_field(name="}============{ Condition de rank }============{", value=f"{text}", inline=False)

        await ctx.respond(embed=embed)

    # Command /rank
    @commands.slash_command(description="Permet de rank une personne.", default_permission=False)
    @commands.has_any_role(config["roles"]["recruteur_prim"], config["roles"]["recruteur_sec"])
    async def rank(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.")):

        principal_guild = self.bot.get_guild(config["principal_guild_id"])
        secondary_guild = self.bot.get_guild(config["secondary_guild_id"])
        member_principal_guild = principal_guild.get_member(user.id)
        member_secondary_guild = secondary_guild.get_member(user.id)
        channel_gg = principal_guild.get_channel(config["channels"]["rank_uwu"])
        cur = self.bot.db.cursor()
        temp_data = cur.execute("SELECT grade FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if temp_data is None:
            await ctx.respond("Utilisateur absent de la base de données")
            return

        data = temp_data[0]
        if not 0 < data < 6:
            if data == 0:
                await ctx.respond("Le passage des candidats nouvelle recrues s'effectue via la commande /bvn")
            else:
                await ctx.respond("Cette personne n'est pas rankable")
            return

        if data == 1:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["recrue_confirme"]))
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["nouvelle_recrue"]))
            await ctx.respond(f"{user.mention} est passé recrue confirmé")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Recrue confirmé. 🎉")
            grade = "Recrue+"
        elif data == 2:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre. 🎉")
            grade = "Membre"
        elif data == 3:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre confirmé")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre confirmé. 🎉")
            grade = "Membre+"
        elif data == 4:
            if not ctx.user.get_role(config["roles"]["gouverneur"]) or not ctx.user.get_role(config["roles"]["gouverneur_sec"]):
                await ctx.respond("Seul un gouverneur ou le leader peu rank un membre confirmé officier.")
                return
            else:
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["officier_prim"]))
                await member_secondary_guild.add_roles(secondary_guild.get_role(config["roles"]["officier_sec"]))
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["deco_hauts_grade"]))
                await ctx.respond(f"{user.mention} est passé officier")
                await channel_gg.send(f"Félicitaion à {user.mention} qui passe Officier. 🎉")
                grade = "Officier"
        elif data == 5:
            if not ctx.user.get_role(config["roles"]["second"]):
                await ctx.respond("Seul le leader pour ajouté de nouveau gouverneurs <3")
                return
            else:
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["gouverneur"]))
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["deco_dieu"]))
                await ctx.respond(f"{user.mention} est passé gouverneur")
                await channel_gg.send(f"Félicitaion à {user.mention} qui passe Gouverneur. 🎉")
                grade = "Gouverneur"
        else:
            return

        ig_name = cur.execute("SELECT pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        try:
            await member_principal_guild.edit(nick=f"{grade} | {ig_name[0]}")
            await member_secondary_guild.edit(nick=f"{grade} | {ig_name[0]}")
        except discord.errors.Forbidden:
            pass
        cur.execute("UPDATE recrutement SET grade = grade+1 WHERE id_discord=?", [user.id])
        self.bot.db.commit()
        cur.close()

    # Command /unrank
    @commands.slash_command(description="Permet de unrank une personne.", default_permission=False)
    @commands.has_any_role(config["roles"]["officier_prim"], config["roles"]["officier_sec"])
    async def unrank(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.")):

        principal_guild = self.bot.get_guild(config["principal_guild_id"])
        secondary_guild = self.bot.get_guild(config["secondary_guild_id"])
        member_principal_guild = principal_guild.get_member(user.id)
        member_secondary_guild = secondary_guild.get_member(user.id)
        cur = self.bot.db.cursor()
        temp_data = cur.execute("SELECT grade FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        if temp_data is None:
            await ctx.respond("Utilisateur absent de la base de données")
            return

        data = temp_data[0]
        if not 1 < data < 7:
            if data == 0:
                await ctx.respond("Le passage des candidats nouvelle recrues s'effectue via la commande /bvn")
            else:
                await ctx.respond("Cette personne n'est pas unrankable")
            return

        if data == 2:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["recrue_confirme"]))
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["nouvelle_recrue"]))
            await ctx.respond(f"{user.mention} est passé Nouvelle recrue")
            grade = "Recrue"
        elif data == 3:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Recrue confirmé")
            grade = "Recrue+"
        elif data == 4:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            grade = "Membre"
        elif data == 5:
            if not member_principal_guild.get_role(config["roles"]["gouverneur"]):
                await ctx.respond("Seul un gouverneur ou le leader peu unrank un officier.")
                return
            else:
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["officier_prim"]))
                await member_secondary_guild.remove_roles(secondary_guild.get_role(config["roles"]["officier_sec"]))
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["deco_hauts_grade"]))
                await ctx.respond(f"{user.mention} est passé Membre confirmé")
                grade = "Membre+"
        elif data == 5:
            if not member_principal_guild.get_role(config["roles"]["second"]):
                await ctx.respond("Seul le leader peu unrank un gouverneur <3")
                return
            else:
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["gouverneur"]))
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["deco_dieu"]))
                await ctx.respond(f"{user.mention} est passé officier")
                grade = "Officier"
        else:
            return

        ig_name = cur.execute("SELECT pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        try:
            await member_principal_guild.edit(nick=f"{grade} | {ig_name[0]}")
            await member_secondary_guild.edit(nick=f"{grade} | {ig_name[0]}")
        except discord.errors.Forbidden:
            pass
        cur.execute("UPDATE recrutement SET grade = grade-1 WHERE id_discord=?", [user.id])
        self.bot.db.commit()
        cur.close()

    # Command /condition
    @commands.slash_command(description="Modifies les données de rank d'un joueur.", default_permission=True)
    async def condition(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur."),
                        donnees: Option(str, "Condition a valider.", choices=["house", "donations", "constructions", "double compte", "participation animation", "créer animation", "recrutement"]),
                        valeur: Option(int, "Entre une valeur.", required=True)):
        cur = self.bot.db.cursor()

        principal_guild = self.bot.get_guild(config["principal_guild_id"])
        member_principal_guild = principal_guild.get_member(ctx.user.id)

        if donnees == "house":
            if member_principal_guild.get_role(config["roles"]["administrateur"]):
                cur.execute("UPDATE recrutement SET statut_maison = statut_maison+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"La maison de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul un administrateur peu effectué cette validation")

        elif donnees == "donations":
            if member_principal_guild.get_role(config["roles"]["officier_prim"]):
                cur.execute("UPDATE recrutement SET donations = donations+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"Les donations de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul un officier peu effectué cette validation")

        elif donnees == "constructions":
            if member_principal_guild.get_role(config["roles"]["architecte"]):
                cur.execute("UPDATE recrutement SET constructions = constructions+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"L'aide au build de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul un architecte peu effectué cette validation")

        elif donnees == "double compte":
            if member_principal_guild.get_role(config["roles"]["officier_prim"]):
                cur.execute("UPDATE recrutement SET double_compte = double_compte+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"Le statut des doubles comptes de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul un officier peu effectué cette validation")

        elif donnees == "participation animation":
            if member_principal_guild.get_role(config["roles"]["animateur"]):
                cur.execute("UPDATE recrutement SET participation_animation = participation_animation+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"La participation de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul un animateur peu effectué cette validation")

        elif donnees == "créer animation":
            if member_principal_guild.get_role(config["roles"]["resp_animateurs"]):
                cur.execute("UPDATE recrutement SET creer_animation = creer_animation+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"La création d'animation de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul le resp. animateurs peu effectué cette validation")

        elif donnees == "recrutement":
            if member_principal_guild.get_role(config["roles"]["resp_recruteurs"]):
                cur.execute("UPDATE recrutement SET nb_recrutement = nb_recrutement+? WHERE id_discord=?", [valeur, user.id])
                await ctx.respond(f"La participation au recrutement de {user.mention} a bien été validé")
            else:
                await ctx.respond(f"Seul le resp. recruteurs peu effectué cette validation")

        self.bot.db.commit()
        cur.close()

    # Command /absence
    @commands.slash_command(description="Donne toute les informations publique sur une personne")
    async def absence(self, ctx: discord.ApplicationContext, fin: Option(str, "Entre une date de fin", required=True)):

        user = ctx.user
        try:
            fin = date.fromisoformat(fin)
        except ValueError:
            await ctx.respond("Format de l'absence invalide ! Écrit sous la forme AAAA-MM-JJ (Année, puis un tiret du 6, Mois, re un tiret et enfin le jour), comme par exemple : 2023-05-25")
            return
        cur = self.bot.db.cursor()
        cur.execute("UPDATE recrutement SET absence_fin = ? WHERE id_discord=?", [fin, user.id])
        self.bot.db.commit()

        await ctx.respond(f"Ton absence jusqu'au {fin} a bien été enregistrer")
