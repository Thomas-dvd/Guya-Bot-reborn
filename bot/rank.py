import json
from datetime import date, timedelta

import discord
from discord import Option, Color
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
                text += f"__Pays :__ ✅\n"
            else:
                text += f"__Pays :__ ❌ Tu doit encore rejoindre le pays. 1️⃣\n"
            if maison:
                text += "__Maison :__ ✅\n"
            else:
                text += f"__Maison :__ ❌ Tu doit encore finir ta maison. 2️⃣\n"
            if time:
                text += "__Ancienneté :__ ✅\n"
            else:
                text += "__Ancienneté :__ ❌ Tu doit avoir une semaine d'ancienneté. 3️⃣\n"
            if do_player_info:
                text += "__Utilisation du bot :__ ✅\n"
            else:
                text += f"__Utilisation du bot :__ ❌ Tu doit t'être renseigné au moins une fois sur tes conditions de rank. 4️⃣\n"

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
                    text += f"__Contribution économique :__ ❌ Tu doit encore farmer {5000 - data['donations']}$ pour le pays. 5️⃣\n"
            else:
                text += "__Farming :__ ❌ Pour rejoindre le pôle économique, tu doit récupérer le grade @Farmer. 6️⃣\n"

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
                    text += f"__Contribution de build :__ ❌ Tu doit participer a encore au moins {1 - data['constructions']} chantier de build. 7️⃣\n"
            else:
                text += "__Constructeur :__ ❌ Pour rejoindre le pôle build, tu doit récupérer le grade @Constructeur. 8️⃣\n"

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
                text += f"__Maison :__ ❌ Tu doit encore finir ta maison de membre. 1️⃣\n"
            if double_compte:
                text += "__Double compte :__ ✅\n"
            else:
                text += f"__Double compte :__ ❌ Tu doit mettre un DC dans le trinité-et-tobago. 2️⃣\n"
            if time:
                text += "__Ancienneté :__ ✅\n"
            else:
                text += "__Ancienneté :__ ❌ Tu doit avoir un mois d'ancienneté. 3️⃣\n"

            donation = data["donations"] >= 20000

            if donation:
                text += f"\n**Pôle économique :** ✅\n"
            else:
                text += f"\n**Pôle économique :** ❌\n"
            if donation:
                text += "__Contribution économique :__ ✅\n"
            else:
                text += f"__Contribution économique :__ ❌ Tu doit encore farmer {20000 - data['donations']}$ pour le pays. 4️⃣\n"

            projet = data["constructions"] >= 4

            if projet:
                text += f"\n**Pôle build :** ✅\n"
            else:
                text += f"\n**Pôle build :** ❌\n"
            if projet:
                text += "__Contribution de build :__ ✅\n"
            else:
                text += f"__Contribution de build :__ ❌ Tu doit participer a encore au moins {4 - data['constructions']} chantier de build. 5️⃣\n"

            animation = data["participation_animation"] == 1

            if animation:
                text += f"\n**Pôle animation :** ✅\n"
            else:
                text += f"\n**Pôle animation :** ❌\n"
            if animation:
                text += "__Participation a une animation :__ ✅\n"
            else:
                text += f"__Participation a une animation :__ ❌ Tu doit participer a une animation (demander aux animateur de noté ta participation. 6️⃣)\n"

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
                text += "__Ancienneté :__ ❌ Tu doit avoir 3 mois d'ancienneté. 1️⃣\n\n"

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
                text += f"| __Contribution :__ ❌ Tu doit encore farmer {70000 - data['donations']}$ pour le pays. 2️⃣\n"

            if projet and grade_archi_builder:
                text += f"|\n| **Pôle build :** ✅\n"
            else:
                text += f"|\n| **Pôle build :** ❌\n"
            if projet:
                text += "| __Contribution de build :__ ✅\n"
            else:
                text += f"| __Contribution de build :__ ❌ Tu doit participer a encore au moins {9 - data['constructions']} chantier de build. 3️⃣\n"
            if grade_archi_builder:
                text += "| __Gestion de build :__ ✅\n"
            else:
                text += f"| __Gestion de build :__ ❌ Tu doit candidaté pour devenir @Architecte ou @Builder. 4️⃣\n"

            if grade_anim and animation:
                text += f"|\n| **Pôle animation :** ✅\n"
            else:
                text += f"|\n| **Pôle animation :** ❌\n"
            if grade_anim:
                if animation:
                    text += "| __Animation :__ ✅\n"
                else:
                    text += f"| __Animation :__ ❌ Tu doit encore organiser au moins {9 - data['creer_animation']} animations. 6️⃣\n"
            else:
                text += f"| __Animation :__ ❌ Tu doit candidaté pour devenir @Animateur. 5️⃣\n"

            if grade_recru and nb_recrutement:
                text += f"|\n| **Pôle recrutement :** ✅\n"
            else:
                text += f"|\n| **Pôle recrutement :** ❌\n"
            if grade_recru:
                if nb_recrutement:
                    text += "| __Recrutement :__ ✅\n"
                else:
                    text += f"| __Recrutement :__ ❌ Tu doit encore recruter au moins {10 - data['nb_recrutement']} joueurs. 8️⃣\n"
            else:
                text += f"| __Recrutement :__ ❌ Tu doit candidaté pour devenir @Recruteur. 7️⃣\n"

            text += "\n**Récompense de rank :** Speed Leg (+40% de vitesse de déplacement)"

        elif data["grade"] == 4:  # Membre confirmé
            embed.add_field(name="Grade :", value="Membre confirmé")
            text += "Pour continuer à progresser dans le pays, il n'y a plus de conditions de rank précises. Le rank Officier ou gouverneur, est rare, il faut valider de nombreuses conditions. Le meilleur moyen de passé Officier, c'es-t-en continuant, tous les jours à t'investir pour le pays, à être présent et à l'écoute des autres, et ainsi permettre à notre nation d'avancer"

        elif data["grade"] == 5:  # Officier
            embed.add_field(name="Grade :", value="Officier")
            text += "Pour continuer à progresser dans le pays, il n'y a plus de conditions de rank précises. Le rank Officier ou gouverneur, est rare, il faut valider de nombreuses critères. Le meilleur moyen de passé Officier, c'es-t-en continuant, tous les jours à t'investir pour le pays, à être présent et à l'écoute des autres, et ainsi permettre à notre nation d'avancer"

        elif data["grade"] == 6:  # Gouverneur
            embed.add_field(name="Grade :", value="Gouverneur")
            text += "Le grade de leader n'est pas négotiable"

        elif data["grade"] == 7:  # Leader
            embed.add_field(name="Grade :", value="Leader")
            text += "Oui alors... Que dire ici... En soit on dit que la vie c'est de ne jamais arrêter d'apprendre, donc on peu toujours s'élever nan ? Bon ca répond pas la question... Que dire ici ? On a qu'a dire que c'est un easter egg. Ouais c'est une bonne idée, donc \"Ouais GG t'a trouver un easter egg !\" Voila, c'est tout, donc retourne bossé maintenant au lieu de lire ce genre de message"

        embed.add_field(name="}============{ Condition de rank }============{", value=f"{text}", inline=False)

        await ctx.respond(embed=embed)

    # Detection réaction player-info
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if f"{message.author}" != f"{self.bot.user.name}#{self.bot.user.discriminator}":
            return
        embed = message.embeds[0]
        check = embed.fields[6].name
        grade = embed.fields[6].value

        if check != "Grade :":
            return

        if grade == "Nouvelle recrue":
            if payload.emoji.name == "1️⃣":
                await message.reply(f"__La condition de rank **Pays** (réaction 1️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est automatique, elle ce valide toute seule dès que vous avez rejoint un des pays de la GDE IG (peu mettre jusqu'a 24h à s'actualiser")
            if payload.emoji.name == "2️⃣":
                await message.reply(f"__La condition de rank **Maison** (réaction 2️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est valider par un administrateur quand votre maison est conforme.\n\n **1 - Trouver son schématique :**\n\nPour construire votre maison, vous devez télécharger le schématique disponible en cliquant sur le texte en bleu en dessous de \"Schématique\" dans le /player-info (Pour apprendre à utiliser Schematica : X).\nVotre schématique fait précisément 16x16 blocs, exactement la même taille que votre chunk. Il faut donc le poser de telle sorte qu'il rentre dedans. Il n'est pas nécessaire de tourner le schématique, celui-ci est directement dans le bon sens. Arrangez-vous pour que la hauteur du sol (laine rouge, bleu et vert) corresponde au sols des maisons mitoyennes.\n\n**2 - Les blocs à utiliser :**\n\nUne fois le schématique posé correctement, il faut commencer à le construire avec les mêmes blocs que ceux affichés (à l'exception de la laine posée au sol). Tous les blocs sont disponibles au __/f home__ dans des chestshop (shop automatisé avec des panneaux) à l'exception de la laine, celle-ci n'est pas à poser, voir ci dessous. *__Tips__ : Il est conseillé de construire sa maison couche par couche*\n\n**3 - Construire la route devant sa maison (Laines) :**\n\nLes 4 types de laines correspondent en réalité à un \"damier\" de plusieurs blocs différents à poser de manière aléatoire. Au bkr, chaque coffre avec une laine (rouge, bleu ou verte) doit être utilisé pour le damier en rapport. Pour le damier cyan, il faut mélanger des blocs du damier rouge et bleu.\n\n**4 - Meublement de votre maison :**\n\nPour finir, rajouter de la décoration à l'intérieur et à l'extérieur pour permettre de valider officiellement votre maison. (le meublement se fait à votre guise et selon vos goûts)\n\n**=> Votre maison est alors finie. Crée un ticket en rapport dans <#1019554369764589579>. Envoyez les coordonnées de votre maison**")
            if payload.emoji.name == "3️⃣":
                await message.reply(f"__La condition de rank **Ancienneté** (réaction 3️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est automatique, elle ce valide d'elle même lorsque votre ancienneté dépasse 1 semaine (calculer sur la date du /register), un message vous sera par ailleurs également envoyé")
            if payload.emoji.name == "4️⃣":
                await message.reply(f"__La condition de rank **Utilisation du bot** (réaction 4️⃣) :__ *demander par {payload.member.mention}*\n \nCondition qui ce valide dès lors que vous avez fait au moins 1 /player-info")
            if payload.emoji.name == "5️⃣":
                await message.reply(f"__La condition de rank **Contribution économique** (réaction 5️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition doit être valider manuellement. Le pôle économiques met a votre dispositions diverses techniques de farms pour ce faire de l'argent, que vous êtes libre d'utiliser ou non.\nPour passer Recrue confirmé, nous demander a toute les Nouvelles recrues une donation de 5.000$ au pays. Pour la faire, executez la commande __/econ bank deposite guyana 5000__ pour mettre de l'argent dans la banque de la guyana. Un message apparaitra alors dans le chat globale, prenez le alors en photo (double F2 de préférence) et envoyez le dans <#1019966582652416000>, un Officier s'occupera alors d'actualiser le montant total de vos donations.\n \n*PS: Vous n'êtes pas obliger de déposer 5.000$ d'un coup, le bot est en mesure de vous dire quel quantité il vous reste a donner. Dans la même logique, vous pouvez donner plus et cela sera pris en compte pour la même condition du passage de Recrue confirmé à Membre*")
            if payload.emoji.name == "6️⃣":
                await message.reply(f"__La condition de rank **Contribution de build** (réaction 6️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est en 2 partie, la première consiste à rejoindre le pôle économique en récupérant le grade Farmer dans le <#1019552996276850720>")
            if payload.emoji.name == "7️⃣":
                await message.reply(f"__La condition de rank **Contribution de build** (réaction 7️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition doit être valider manuellement. Dans le pôle build, vous trouverez un fils \"__Accès__\" pour participer au différents projets de constructions de la guyana, et signalé lorsque vous avez finit. Un Officier s'occupera alors d'actualiser le total de vos aide au build en guyana.\n \n*PS: Le bot est en mesure de vous dire sur combien de chantier vous avez participer. Vous pouvez donc a participate a plus qu'indiquer et cela sera pris en compte pour la même condition du passage de Recrue confirmé à Membre*")
            if payload.emoji.name == "8️⃣":
                await message.reply(f"__La condition de rank **Contribution de build** (réaction 8️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est en 2 partie, la première consiste à rejoindre le pôle build en récupérant le grade Constructeur dans le <#1019553526319435796>")

        if grade == "Recrue confirmé":
            if payload.emoji.name == "1️⃣":
                await message.reply(f"__La condition de rank **Maison** (réaction 1️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est valider par un administrateur quand votre maison est conforme. Le schématique vous a été fournit au moment de votre rank Recrue confirmé, vous pouvez demander a un Officier de vous le redonnez si vous l'avez perdu")
            if payload.emoji.name == "2️⃣":
                await message.reply(f"__La condition de rank **Double compte** (réaction 2️⃣) :__ *demander par {payload.member.mention}*\n \nPour aider le pays, nous vous demandons de crée un double compte sur NationsGlory (vous pouvez aller jusqu'a 4 compte sur la même IP). Vous devez alors vous connecter sur le serveur Green et rejoindre le trinité (pays ouvert de base, accessible avec : __/f join triniteettobago__). Envoyez ensuite un screen de votre DC dans le trinité dans le <#1019966582652416000>.\nNous vous demandons également si possible de restez connecter un certains temps sur ce double compte pour monter son power (visible avec la commande __/f s__), pas besoin de faire des actions particulière, juste être connecter")
            if payload.emoji.name == "3️⃣":
                await message.reply(f"__La condition de rank **Ancienneté** (réaction 3️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est automatique, elle ce valide d'elle même lorsque votre ancienneté dépasse 1 mois (calculer sur la date du /register), un message vous sera par ailleurs également envoyé")
            if payload.emoji.name == "4️⃣":
                await message.reply(f"__La condition de rank **Contribution économique** (réaction 4️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition doit être valider manuellement. Pour passer Membre, nous demander a toute les Recrues confirmé une donation de 15.000$ au pays. Pour la faire, executez la commande __/econ bank deposite guyana 15000__ pour mettre de l'argent dans la banque de la guyana. Un message apparaitra alors dans le chat globale, prenez le alors en photo (double F2 de préférence) et envoyez le dans <#1019966582652416000>, un Officier s'occupera alors d'actualiser le montant total de vos donations.\n \n*PS: Vous n'êtes pas obliger de déposer 15.000$ d'un coup, le bot est en mesure de vous dire quel quantité il vous reste a donner. Dans la même logique, vous pouvez donner plus et cela sera pris en compte pour la même condition du passage de Membre à Membre confirmé*")
            if payload.emoji.name == "5️⃣":
                await message.reply(f"__La condition de rank **Contribution de build** (réaction 5️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition doit être valider manuellement. Dans le pôle build, vous trouverez un fils \"__Accès__\" pour participer au différents projets de constructions de la guyana, et signalé lorsque vous avez finit. Un Officier s'occupera alors d'actualiser le total de vos aide au build en guyana.\n \n*PS: Le bot est en mesure de vous dire sur combien de chantier vous avez participer. Vous pouvez donc a participate a plus qu'indiquer et cela sera pris en compte pour la même condition du passage de Membre à Membre confirmé*")
            if payload.emoji.name == "6️⃣":
                await message.reply(f"__La condition de rank **Participation a une activité** (réaction 6️⃣) :__ *demander par {payload.member.mention}*\n \nPour passer Membre, nous vous demandons d'avoir participer au moins une fois a une animation organiser par le pôle animateur. Le planning est envoyer dans le <#895676485598347305>. N'oublier pas de demander au animateur de valider votre participation à la fin de l'event (une seul fois est suffisante, ce n'est pas cumulable)")

        if grade == "Membre":
            if payload.emoji.name == "1️⃣":
                await message.reply(f"__La condition de rank **Ancienneté** (réaction 1️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est automatique, elle ce valide d'elle même lorsque votre ancienneté dépasse 3 mois (calculer sur la date du /register), un message vous sera par ailleurs également envoyé")
            if payload.emoji.name == "2️⃣":
                await message.reply(f"__La condition de rank **Contribution économique** (réaction 2️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition doit être valider manuellement. Pour passer Membre confirmé, nous demander a toute les Recrues confirmé une donation de 50.000$ au pays. Pour la faire, executez la commande __/econ bank deposite guyana 50000__ pour mettre de l'argent dans la banque de la guyana. Un message apparaitra alors dans le chat globale, prenez le alors en photo (double F2 de préférence) et envoyez le dans <#1019966582652416000>, un Officier s'occupera alors d'actualiser le montant total de vos donations.\n \n*PS: Vous n'êtes pas obliger de déposer 15.000$ d'un coup, le bot est en mesure de vous dire quel quantité il vous reste a donner.*")
            if payload.emoji.name == "3️⃣":
                await message.reply(f"__La condition de rank **Contribution de build** (réaction 3️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition doit être valider manuellement. Dans le pôle build, vous trouverez un fils \"__Accès__\" pour participer au différents projets de constructions de la guyana, et signalé lorsque vous avez finit. Un Officier s'occupera alors d'actualiser le total de vos aide au build en guyana.\n \n*PS: Le bot est en mesure de vous dire sur combien de chantier vous avez participer.*")
            if payload.emoji.name == "4️⃣":
                await message.reply(f"__La condition de rank **Gestion de build** (réaction 4️⃣) :__ *demander par {payload.member.mention}*\n \nPour valider cette condition, vous devez candidater et devenir Builder ou Architecte via le <#1019843946593140787>")
            if payload.emoji.name == "5️⃣":
                await message.reply(f"__La condition de rank **Animation** (réaction 5️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est en 2 partie, la première consiste à candidater pour le grade Animateur dans le <#1019843946593140787>")
            if payload.emoji.name == "6️⃣":
                await message.reply(f"__La condition de rank **Animation** (réaction 6️⃣) :__ *demander par {payload.member.mention}*\n \nVous devez réaliser un minimum de 9 animation en temps qu'animateur (demandez au Resp. Animateur de noté les animations que vous organiser).")
            if payload.emoji.name == "7️⃣":
                await message.reply(f"__La condition de rank **Recrutement** (réaction 7️⃣) :__ *demander par {payload.member.mention}*\n \nCette condition est en 2 partie, la première consiste à candidater pour le grade Recruteur dans le <#1019843946593140787>")
            if payload.emoji.name == "8️⃣":
                await message.reply(f"__La condition de rank **Recrutement de build** (réaction 8️⃣) :__ *demander par {payload.member.mention}*\n \nVous devez réaliser un minimum de 10 recrutement en temps que recruteur (demandez au Resp. recruteur de noté les recrutement que vous organiser).")

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
            await ctx.respond(f"{user.mention} est passé Recrue confirmé")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Recrue confirmé. 🎉")
            cur.execute("UPDATE recrutement SET grade = 2 WHERE id_discord=?", [user.id])
            grade = "Recrue+"
        elif data == 2:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre. 🎉")
            cur.execute("UPDATE recrutement SET grade = 3 WHERE id_discord=?", [user.id])
            grade = "Membre"
        elif data == 3:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre confirmé")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre confirmé. 🎉")
            cur.execute("UPDATE recrutement SET grade = 4 WHERE id_discord=?", [user.id])
            grade = "Membre+"
        elif data == 4:
            if not ctx.user.get_role(config["roles"]["gouverneur"]) and not ctx.user.get_role(config["roles"]["gouverneur_sec"]):
                await ctx.respond("Seul un gouverneur ou le leader peu rank un membre confirmé Officier.")
                return
            else:
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["officier_prim"]))
                try:
                    await member_secondary_guild.add_roles(secondary_guild.get_role(config["roles"]["officier_sec"]))
                except AttributeError:
                    pass
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["deco_hauts_grade"]))
                await ctx.respond(f"{user.mention} est passé Officier")
                await channel_gg.send(f"Félicitaion à {user.mention} qui passe Officier. 🎉")
                cur.execute("UPDATE recrutement SET grade = 5 WHERE id_discord=?", [user.id])
                grade = "Officier"
        elif data == 5:
            if not ctx.user.get_role(config["roles"]["second"]):
                await ctx.respond("Seul le leader pour ajouté de nouveau gouverneurs <3")
                return
            else:
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["Gouverneur"]))
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["deco_dieu"]))
                await ctx.respond(f"{user.mention} est passé Gouverneur")
                await channel_gg.send(f"Félicitaion à {user.mention} qui passe Gouverneur. 🎉")
                cur.execute("UPDATE recrutement SET grade = 6 WHERE id_discord=?", [user.id])
                grade = "Gouverneur"
        else:
            return

        ig_name = cur.execute("SELECT pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        try:
            await member_principal_guild.edit(nick=f"{grade} | {ig_name[0]}")
            try:
                await member_secondary_guild.edit(nick=f"{grade} | {ig_name[0]}")
            except AttributeError:
                pass
        except discord.errors.Forbidden:
            pass
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
            await ctx.respond("Cette personne n'est pas unrankable")
            return

        if data == 2:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["recrue_confirme"]))
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["nouvelle_recrue"]))
            await ctx.respond(f"{user.mention} est passé recrue")
            cur.execute("UPDATE recrutement SET grade = 1 WHERE id_discord=?", [user.id])
            grade = "Recrue"
        elif data == 3:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Recrue+")
            cur.execute("UPDATE recrutement SET grade = 2 WHERE id_discord=?", [user.id])
            grade = "Recrue+"
        elif data == 4:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            cur.execute("UPDATE recrutement SET grade = 3 WHERE id_discord=?", [user.id])
            grade = "Membre"
        elif data == 5:
            if not ctx.user.get_role(config["roles"]["Gouverneur"]) and not ctx.user.get_role(config["roles"]["gouverneur_sec"]):
                await ctx.respond("Seul un Gouverneur ou le leader peu unrank un Officier membre confirmé .")
                return
            else:
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["officier_prim"]))
                try:
                    await member_secondary_guild.remove_roles(secondary_guild.get_role(config["roles"]["officier_sec"]))
                except AttributeError:
                    pass
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["deco_hauts_grade"]))
                await ctx.respond(f"{user.mention} est passé Membre confirmé")
                cur.execute("UPDATE recrutement SET grade = 4 WHERE id_discord=?", [user.id])
                grade = "Membre+"
        elif data == 6:
            if not ctx.user.get_role(config["roles"]["second"]):
                await ctx.respond("Seul le leader pour unrank les officiers")
                return
            else:
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["Gouverneur"]))
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["deco_dieu"]))
                await ctx.respond(f"{user.mention} est passé Officier")
                cur.execute("UPDATE recrutement SET grade = 5 WHERE id_discord=?", [user.id])
                grade = "Officier"
        else:
            return

        ig_name = cur.execute("SELECT pseudo_ingame FROM recrutement WHERE id_discord=?", [user.id]).fetchone()
        try:
            await member_principal_guild.edit(nick=f"{grade} | {ig_name[0]}")
            try:
                await member_secondary_guild.edit(nick=f"{grade} | {ig_name[0]}")
            except AttributeError:
                pass
        except discord.errors.Forbidden:
            pass
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
                await ctx.respond(f"Seul un Officier peu effectué cette validation")

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
                await ctx.respond(f"Seul un Officier peu effectué cette validation")

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
    @commands.slash_command(description="Pour noté l'absence de quelqu'un")
    @commands.has_any_role(config["roles"]["recruteur_prim"], config["roles"]["recruteur_sec"])
    async def absence(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur."), fin: Option(str, "Entre une date de fin", required=True)):

        try:
            fin = date.fromisoformat(fin)
        except ValueError:
            await ctx.respond("Format de l'absence invalide ! Écrit sous la forme AAAA-MM-JJ (Année, puis un tiret du 6, Mois, re un tiret et enfin le jour), comme par exemple : 2023-05-25")
            return
        cur = self.bot.db.cursor()
        cur.execute("UPDATE recrutement SET absence_fin = ? WHERE id_discord=?", [fin, user.id])
        self.bot.db.commit()

        await ctx.respond(f"L'absence de {user.mention} jusqu'au {fin} a bien été enregistrer")
