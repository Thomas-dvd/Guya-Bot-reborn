import json
from datetime import date, timedelta
from PIL import Image
from discord.ui import Modal, InputText, View, Button

from Merge_Pictures import merge_image

import discord
from discord import Option, Color
from discord.ext import commands

import utils
from main import GuyaBot

Admin0 = Image.open('images/Administrateur0.png')
Admin1 = Image.open('images/Administrateur1.png')
Anim0 = Image.open('images/Animateur0.png')
Anim1 = Image.open('images/Animateur1.png')
Anim2 = Image.open('images/Animateur2.png')
Build0 = Image.open('images/Builder0.png')
Build1 = Image.open('images/Builder1.png')
Build2 = Image.open('images/Builder2.png')
Build3 = Image.open('images/Builder3.png')
Farm0 = Image.open('images/Farmer0.png')
Farm1 = Image.open('images/Farmer1.png')
Farm2 = Image.open('images/Farmer2.png')
Farm3 = Image.open('images/Farmer3.png')
Journ0 = Image.open('images/Journaliste0.png')
Journ1 = Image.open('images/Journaliste1.png')
Rec0 = Image.open('images/Recruteur0.png')
Rec1 = Image.open('images/Recruteur1.png')
Rec2 = Image.open('images/Recruteur2.png')
default = Image.open('images/default.png')


with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def setup(bot):
    print('Loading cog rank')
    bot.add_cog(Rank(bot))


def player_info_main_part(bot, user, ctx):
    cur = bot.db.cursor()
    cur.execute("SELECT * FROM recrutement WHERE id_discord=?", [user.id])
    temp = cur.fetchone()
    if temp is None:
        return None

    data = {
        "id_sys": temp[0],
        "id_discord": temp[1],
        "pseudo_ingame": temp[2],
        "annee_naissance": temp[3],
        "experience": temp[4],
        "grade": temp[5],
        "pays": temp[6],
        "peut_quitter_pays": temp[7],
        "date_recrutement": temp[8],
        "anciennete": temp[9],
        "schematique": temp[10],
        "last_connection": temp[11],
        "absence_fin": temp[12],
        "has_done_player_info": temp[13],
        "statut_maison": temp[14],
        "double_compte": temp[15],
        "soldat": temp[16],
        "journaliste": temp[17],
        "recruteur": temp[18],
        "animateur": temp[19],
        "joueur": temp[20],
        "builder": temp[21],
        "constructeur": temp[22],
        "directeur": temp[23],
        "économiste": temp[24],
        "farmer": temp[25]
    }

    if data['has_done_player_info'] != 1 and ctx is not None:
        cur.execute("UPDATE recrutement SET has_done_player_info = 1 WHERE id_discord=?", [ctx.user.id])
        bot.db.commit()

    jobs = {
        "MSoldat": -1,
        "MJournaliste": -1,
        "MRecruteur": -1,
        "MAnimateur": -1,
        "MJoueur": -1,
        "MBuilder": -1,
        "MConstructeur": -1,
        "MDirecteur": -1,
        "MÉconomiste": -1,
        "MFarmer": -1,

        "Mnv1": 0,
        "Mnv2": 0,
        "Mnv3": 0,
        "vect_image": []
    }

    # Setup metiers levels
    if user.get_role(config["roles"]["jobs"]["soldat"]) is not None:
        if data['soldat'] == 1:
            jobs['MSoldat'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(default)
        elif data['soldat'] == 2:
            jobs['MSoldat'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['soldat'] >= 3:
            jobs['MSoldat'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MSoldat'] = 0
            jobs['vect_image'].append(default)
    if user.get_role(config["roles"]["jobs"]["journaliste"]) is not None:
        if data['journaliste'] == 1:
            jobs['MJournaliste'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(Journ1)
        elif data['journaliste'] == 2:
            jobs['MJournaliste'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['journaliste'] >= 3:
            jobs['MJournaliste'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MJournaliste'] = 0
            jobs['vect_image'].append(Journ0)
    if user.get_role(config["roles"]["jobs"]["recruteur"]) is not None:
        if 13 > data['recruteur'] >= 3:
            jobs['MRecruteur'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(Rec1)
        elif 28 > data['recruteur'] >= 13:
            jobs['MRecruteur'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(Rec2)
        elif data['recruteur'] >= 28:
            jobs['MRecruteur'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MRecruteur'] = 0
            jobs['vect_image'].append(Rec0)
    if user.get_role(config["roles"]["jobs"]["animateur"]) is not None:
        if 8 > data['animateur'] >= 3:
            jobs['MAnimateur'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(Anim1)
        elif 18 > data['animateur'] >= 8:
            jobs['MAnimateur'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(Anim2)
        elif data['animateur'] >= 18:
            jobs['MAnimateur'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MAnimateur'] = 0
            jobs['vect_image'].append(Anim0)
    if user.get_role(config["roles"]["jobs"]["joueur"]) is not None:
        if 25000 > data['joueur'] >= 10000:
            jobs['MJoueur'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(default)
        elif 50000 > data['joueur'] >= 25000:
            jobs['MJoueur'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['joueur'] >= 50000:
            jobs['MJoueur'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MJoueur'] = 0
            jobs['vect_image'].append(default)
    if user.get_role(config["roles"]["jobs"]["builder"]) is not None:
        if 6 > data['builder'] >= 1:
            jobs['MBuilder'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(Build1)
        elif 16 > data['builder'] >= 6:
            jobs['MBuilder'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(Build2)
        elif data['builder'] >= 16:
            jobs['MBuilder'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(Build3)
        else:
            jobs['MBuilder'] = 0
            jobs['vect_image'].append(Build0)
    if user.get_role(config["roles"]["jobs"]["constructeur"]) is not None:
        if 8 > data['constructeur'] >= 3:
            jobs['MConstructeur'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(default)
        elif 23 > data['constructeur'] >= 8:
            jobs['MConstructeur'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['constructeur'] >= 23:
            jobs['MConstructeur'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MConstructeur'] = 0
            jobs['vect_image'].append(default)
    if user.get_role(config["roles"]["jobs"]["directeur"]) is not None:
        if data['directeur'] == 1:
            jobs['MDirecteur'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(default)
        elif data['directeur'] == 2:
            jobs['MDirecteur'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['directeur'] >= 3:
            jobs['MDirecteur'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MDirecteur'] = 0
            jobs['vect_image'].append(default)
    if user.get_role(config["roles"]["jobs"]["économiste"]) is not None:
        if data['économiste'] == 1:
            jobs['MÉconomiste'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(default)
        elif data['économiste'] == 2:
            jobs['MÉconomiste'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['économiste'] >= 3:
            jobs['MÉconomiste'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MÉconomiste'] = 0
            jobs['vect_image'].append(default)
    if user.get_role(config["roles"]["jobs"]["farmer"]) is not None:
        if 20000 > data['farmer'] >= 5000:
            jobs['MFarmer'] = 1
            jobs['Mnv1'] += 1
            jobs['vect_image'].append(default)
        elif 70000 > data['farmer'] >= 20000:
            jobs['MFarmer'] = 2
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['vect_image'].append(default)
        elif data['farmer'] >= 70000:
            jobs['MFarmer'] = 3
            jobs['Mnv1'] += 1
            jobs['Mnv2'] += 1
            jobs['Mnv3'] += 1
            jobs['vect_image'].append(default)
        else:
            jobs['MFarmer'] = 0
            jobs['vect_image'].append(default)

    embed = utils.create_embed(bot, f"Stats de {user}")
    embed.add_field(name="Nom en jeu :", value=f"{data['pseudo_ingame']}")
    embed.add_field(name="ID système :", value=f"{data['id_sys']}")
    embed.add_field(name="Pays :", value=f"{data['pays']}")
    embed.add_field(name="Dernière connexion :", value=f"{data['last_connection']}")
    embed.add_field(name="Date de recrutement :", value=f"{data['date_recrutement']}")
    embed.add_field(name="Schematic :", value=f"[{data['schematique']}]({config['schematics'][data['schematique']] if data['schematique'] in config['schematics'] else 'https://www.youtube.com/c/Tominix356?sub_confirmation=1'})")

    if data["grade"] == 0:  # Candidat
        embed.add_field(name="Grade :", value="Candidat")
    elif data["grade"] == 1:  # Nouvelle recrue
        embed.add_field(name="Grade :", value="Nouvelle recrue")
    elif data["grade"] == 2:  # Recrue confirmé
        embed.add_field(name="Grade :", value="Recrue confirmé")
    elif data["grade"] == 3:  # Membre
        embed.add_field(name="Grade :", value="Membre")
    elif data["grade"] == 4:  # Membre confirmé
        embed.add_field(name="Grade :", value="Membre confirmé")
    elif data["grade"] == 5:  # Officier
        embed.add_field(name="Grade :", value="Officier")
    elif data["grade"] == 6:  # Gouverneur
        embed.add_field(name="Grade :", value="Gouverneur")
    elif data["grade"] == 7:  # Leader
        embed.add_field(name="Grade :", value="Leader")

    return embed, jobs, data


def player_info_rank_part(data, embed, jobs):
    text = ""
    if data["grade"] == 0:  # Candidat
        text += "Tu doit finir ton recrutement"

    elif data["grade"] == 1:  # Nouvelle recrue

        if data["pays"] in config["list_pays"]:
            text += f"__Pays :__ ✅\n"
        else:
            text += f"__Pays :__ ❌ Tu doit encore rejoindre le pays. 1️⃣\n"
        if data["statut_maison"] >= 1:
            text += "__Maison :__ ✅\n"
        else:
            text += f"__Maison :__ ❌ Tu doit encore finir ta maison. 2️⃣\n"
        if data["anciennete"] >= 1:
            text += "__Ancienneté :__ ✅\n"
        else:
            text += "__Ancienneté :__ ❌ Tu doit avoir une semaine d'ancienneté. 3️⃣\n"
        if data["has_done_player_info"] == 1:
            text += "__Utilisation du bot :__ ✅\n"
        else:
            text += f"__Utilisation du bot :__ ❌ Tu doit t'être renseigné au moins une fois sur tes conditions de rank. 4️⃣\n"
        if jobs['Mnv1'] >= 1:
            text += f"__Métiers :__ ✅\n"
        else:
            text += f"__Métiers :__ ❌ Tu doit avoir : un métier *Nv.1* ({jobs['Mnv1']}/1 Nv.1).\n"

    elif data["grade"] == 2:  # Recrue confirmé

        if data["statut_maison"] >= 2:
            text += "__Maison :__ ✅\n"
        else:
            text += f"__Maison :__ ❌ Tu doit encore finir ta maison de membre. 1️⃣\n"
        if data["double_compte"] >= 1:
            text += "__Double compte :__ ✅\n"
        else:
            text += f"__Double compte :__ ❌ Tu doit mettre un DC dans le trinité-et-tobago. 2️⃣\n"
        if data["anciennete"] >= 2:
            text += "__Ancienneté :__ ✅\n"
        else:
            text += "__Ancienneté :__ ❌ Tu doit avoir un mois d'ancienneté. 3️⃣\n"
        if jobs['Mnv2'] >= 2 or (jobs['Mnv1'] >= 3 and jobs['Mnv2'] >= 1):
            text += f"__Métiers :__ ✅\n"
        else:
            text += f"__Métiers :__ ❌ Tu doit avoir : deux métier *Nv.2* ({jobs['Mnv2']}/2 Nv.2) __ou__ un métier *Nv.2* et deux métier *Nv.1* ({jobs['Mnv2']}/1 Nv.2, {jobs['Mnv1'] - 1}/2 Nv.1).\n"

    elif data["grade"] == 3:  # Membre

        if data["anciennete"] == 3:
            text += "__Ancienneté :__ ✅\n\n"
        else:
            text += "__Ancienneté :__ ❌ Tu doit avoir 3 mois d'ancienneté. 1️⃣\n"
        if jobs['Mnv3'] >= 2 or jobs['Mnv2'] >= 3:
            text += f"__Métiers :__ ✅ ({jobs['Mnv2']}/1) ({jobs['Mnv1']}/2)\n"
        else:
            text += f"__Métiers :__ ❌ Tu doit avoir : deux métier *Nv.3* ({jobs['Mnv3']}/2) __ou__ trois métier *Nv.2* ({jobs['Mnv2']}/3).\n"

    elif data["grade"] == 4:  # Membre confirmé
        text += "*Soon...*\n Dans l'attente de l'arriver des conditions, pour continuer à progresser dans le pays, il n'y a plus de conditions de rank précises. C'est basé sur votre implication dans le pays"

    elif data["grade"] == 5:  # Officier
        text += "Il n'y a plus de conditions de rank précises. C'est basé sur votre implication dans le pays"

    elif data["grade"] == 6:  # Gouverneur
        text += "Le grade de leader n'est pas négotiable"

    elif data["grade"] == 7:  # Leader
        text += "Oui alors... Que dire ici... En soit on dit que la vie c'est de ne jamais arrêter d'apprendre, donc on peu toujours s'élever nan ? Bon ca répond pas la question... Que dire ici ? On a qu'a dire que c'est un easter egg. Ouais c'est une bonne idée, donc \"Ouais GG t'a trouver un easter egg !\" Voila, c'est tout, donc retourne bossé maintenant au lieu de lire ce genre de message"

    embed.add_field(name="}==============={ Condition de rank }==============={", value=f"{text}", inline=False)

    return embed


def player_info_jobs_part(embed, jobs, selected_job, data):
    text = ""
    can_join = 0
    if selected_job == 1:   # Soldat
        metier_name = "Soldat"
        embed.color = Color.default()
        if jobs['MSoldat'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de soldat, du pôle __pvp__ ⬛ consiste a protéger la faction de toute menace, par la force, l'intelligence et la discipline, mais surtout l'amour de la patrie.*\n\n**Condition pour rejoindre : **\nConditions a venir"
            can_join = 2
        elif jobs['MSoldat'] == 0:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de soldat, du pôle __pvp__ ⬛ consiste a protéger la faction de toute menace, par la force, l'intelligence et la discipline, mais surtout l'amour de la patrie.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2
        elif jobs['MSoldat'] == 1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de soldat, du pôle __pvp__ ⬛ consiste a protéger la faction de toute menace, par la force, l'intelligence et la discipline, mais surtout l'amour de la patrie.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2
        elif jobs['MSoldat'] == 2:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de soldat, du pôle __pvp__ ⬛ consiste a protéger la faction de toute menace, par la force, l'intelligence et la discipline, mais surtout l'amour de la patrie.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2
        elif jobs['MSoldat'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de soldat, du pôle __pvp__ ⬛ consiste a protéger la faction de toute menace, par la force, l'intelligence et la discipline, mais surtout l'amour de la patrie.*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2

    if selected_job == 2:   # Journaliste
        metier_name = "Journaliste"
        embed.color = Color.blue()
        if jobs['MJournaliste'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de journaliste, du pôle __journal__ 🟦 consiste a gérer l'écriture de scripte, leurs enregistrements, leurs montage dans des vidéos qui sont par la suite diffusée sur youtube.*\n\n**Condition pour rejoindre : **\nConditions a venir"
            can_join = 2
        if jobs['MJournaliste'] == 0:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905037272002570/Journaliste0.png")
            text += f"*Le métier de journaliste, du pôle __journal__ 🟦 consiste a gérer l'écriture de scripte, leurs enregistrements, leurs montage dans des vidéos qui sont par la suite diffusée sur youtube.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2
        elif jobs['MJournaliste'] == 1:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905037666254938/Journaliste1.png")
            text += f"*Le métier de journaliste, du pôle __journal__ 🟦 consiste a gérer l'écriture de scripte, leurs enregistrements, leurs montage dans des vidéos qui sont par la suite diffusée sur youtube.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2
        elif jobs['MJournaliste'] == 2:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de journaliste, du pôle __journal__ 🟦 consiste a gérer l'écriture de scripte, leurs enregistrements, leurs montage dans des vidéos qui sont par la suite diffusée sur youtube.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2
        elif jobs['MJournaliste'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de journaliste, du pôle __journal__ 🟦 consiste a gérer l'écriture de scripte, leurs enregistrements, leurs montage dans des vidéos qui sont par la suite diffusée sur youtube.*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant : **\nConditions a venir"
            can_join = 2

    if selected_job == 3:   # Recruteur
        metier_name = "Recruteur"
        embed.color = Color.purple()
        if jobs['MRecruteur'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de recruteur, du pôle __recrutement__ 🟪 consiste a accueillir les nouveaux arrivants, les formés et s'assurée de leurs intégration dans le pays.*\n\n**Condition pour rejoindre : **\n- Savoir parler en vocal de manière convaincu, chaleureuse, accueillante, ne pas être timide\n- Être au minimum <@&{config['roles']['grades']['membre']}>"
            if data['grade'] >= 3:
                can_join = 1
        if jobs['MRecruteur'] == 0:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905035103547402/Recruteur0.png")
            text += f"*Le métier de recruteur, du pôle __recrutement__ 🟪 consiste a accueillir les nouveaux arrivants, les formés et s'assurée de leurs intégration dans le pays.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant : **\n- Avoir effectuer 3 recrutement ({3-data['recruteur']} restant)"
        elif jobs['MRecruteur'] == 1:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905035543937114/Recruteur1.png")
            text += f"*Le métier de recruteur, du pôle __recrutement__ 🟪 consiste a accueillir les nouveaux arrivants, les formés et s'assurée de leurs intégration dans le pays.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant : **\n- Avoir effectuer 10 recrutement ({13-data['recruteur']} restant)"
        elif jobs['MRecruteur'] == 2:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905035862708355/Recruteur2.png")
            text += f"*Le métier de recruteur, du pôle __recrutement__ 🟪 consiste a accueillir les nouveaux arrivants, les formés et s'assurée de leurs intégration dans le pays.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant : **\n- Avoir effectuer 15 recrutement ({28-data['recruteur']} restant)"
        elif jobs['MRecruteur'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de recruteur, du pôle __recrutement__ 🟪 consiste a accueillir les nouveaux arrivants, les formés et s'assurée de leurs intégration dans le pays.*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant : **\nConditions a venir"

    if selected_job == 4:   # Animateur
        metier_name = "Animateur"
        embed.color = Color.green()
        if jobs['MAnimateur'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier d'animateur, du pôle __animation__ 🟩 consiste a organiser divers event sur des plateformes extérieur a NationsGlory (discord, jeu en ligne, minecraft et bien plus).*\n\n**Condition pour rejoindre : **\n- Motivation\n- Être Joueur {config['emoji_1']}\n- Être au minimum <@&{config['roles']['grades']['recrue_confirme']}>"
        if jobs['MAnimateur'] == 0:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905019160989796/Animateur0.png")
            text += f"*Le métier d'animateur, du pôle __animation__ 🟩 consiste a organiser divers event sur des plateformes extérieur a NationsGlory (discord, jeu en ligne, minecraft et bien plus).*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant :**\n- Avoir effectuer 3 animations ({3-data['animateur']} restant)"
        elif jobs['MAnimateur'] == 1:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905019475574804/Animateur1.png")
            text += f"*Le métier d'animateur, du pôle __animation__ 🟩 consiste a organiser divers event sur des plateformes extérieur a NationsGlory (discord, jeu en ligne, minecraft et bien plus).*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant :**\n- Avoir effectuer 5 animations ({8-data['animateur']} restant)"
        elif jobs['MAnimateur'] == 2:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905019773374555/Animateur2.png")
            text += f"*Le métier d'animateur, du pôle __animation__ 🟩 consiste a organiser divers event sur des plateformes extérieur a NationsGlory (discord, jeu en ligne, minecraft et bien plus).*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant :**\n- Avoir effectuer 10 animations ({18-data['animateur']} restant)"
        elif jobs['MAnimateur'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier d'animateur, du pôle __animation__ 🟩 consiste a organiser divers event sur des plateformes extérieur a NationsGlory (discord, jeu en ligne, minecraft et bien plus).*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant :**\n- Conditions a venir"

    if selected_job == 5:   # Joueur
        metier_name = "Joueur"
        embed.color = Color.green()
        if jobs['MJoueur'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de joueur, du pôle __animation__ 🟩 consiste a participer aux events organiser par le pôle. La participation mais aussi les victoires (quand possible) et belle actions, permette d'Up ce métier.*\n\n**Condition pour rejoindre : **\n- Aucunes"
            can_join = 1
        if jobs['MJoueur'] == 0:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de joueur, du pôle __animation__ 🟩 consiste a participer aux events organiser par le pôle. La participation mais aussi les victoires (quand possible) et belle actions, permette d'Up ce métier.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant :**\n- Avoir 10.000pts ({10000-data['joueur']} restant)"
        elif jobs['MJoueur'] == 1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de joueur, du pôle __animation__ 🟩 consiste a participer aux events organiser par le pôle. La participation mais aussi les victoires (quand possible) et belle actions, permette d'Up ce métier.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant :**\n- Avoir 10.000pts ({10000-data['joueur']} restant)"
        elif jobs['MJoueur'] == 2:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de joueur, du pôle __animation__ 🟩 consiste a participer aux events organiser par le pôle. La participation mais aussi les victoires (quand possible) et belle actions, permette d'Up ce métier.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant :**\n- Avoir 10.000pts ({10000-data['joueur']} restant)"
        elif jobs['MJoueur'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de joueur, du pôle __animation__ 🟩 consiste a participer aux events organiser par le pôle. La participation mais aussi les victoires (quand possible) et belle actions, permette d'Up ce métier.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant :**\n- Conditions a venir"

    if selected_job == 6:   # Builder
        metier_name = "Builder"
        embed.color = Color.orange()
        if jobs['MBuilder'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de builder, du pôle __build__ 🟦 consiste a réaliser les différents schématiques du pays en créatifs, qui seront ensuite poser InGame par les constructeurs.*\n\n**Condition pour rejoindre : **\n- Maîtriser Schématica et WorldEdit\n- Être motiver\n- Savoir bien build dans le thème de la GDE (et d'une manière général)\n- Être au minimum <@&{config['roles']['grades']['recrue_confirme']}>\n- Être constructeur {config['emoji_1']}"
            if data['grade'] >= 2:
                can_join = 1
        if jobs['MBuilder'] == 0:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905020087931010/Builder0.png")
            text += f"*Le métier de builder, du pôle __build__ 🟦 consiste a réaliser les différents schématiques du pays en créatifs, qui seront ensuite poser InGame par les constructeurs.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant :**\n- Avoir réaliser 1 construction ({1-data['builder']} restant)"
        elif jobs['MBuilder'] == 1:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905020419293324/Builder1.png")
            text += f"*Le métier de builder, du pôle __build__ 🟦 consiste a réaliser les différents schématiques du pays en créatifs, qui seront ensuite poser InGame par les constructeurs.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant :**\n- Avoir réaliser 5 construction ({6-data['builder']} restant)"
        elif jobs['MBuilder'] == 2:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905021631451187/Builder2.png")
            text += f"*Le métier de builder, du pôle __build__ 🟦 consiste a réaliser les différents schématiques du pays en créatifs, qui seront ensuite poser InGame par les constructeurs.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant :**\n- Avoir réaliser 10 construction ({16-data['builder']} restant)"
        elif jobs['MBuilder'] == 3:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905021950201866/Builder3.png")
            text += f"*Le métier de builder, du pôle __build__ 🟦 consiste a réaliser les différents schématiques du pays en créatifs, qui seront ensuite poser InGame par les constructeurs.*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant :**\n- Conditions a venir"

    if selected_job == 7:   # Constructeur
        metier_name = "Constructeur"
        embed.color = Color.orange()
        if jobs['MConstructeur'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de constructeur, du pôle __build__ 🟦 consiste a posées les différents schématiques du pays réaliser par les builders.*\n\n**Condition pour rejoindre : **\n- Aucunes"
            can_join = 1
        if jobs['MConstructeur'] == 0:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de constructeur, du pôle __build__ 🟦 consiste a posées les différents schématiques du pays réaliser par les builders.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant :**\n- Avoir contribuer a la pose de 3 construction ({3-data['builder']} restant)"
        elif jobs['MConstructeur'] == 1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de constructeur, du pôle __build__ 🟦 consiste a posées les différents schématiques du pays réaliser par les builders.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant :**\n- Avoir contribuer a la pose de 5 construction ({8-data['builder']} restant)"
        elif jobs['MConstructeur'] == 2:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de constructeur, du pôle __build__ 🟦 consiste a posées les différents schématiques du pays réaliser par les builders.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant :**\n- Avoir contribuer a la pose de 15 construction ({23-data['builder']} restant)"
        elif jobs['MConstructeur'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de constructeur, du pôle __build__ 🟦 consiste a posées les différents schématiques du pays réaliser par les builders.*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant :**\n- Conditions a venir"

    if selected_job == 8:   # Directeur
        metier_name = "Directeur"
        embed.color = Color.yellow()
        if jobs['MDirecteur'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de directeur, du pôle __économique__ 🟨 consiste a gérer un projet économique qui emploi des membres du pays et permet ainsi de faire tournée l'économie du pays.*\n\n**Condition pour rejoindre : **\n- Être Farmer {config['emoji_2']} __ou__ être Économiste {config['emoji_2']}\n- Être au minimum <@&{config['roles']['grades']['membre']}>"
            if data['grade'] >= 3:
                can_join = 1
        if jobs['MDirecteur'] == 0:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de directeur, du pôle __économique__ 🟨 consiste a gérer un projet économique qui emploi des membres du pays et permet ainsi de faire tournée l'économie du pays.*\n\n**Level actuel :** {config['emoji_0']}\n\n**Level suivant :**\n- Conditions a venir"
        elif jobs['MDirecteur'] == 1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de directeur, du pôle __économique__ 🟨 consiste a gérer un projet économique qui emploi des membres du pays et permet ainsi de faire tournée l'économie du pays.*\n\n**Level actuel :** {config['emoji_1']}\n\n**Level suivant :**\n- Conditions a venir"
        elif jobs['MDirecteur'] == 2:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de directeur, du pôle __économique__ 🟨 consiste a gérer un projet économique qui emploi des membres du pays et permet ainsi de faire tournée l'économie du pays.*\n\n**Level actuel :** {config['emoji_2']}\n\n**Level suivant :**\n- Conditions a venir"
        elif jobs['MDirecteur'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier de directeur, du pôle __économique__ 🟨 consiste a gérer un projet économique qui emploi des membres du pays et permet ainsi de faire tournée l'économie du pays.*\n\n**Level actuel :** {config['emoji_3']}\n\n**Level suivant :**\n- Conditions a venir"

    if selected_job == 9:   # Économiste
        metier_name = "Économiste"
        embed.color = Color.yellow()
        if jobs['MÉconomiste'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            text += f"*Le métier d'économiste, du pôle __économique__ 🟨 consiste a crée des tutoriels de farmings sur les ressources rentables du moment et ainsi permettre au joueurs encore novice du pays de farmer efficacement.*\n\n**Condition pour rejoindre : **\n- Être Farmer {config['emoji_1']}\n- Être au minimum <@&{config['roles']['grades']['recrue_confirme']}>"
            if data['grade'] >= 2:
                can_join = 1
        if jobs['MÉconomiste'] == 0:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
        elif jobs['MÉconomiste'] == 1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
        elif jobs['MÉconomiste'] == 2:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
        elif jobs['MÉconomiste'] == 3:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")

    if selected_job == 10:   # Farmer
        metier_name = "Farmer"
        embed.color = Color.yellow()
        if jobs['MFarmer'] == -1:
            embed.set_thumbnail(url="https://discord.com/assets/e4ec7c5d7af5342f57347c9ada429fba.gif")
            can_join = 1
        if jobs['MFarmer'] == 0:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905018049515670/Farmer0.png")
        elif jobs['MFarmer'] == 1:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905036173094952/Farmer1.png")
        elif jobs['MFarmer'] == 2:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905036567347210/Farmer2.png")
        elif jobs['MFarmer'] == 3:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962037953314578482/1050905036957421621/Farmer3.png")

    embed.add_field(name=f'{"}"}==============={"{"} Métier : {metier_name} {"}"}==============={"{"}', value=f"{text}", inline=False)

    return embed, can_join


class Rank(commands.Cog):
    def __init__(self, bot: GuyaBot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------
    #                               Command /player-info
    # ------------------------------------------------------------------------------------------

    @commands.slash_command(name="player-info", description="Donne toute les informations publique sur une personne")
    async def player_info(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur.", required=False)):
        if user is None:
            user = ctx.user

        embed = None
        try:
            embed, jobs, data = player_info_main_part(self.bot, user, ctx)
        except TypeError:
            pass
        if embed is None:
            await ctx.respond("Utilisateur absent de la base de données")
            return

        embed = player_info_rank_part(data, embed, jobs)

        await ctx.respond(embed=embed, view=PlayerInfoJobsButton(self.bot))
        # if jobs['vect_image']:
        #     merge_image(jobs['vect_image'])
        #     job_picture = discord.File("images/job_picture.png", filename="job_picture.png")
        #     await ctx.send(file=job_picture)

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

    # ------------------------------------------------------------------------------------------
    #                                   Command /rank
    # ------------------------------------------------------------------------------------------
    @commands.slash_command(description="Permet de rank une personne.", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
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
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["recrue_confirme"]))
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["grades"]["nouvelle_recrue"]))
            await ctx.respond(f"{user.mention} est passé Recrue confirmé")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Recrue confirmé. 🎉")
            cur.execute("UPDATE recrutement SET grade = 2 WHERE id_discord=?", [user.id])
            grade = "Recrue+"
        elif data == 2:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre. 🎉")
            cur.execute("UPDATE recrutement SET grade = 3 WHERE id_discord=?", [user.id])
            grade = "Membre"
        elif data == 3:
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre confirmé")
            await channel_gg.send(f"Félicitaion à {user.mention} qui passe Membre confirmé. 🎉")
            cur.execute("UPDATE recrutement SET grade = 4 WHERE id_discord=?", [user.id])
            grade = "Membre+"
        elif data == 4:
            if not ctx.user.get_role(config["roles"]["grades"]["gouverneur"]):
                await ctx.respond("Seul un gouverneur ou le leader peu rank un membre confirmé Officier.")
                return
            else:
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["officier"]))
                try:
                    await member_secondary_guild.add_roles(secondary_guild.get_role(config["roles"]["grades"]["officier_sec"]))
                except AttributeError:
                    pass
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["grades"]["deco_hauts_grade"]))
                await ctx.respond(f"{user.mention} est passé Officier")
                await channel_gg.send(f"Félicitaion à {user.mention} qui passe Officier. 🎉")
                cur.execute("UPDATE recrutement SET grade = 5 WHERE id_discord=?", [user.id])
                grade = "Officier"
        elif data == 5:
            if not ctx.user.get_role(config["roles"]["grades"]["second"]):
                await ctx.respond("Seul le leader pour ajouté de nouveau gouverneurs <3")
                return
            else:
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["Gouverneur"]))
                await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["deco_dieu"]))
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

    # ------------------------------------------------------------------------------------------
    #                                   Command /unrank
    # ------------------------------------------------------------------------------------------
    @commands.slash_command(description="Permet de unrank une personne.", default_permission=False)
    @commands.has_any_role(config["roles"]["grades"]["officier"])
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
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["grades"]["recrue_confirme"]))
            await member_principal_guild.add_roles(principal_guild.get_role(config["roles"]["grades"]["nouvelle_recrue"]))
            await ctx.respond(f"{user.mention} est passé recrue")
            cur.execute("UPDATE recrutement SET grade = 1 WHERE id_discord=?", [user.id])
            grade = "Recrue"
        elif data == 3:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["grades"]["membre"]))
            await ctx.respond(f"{user.mention} est passé Recrue+")
            cur.execute("UPDATE recrutement SET grade = 2 WHERE id_discord=?", [user.id])
            grade = "Recrue+"
        elif data == 4:
            await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["grades"]["membre_confirme"]))
            await ctx.respond(f"{user.mention} est passé Membre")
            cur.execute("UPDATE recrutement SET grade = 3 WHERE id_discord=?", [user.id])
            grade = "Membre"
        elif data == 5:
            if not ctx.user.get_role(config["roles"]["grades"]["Gouverneur"]) and not ctx.user.get_role(config["roles"]["grades"]["gouverneur_sec"]):
                await ctx.respond("Seul un Gouverneur ou le leader peu unrank un Officier membre confirmé .")
                return
            else:
                await member_principal_guild.remove_roles(principal_guild.get_role(config["roles"]["grades"]["officier"]))
                try:
                    await member_secondary_guild.remove_roles(secondary_guild.get_role(config["roles"]["grades"]["officier_sec"]))
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

    # ------------------------------------------------------------------------------------------
    #                                   Command /condition
    # ------------------------------------------------------------------------------------------
    @commands.slash_command(description="Modifies les données de rank d'un joueur.", default_permission=True)
    async def condition(self, ctx: discord.ApplicationContext, user: Option(discord.User, "Entre un utilisateur."), donnees: Option(str, "Condition a valider.", choices=["house", "donations", "constructions", "double compte", "participation animation", "créer animation", "recrutement"]), valeur: Option(int, "Entre une valeur.", required=True)):
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
            if member_principal_guild.get_role(config["roles"]["grades"]["officier"]):
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
            if member_principal_guild.get_role(config["roles"]["grades"]["officier"]):
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

    # ------------------------------------------------------------------------------------------
    #                                   Command /absence
    # ------------------------------------------------------------------------------------------
    @commands.slash_command(description="Pour noté l'absence de quelqu'un")
    @commands.has_any_role(config["roles"]["jobs"]["recruteur"])
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


    # ------------------------------------------------------------------------------------------
    #                               player-info buttons
    # ------------------------------------------------------------------------------------------
class PlayerInfoJobsButton(View):
    def __init__(self, bot: GuyaBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Farmer", style=discord.ButtonStyle.secondary, emoji="⏪", custom_id="button-right", disabled=True)
    async def right_button_callback(self, button, interaction):
        button_left = [x for x in self.children if x.custom_id == "button-left"][0]
        button_join = [x for x in self.children if x.custom_id == "button-candidater"][0]
        button_join.disabled = False

        if button.label == "Farmer":
            button.label = "Économiste"
            button_left.label = "Soldat"
            button_join.label = "Rejoindre"
            selected_job = 10
        elif button.label == "Économiste":
            button.label = "Directeur"
            button_left.label = "Farmer"
            button_join.label = "Candidater"
            selected_job = 9
        elif button.label == "Directeur":
            button.label = "Constructeur"
            button_left.label = "Économiste"
            button_join.label = "Candidater"
            selected_job = 8
        elif button.label == "Constructeur":
            button.label = "Builder"
            button_left.label = "Directeur"
            button_join.label = "Rejoindre"
            selected_job = 7
        elif button.label == "Builder":
            button.label = "Joueur"
            button_left.label = "Constructeur"
            button_join.label = "Candidater"
            selected_job = 6
        elif button.label == "Joueur":
            button.label = "Animateur"
            button_left.label = "Builder"
            button_join.label = "Rejoindre"
            selected_job = 5
        elif button.label == "Animateur":
            button.label = "Recruteur"
            button_left.label = "Joueur"
            button_join.label = "Candidater"
            selected_job = 4
        elif button.label == "Recruteur":
            button.label = "Journaliste"
            button_left.label = "Animateur"
            button_join.label = "Candidater"
            selected_job = 3
        elif button.label == "Journaliste":
            button.label = "Soldat"
            button_left.label = "Recruteur"
            button_join.label = "Candidater"
            selected_job = 2
        elif button.label == "Soldat":
            button.label = "Farmer"
            button_left.label = "Journaliste"
            button_join.label = "Candidater"
            selected_job = 1

        # msg = interaction.response.edit_message
        # TODO: Interactive user
        user = interaction.guild.get_member(472786888378286081)
        ctx = None
        embed, jobs, data = player_info_main_part(self.bot, user, ctx)
        embed, can_join = player_info_jobs_part(embed, jobs, selected_job, data)

        if can_join == 0:
            button_join.disabled = True
        elif can_join == 1:
            button_join.disabled = False
        else:
            button_join.label = "*Bientôt...*"
            button_join.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Métiers", style=discord.ButtonStyle.secondary, emoji="📑", custom_id="button-jobs")
    async def jobs_button_callback(self, button, interaction):
        button_right = [x for x in self.children if x.custom_id == "button-right"][0]
        button_left = [x for x in self.children if x.custom_id == "button-left"][0]
        button_candidater = [x for x in self.children if x.custom_id == "button-candidater"][0]

        if button.label == "Métiers":
            button.label = "Rank-up"
            button_right.disabled = False
            button_left.disabled = False

            # TODO: Interactive user
            user = interaction.guild.get_member(472786888378286081)
            ctx = None

            embed, jobs, data = player_info_main_part(self.bot, user, ctx)

            text = ""
            if jobs["MSoldat"] == 0:
                text += "\n**⬛Soldat :** ⬡⬡⬡"
            if jobs["MSoldat"] == 1:
                text += "\n**⬛Soldat :** ⬢⬡⬡"
            elif jobs["MSoldat"] == 2:
                text += "\n**⬛Soldat :** ⬢⬢⬡"
            elif jobs["MSoldat"] == 3:
                text += "\n**⬛Soldat :** ⬢⬢⬢"

            if jobs["MJournaliste"] == 0:
                text += "\n**🟦Journaliste :** ⬡⬡⬡"
            if jobs["MJournaliste"] == 1:
                text += "\n**🟦Journaliste :** ⬢⬡⬡"
            elif jobs["MJournaliste"] == 2:
                text += "\n**🟦Journaliste :** ⬢⬢⬡"
            elif jobs["MJournaliste"] == 3:
                text += "\n**🟦Journaliste :** ⬢⬢⬢"

            if jobs["MRecruteur"] == 0:
                text += "\n**🟪Recruteur :** ⬡⬡⬡"
            if jobs["MRecruteur"] == 1:
                text += "\n**🟪Recruteur :** ⬢⬡⬡"
            elif jobs["MRecruteur"] == 2:
                text += "\n**🟪Recruteur :** ⬢⬢⬡"
            elif jobs["MRecruteur"] == 3:
                text += "\n**🟪Recruteur :** ⬢⬢⬢"

            if jobs["MAnimateur"] == 0:
                text += "\n**🟩Animateur :** ⬡⬡⬡"
            if jobs["MAnimateur"] == 1:
                text += "\n**🟩Animateur :** ⬢⬡⬡"
            elif jobs["MAnimateur"] == 2:
                text += "\n**🟩Animateur :** ⬢⬢⬡"
            elif jobs["MAnimateur"] == 3:
                text += "\n**🟩Animateur :** ⬢⬢⬢"

            if jobs["MJoueur"] == 0:
                text += "\n**🟩Joueur :** ⬡⬡⬡"
            if jobs["MJoueur"] == 1:
                text += "\n**🟩Joueur :** ⬢⬡⬡"
            elif jobs["MJoueur"] == 2:
                text += "\n**🟩Joueur :** ⬢⬢⬡"
            elif jobs["MJoueur"] == 3:
                text += "\n**🟩Joueur :** ⬢⬢⬢"

            if jobs["MBuilder"] == 0:
                text += "\n**🟧Builder :** ⬡⬡⬡"
            if jobs["MBuilder"] == 1:
                text += "\n**🟧Builder :** ⬢⬡⬡"
            elif jobs["MBuilder"] == 2:
                text += "\n**🟧Builder :** ⬢⬢⬡"
            elif jobs["MBuilder"] == 3:
                text += "\n**🟧Builder :** ⬢⬢⬢"

            if jobs["MConstructeur"] == 0:
                text += "\n**🟧Constructeur :** ⬡⬡⬡"
            if jobs["MConstructeur"] == 1:
                text += "\n**🟧Constructeur :** ⬢⬡⬡"
            elif jobs["MConstructeur"] == 2:
                text += "\n**🟧Constructeur :** ⬢⬢⬡"
            elif jobs["MConstructeur"] == 3:
                text += "\n**🟧Constructeur :** ⬢⬢⬢"

            if jobs["MDirecteur"] == 0:
                text += "\n**🟨Directeur :** ⬡⬡⬡"
            if jobs["MDirecteur"] == 1:
                text += "\n**🟨Directeur :** ⬢⬡⬡"
            elif jobs["MDirecteur"] == 2:
                text += "\n**🟨Directeur :** ⬢⬢⬡"
            elif jobs["MDirecteur"] == 3:
                text += "\n**🟨Directeur :** ⬢⬢⬢"

            if jobs["MÉconomiste"] == 0:
                text += "\n**🟨Économiste :** ⬡⬡⬡"
            if jobs["MÉconomiste"] == 1:
                text += "\n**🟨Économiste :** ⬢⬡⬡"
            elif jobs["MÉconomiste"] == 2:
                text += "\n**🟨Économiste :** ⬢⬢⬡"
            elif jobs["MÉconomiste"] == 3:
                text += "\n**🟨Économiste :** ⬢⬢⬢"

            if jobs["MFarmer"] == 0:
                text += "\n**🟨Farmer :** ⬡⬡⬡"
            if jobs["MFarmer"] == 1:
                text += "\n**🟨Farmer :** ⬢⬡⬡"
            elif jobs["MFarmer"] == 2:
                text += "\n**🟨Farmer :** ⬢⬢⬡"
            elif jobs["MFarmer"] == 3:
                text += "\n**🟨Farmer :** ⬢⬢⬢"

            if text == "":
                text += "Tu n'a pas encore rejoint de métier, appuis sur le bouton \"candidater\" ou \"rejoindre\" pour en rejoindre un !"

            embed.add_field(name="}==============={ Liste de tes métiers }==============={", value=f"{text}", inline=False)

        elif button.label == "Rank-up":
            button.label = "Métiers"
            button_right.disabled = True
            button_left.disabled = True
            button_candidater.disabled = True

            # TODO: Interactive user
            user = interaction.guild.get_member(472786888378286081)
            ctx = None
            embed, jobs, data = player_info_main_part(self.bot, user, ctx)
            embed = player_info_rank_part(data, embed, jobs)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Soldat", style=discord.ButtonStyle.secondary, emoji="⏩", custom_id="button-left", disabled=True)
    async def left_button_callback(self, button, interaction):
        button_right = [x for x in self.children if x.custom_id == "button-right"][0]
        button_join = [x for x in self.children if x.custom_id == "button-candidater"][0]
        button_join.disabled = False

        if button.label == "Journaliste":
            button.label = "Recruteur"
            button_right.label = "Soldat"
            button_join.label = "Candidater"
            selected_job = 2
        elif button.label == "Recruteur":
            button.label = "Animateur"
            button_right.label = "Journaliste"
            button_join.label = "Candidater"
            selected_job = 3
        elif button.label == "Animateur":
            button.label = "Joueur"
            button_right.label = "Recruteur"
            button_join.label = "Candidater"
            selected_job = 4
        elif button.label == "Joueur":
            button.label = "Builder"
            button_right.label = "Animateur"
            button_join.label = "Rejoindre"
            selected_job = 5
        elif button.label == "Builder":
            button.label = "Constructeur"
            button_right.label = "Joueur"
            button_join.label = "Candidater"
            selected_job = 6
        elif button.label == "Constructeur":
            button.label = "Directeur"
            button_right.label = "Builder"
            button_join.label = "Rejoindre"
            selected_job = 7
        elif button.label == "Directeur":
            button.label = "Économiste"
            button_right.label = "Constructeur"
            button_join.label = "Candidater"
            selected_job = 8
        elif button.label == "Économiste":
            button.label = "Farmer"
            button_right.label = "Directeur"
            button_join.label = "Candidater"
            selected_job = 9
        elif button.label == "Farmer":
            button.label = "Soldat"
            button_right.label = "Économiste"
            button_join.label = "Rejoindre"
            selected_job = 10
        elif button.label == "Soldat":
            button.label = "Journaliste"
            button_right.label = "Farmer"
            selected_job = 1

        # TODO: Interactive user
        user = interaction.guild.get_member(472786888378286081)
        ctx = None
        embed, jobs, data = player_info_main_part(self.bot, user, ctx)
        embed, can_join = player_info_jobs_part(embed, jobs, selected_job, data)

        if can_join:
            button_join.disabled = False
        else:
            button_join.label = "Tu ne remplis pas les conditions"
            button_join.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Candidater", style=discord.ButtonStyle.green, emoji="👔", custom_id="button-candidater", disabled=True)
    async def candidater_button_callback(self, button, interaction):
        await interaction.response.edit_message(view=self)
