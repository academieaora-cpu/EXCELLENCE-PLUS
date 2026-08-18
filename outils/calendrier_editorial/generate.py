#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère le calendrier éditorial Excellence+ — v3, arbitrages du 30/07/2026,
jours/heures ajustés le 02/08/2026, ouverture des canaux revue le 18/08/2026.

⚠️ SUPERSÉDÉ LE 18/08/2026 — ce générateur produit une architecture HTML
(window.ENTRIES/WEEKS + template.html) différente de celle qui est actuellement
dans rapports/calendrier_editorial_excellence_plus.html (fiches <details>,
statuts cliquables). Le relancer n'actualise PAS le fichier courant, il le
remplacerait par l'ancienne architecture. Voir README.md du dossier.

Règles appliquées (source : config/creneaux.json, qui fait foi) :
  · 6 mois — août 2026 → janvier 2027 (janvier réintégré au programme)
  · 3 publications par semaine par canal prioritaire (Facebook, WhatsApp,
    Instagram — même jour/heure/pilier), TikTok en plus (~1×/mois, vidéo
    source déjà disponible) — lundi 06h00 · mercredi 12h00 · samedi 06h00 WAT
  · Les 4 canaux prioritaires sont ouverts SIMULTANÉMENT dès le lancement
    (18/08/2026 — remplace l'ouverture progressive du 30/07/2026)
  · Ciblage : Yaoundé dans son ensemble, plus le premium exclusif
  · Aucune campagne Meta Ads au mois 1 (août)
  · Piliers 40 / 35 / 25 mesurés sur la période entière

Ce générateur produit le PLAN (date, canal, pilier, angle). Le texte de chaque
publication est rédigé ensuite, publication par publication, et passe par le
circuit BAT/BAP. Un calendrier n'est pas un stock de textes.
"""
import codecs
import datetime
import json
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ICI, "data")
REPO_ROOT = os.path.join(ICI, "..", "..")
CONFIG = os.path.join(ICI, "..", "..", "config", "creneaux.json")
os.makedirs(DATA, exist_ok=True)

AUT, MET, PRE = "autorité_éducative", "methode_excellence", "la_preuve"

FR_JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
FR_MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
FR_MOIS_COURT = ["", "jan", "fév", "mar", "avr", "mai", "juin",
                 "juil", "aoû", "sep", "oct", "nov", "déc"]

# Index des jours ISO utilisés par les créneaux (lundi = 0)
JOUR_INDEX = {nom: i for i, nom in enumerate(FR_JOURS)}


def fr_date(d):
    return "%d %s %d" % (d.day, FR_MOIS[d.month], d.year)


def fr_date_court(d):
    return "%d %s" % (d.day, FR_MOIS_COURT[d.month])


def mois_id(d):
    return "%04d-%02d" % (d.year, d.month)


def charger_config():
    with codecs.open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Référentiels d'affichage
# ---------------------------------------------------------------------------
PLATFORMS = [
    {"id": "facebook", "nom": "Facebook", "icone": "\U0001F4D8", "couleur": "#1877F2"},
    {"id": "whatsapp", "nom": "WhatsApp", "icone": "\U0001F4AC", "couleur": "#25D366"},
    {"id": "instagram", "nom": "Instagram", "icone": "\U0001F4F8", "couleur": "#E1306C"},
    {"id": "tiktok", "nom": "TikTok", "icone": "\U0001F3B5", "couleur": "#010101"},
]

PILLARS = [
    {"id": AUT, "nom": "Autorité", "nom_long": "Autorité éducative",
     "couleur": "#C2570F", "part": 40, "phare": True},
    {"id": MET, "nom": "Méthode", "nom_long": "La méthode Excellence+",
     "couleur": "#1B2D5C", "part": 35, "phare": False},
    {"id": PRE, "nom": "Preuve", "nom_long": "La preuve",
     "couleur": "#1B6B3C", "part": 25, "phare": False},
]
PILIER_PAR_NUM = {1: AUT, 2: MET, 3: PRE}

STATUTS = [
    {"id": "a_rediger", "label": "À rédiger", "couleur": "#9CA0A8"},
    {"id": "bat_envoye", "label": "BAT envoyé", "couleur": "#F37021"},
    {"id": "bat_valide", "label": "BAT validé", "couleur": "#3B82C4"},
    {"id": "bap_recu", "label": "BAP reçu", "couleur": "#1B6B3C"},
    {"id": "publie", "label": "Publié", "couleur": "#22C55E"},
]

COULEUR_MOIS = {
    "2026-08": "#F37021", "2026-09": "#C0392B", "2026-10": "#27AE60",
    "2026-11": "#142850", "2026-12": "#D4AC0D", "2027-01": "#1B6B3C",
}

INTERDITS_NOTE = (
    "Ne jamais écrire « Excellence++ » (nom exact : Excellence+) · "
    "ne jamais mentionner le nombre d'enseignants · ne jamais nommer un concurrent · "
    "ne jamais promettre la réussite — Excellence+ la mesure et la montre · "
    "ne jamais chiffrer un tarif publiquement · "
    "ne jamais laisser penser que le service est réservé aux quartiers aisés · "
    "ne jamais publier sans BAP écrit reçu par email (bap_recu_le ET bap_email_ref) · "
    "vocal ou message WhatsApp jamais accepté comme BAP · "
    "ne jamais publier un mineur identifiable sans autorisation parentale archivée."
)

# ---------------------------------------------------------------------------
# ANGLES par mois et par pilier.
# Chaque mois a son thème ; chaque pilier y trouve sa déclinaison. Les angles
# restent des intentions éditoriales — le texte final est rédigé au moment du
# BAT, pas ici.
# ---------------------------------------------------------------------------
ANGLES = {
    "2026-08": {  # Fondation et preuve
        AUT: [
            "Préparer la rentrée : trois gestes à commencer maintenant",
            "Reprendre le rythme avant la reprise, pas après",
            "Ce qu'un parent peut vérifier avant de choisir un accompagnement",
            "Organiser le travail à la maison sans transformer le salon en salle de classe",
            "Les questions à poser avant de confier son enfant à quelqu'un",
        ],
        MET: [
            "Comment Excellence+ sélectionne et suit ses enseignants",
            "Ce qui se passe pendant une séance à domicile",
            "Le rôle de l'encadreur — ce que personne ne voit",
            "Le bilan séquentiel : à quoi ça sert, ce qu'on y lit",
            "Disponible de 06h à 24h — pourquoi cette amplitude",
        ],
        PRE: [
            "93 % puis 97 % — deux ans, deux chiffres vérifiables",
            "Un bulletin avant, un bulletin après",
            "Ce qu'une famille accompagnée depuis deux ans en dit",
            "Des résultats qu'on mesure et qu'on montre",
        ],
    },
    "2026-09": {  # La rentrée
        AUT: [
            "Première semaine : les trois signaux qui comptent",
            "Un enfant qui décroche ne le dit pas — il le montre",
            "Les quinze premiers jours décident du trimestre",
            "Classes d'examen : ce qui change cette année",
            "Aider sans faire à sa place",
        ],
        MET: [
            "Comment on construit un plan de travail en début d'année",
            "Le premier rendez-vous avec une nouvelle famille",
            "Adapter le rythme à l'élève, pas l'inverse",
            "Suivre la progression semaine après semaine",
            "Ce qu'on demande à un enseignant avant sa première séance",
        ],
        PRE: [
            "Une rentrée réussie, racontée par une famille de Yaoundé",
            "Du CM2 aux classes d'examen — le parcours d'un élève suivi",
            "Ce qui a changé après un trimestre d'accompagnement",
            "Témoignage : passer d'un bulletin subi à un bulletin choisi",
        ],
    },
    "2026-10": {  # La méthode au quotidien
        AUT: [
            "Réviser efficacement : ce qui marche vraiment",
            "Le mi-trimestre, moment idéal pour corriger le tir",
            "Gérer la fatigue scolaire sans relâcher",
            "Devoirs du soir : combien de temps, à quelle heure",
            "Quand faut-il s'inquiéter d'une note en baisse",
        ],
        MET: [
            "Une journée d'encadreur, du matin au soir",
            "Comment on corrige une méthode qui ne fonctionne pas",
            "Portrait d'enseignant : pourquoi il fait ce métier",
            "Coulisses d'un suivi terrain à Yaoundé",
            "La communication parent-enseignant-encadreur, en pratique",
        ],
        PRE: [
            "Trois mois d'accompagnement, ce qui a bougé",
            "Un élève, une progression, des preuves",
            "Ce que les parents disent après un trimestre",
            "Avant / après : lire une progression réelle",
        ],
    },
    "2026-11": {  # Autorité éducative
        AUT: [
            "Préparer les examens de fin de trimestre",
            "Méthode de révision intensive : la construire, pas l'improviser",
            "Le premier bulletin 2026-2027 : comment le lire",
            "Stress d'examen : ce qui aide, ce qui aggrave",
            "Choisir ses priorités quand tout semble urgent",
            "Le sommeil, variable oubliée de la réussite scolaire",
        ],
        MET: [
            "Comment on prépare un élève à une classe d'examen",
            "Réajuster un accompagnement en cours d'année",
            "Ce qu'on mesure chez un élève, et pourquoi",
            "Travailler avec les familles, pas seulement pour elles",
        ],
        PRE: [
            "Mention Très Bien au BEPC — le chemin, pas seulement le résultat",
            "Ce qu'un trimestre d'écart produit sur un bulletin",
            "Témoignage d'un élève de classe d'examen",
        ],
    },
    "2026-12": {  # Bilan et cap
        AUT: [
            "Faire le point à mi-parcours de l'année scolaire",
            "Les vacances de fin d'année : repos ou révision ?",
            "Préparer le second trimestre pendant les congés",
            "Ce qu'on attend d'un enfant après un premier trimestre",
        ],
        MET: [
            "Six mois d'accompagnement — ce que la méthode a corrigé",
            "Comment on prépare la reprise de janvier",
            "Bilan séquentiel de fin de trimestre : ce qu'il contient",
            "Ce que l'équipe retient de ce premier trimestre",
        ],
        PRE: [
            "Bilan mi-annuel : les résultats de la période",
            "Merci aux familles qui nous ont fait confiance",
            "Ce qu'une année d'accompagnement change concrètement",
        ],
    },
    "2027-01": {  # Nouvel élan
        AUT: [
            "Reprendre après les congés sans tout recommencer",
            "Second trimestre : le moment où l'écart se creuse ou se comble",
            "Fixer des objectifs tenables pour la suite de l'année",
            "Préparer les examens de fin d'année, dès janvier",
            "Ce qui distingue un élève qui progresse d'un élève qui stagne",
        ],
        MET: [
            "Nouvelle année, mêmes exigences : comment on repart",
            "Ajuster un accompagnement au second trimestre",
            "Ce qu'on met en place pour les classes d'examen",
            "Notre façon de travailler, expliquée simplement",
        ],
        PRE: [
            "Résultats du premier trimestre 2026-2027",
            "Une famille raconte son année avec Excellence+",
            "93 % puis 97 % — et la suite",
        ],
    },
}

FORMATS = {
    AUT: ["Carrousel conseil", "Post pédagogique", "Question aux parents"],
    MET: ["Coulisses", "Portrait d'enseignant", "Infographie de processus"],
    PRE: ["Témoignage", "Chiffre-clé", "Avant / après anonymisé"],
}

PILIER_NOM_LONG = {AUT: "Autorité éducative", MET: "La méthode Excellence+", PRE: "La preuve"}
TON_PAR_PILIER = {AUT: "Crédible · Proche", MET: "Rassurant · Déterminé", PRE: "Proche · Rassurant"}
# Rôle de chaque pilier — reprise directe de brand_guidelines.md §4, pas une
# reformulation libre.
PILIER_ROLE = {
    AUT: "pose Excellence+ comme référence pédagogique de confiance",
    MET: "rend visible ce qui est invisible : la rigueur du suivi terrain",
    PRE: "déclenche la décision par la preuve",
}

# ---------------------------------------------------------------------------
# Niveau 3 (fiche) — champs enrichis : objectifs, direction visuelle, contenu
# suggéré, production, validation. Générés (pas 78 entrées écrites à la
# main), mais avec assez de variation par pilier/format pour ne pas produire
# le même bloc dupliqué partout — c'est précisément ce qui rendait
# inutilisable un modèle externe reçu le 10/08/2026 (même decor/cadrage/
# ambiance recopiés sur toutes les fiches, et palette de logo au lieu de la
# palette de communication sociale).
# ---------------------------------------------------------------------------
CTA_PAR_PILIER = {
    AUT: ["Enregistrez ce post, vous en aurez besoin bientôt",
          "Posez vos questions en commentaire",
          "Partagez-le à un parent que ça concerne"],
    MET: ["Écrivez-nous sur WhatsApp pour en savoir plus",
          "Posez vos questions en commentaire, on répond sous 48h",
          "Suivez la suite en story cette semaine"],
    PRE: ["Écrivez-nous sur WhatsApp : +237 699 403 969",
          "Partagez si ce résultat vous parle",
          "Contactez-nous pour en discuter"],
}
KPI_PAR_PILIER = {
    AUT: "Enregistrements + partages",
    MET: "Commentaires + messages WhatsApp générés",
    PRE: "Partages + messages WhatsApp générés",
}
DECOR_PAR_PILIER = {
    AUT: "Intérieur familial, coin devoirs ou salon — Yaoundé",
    MET: "Séance à domicile ou coulisses de suivi terrain — Yaoundé",
    PRE: "Portrait, bulletin ou cahier en gros plan — Yaoundé",
}
CADRAGE_PAR_FORMAT = {
    "Carrousel conseil": "Carrousel 4-5 slides, une idée par slide, texte court",
    "Post pédagogique": "Plan large, espace de respiration pour le texte",
    "Question aux parents": "Cadrage simple, regard tourné vers la question posée",
    "Coulisses": "Plan rapproché sur un geste ou un visage adulte (jamais un enfant identifiable)",
    "Portrait d'enseignant": "Portrait moyen, lumière naturelle, cadre professionnel chaleureux",
    "Infographie de processus": "Schéma en étapes numérotées, peu de texte par étape",
    "Témoignage": "Citation en surimpression sur fond sobre",
    "Chiffre-clé": "Chiffre en typo Inter Black, grand format, orange sur navy",
    "Avant / après anonymisé": "Diptyque avant/après, tout élément identifiant flouté",
}
AMBIANCE_STANDARD = (
    "Navy #1B2D5C, orange #EC770D et blanc — n'importe laquelle des trois peut "
    "dominer selon le visuel, jamais de texte blanc en fond orange (voir "
    "palette_excellence.json et plateforme_marque.md §5)."
)
A_EVITER_STANDARD = (
    "Aucun visage d'enfant identifiable sans autorisation parentale archivée · "
    "aucun chiffre d'effectif enseignants · jamais « Excellence++ » · "
    "aucun tarif chiffré publiquement."
)
ELEMENTS_PAR_FORMAT = {
    "Carrousel conseil": ["Numérotation des slides", "Une idée par slide"],
    "Post pédagogique": ["Icône ou pictogramme simple"],
    "Question aux parents": ["Zone de texte pour la question posée"],
    "Coulisses": ["Geste de travail concret (cahier, correction, échange)"],
    "Portrait d'enseignant": ["Cadre professionnel", "Regard caméra"],
    "Infographie de processus": ["Étapes numérotées", "Flèches de progression"],
    "Témoignage": ["Guillemets ou cadre de citation"],
    "Chiffre-clé": ["Chiffre en grand format", "Contexte en sous-texte"],
    "Avant / après anonymisé": ["Ligne de séparation avant/après", "Éléments identifiants floutés"],
}

# Persona et étape du tunnel : dérivés du rôle documenté de chaque pilier
# (brand_guidelines.md §4 — Autorité "pose Excellence+ comme référence",
# Méthode "rend visible ce qui est invisible", Preuve "déclenche la
# décision"), pas une segmentation démographique inventée en plus de la
# cible unique déjà définie en §3.
PERSONA_PAR_PILIER = {
    AUT: "Parent d'élève à Yaoundé — repère un besoin, pas encore en recherche active",
    MET: "Parent d'élève à Yaoundé — compare les options de suivi scolaire",
    PRE: "Parent d'élève à Yaoundé — cherche une preuve avant de décider",
}
ETAPE_TUNNEL_PAR_PILIER = {AUT: "Découverte", MET: "Considération", PRE: "Décision"}

HASHTAGS_BASE = ["#ExcellencePlus", "#Yaoundé"]
HASHTAGS_PAR_MOIS = {
    "2026-08": "#Rentrée2026", "2026-09": "#Rentrée2026",
    "2026-10": "#SoutienScolaire", "2026-11": "#RéussiteScolaire",
    "2026-12": "#BilanTrimestre", "2027-01": "#NouvelÉlan",
}


def hashtags_du_mois(mid):
    return HASHTAGS_BASE + [HASHTAGS_PAR_MOIS.get(mid, "#SoutienScolaire")]


def canaux_ouverts_a(config, mid):
    """Canaux dont la date d'activation (config/creneaux.json) est atteinte
    au mois mid — depuis le 18/08/2026, les 4 canaux prioritaires (facebook,
    whatsapp, instagram, tiktok) partagent la même date d'activation
    (2026-08) : ils s'ouvrent simultanément, plus de canal seul au
    lancement. linkedin/youtube restent à null (hors périmètre)."""
    activation = (config.get("canaux") or {}).get("activation") or {}
    return [c for c, date_min in activation.items() if date_min and date_min <= mid]


def description_entry(config, mid, m, pilier, plateforme_creneau):
    noms = {"facebook": "Facebook", "whatsapp": "Chaîne WhatsApp",
            "instagram": "Instagram", "tiktok": "TikTok"}
    ouverts = [c for c in ("facebook", "whatsapp", "instagram", "tiktok")
               if c in canaux_ouverts_a(config, mid)]
    decl = ", ".join(noms[c] for c in ouverts) if ouverts else noms[plateforme_creneau]
    return (
        "Thème du mois : %s. Pilier « %s » — %s.\n"
        "Persona : %s.\n"
        "Canaux ouverts ce mois-ci selon config/creneaux.json : %s — publication "
        "réelle sur %s (seul canal avec un créneau programmé aujourd'hui) ; les "
        "autres restent une déclinaison possible une fois leur créneau ajouté."
    ) % (m["theme"], PILIER_NOM_LONG[pilier], PILIER_ROLE[pilier],
         PERSONA_PAR_PILIER[pilier], decl, noms[plateforme_creneau])


def direction_visuelle(pilier, format_, angle):
    return {
        "sujet": angle,
        "decor": DECOR_PAR_PILIER[pilier],
        "elements": ELEMENTS_PAR_FORMAT.get(format_, []),
        "cadrage": CADRAGE_PAR_FORMAT.get(format_, "Plan moyen, espace de texte pour l'accroche"),
        "ambiance": AMBIANCE_STANDARD,
        "prompt_ia": "%s — %s, Yaoundé Cameroun, lumière naturelle chaleureuse, "
                     "palette navy #1B2D5C et orange #EC770D, photoréaliste" % (
                         angle, DECOR_PAR_PILIER[pilier]),
        "references": "Cohérence avec brand_guidelines.md §7 (identité visuelle Excellence+)",
        "a_eviter": A_EVITER_STANDARD,
    }


def contenu_suggere(angle, pilier, cta, mid):
    """Amorce de brief pour le rédacteur — pas le texte final.

    generate.py ne produit que le PLAN : le corps définitif se rédige au
    moment du BAT, publication par publication (voir docstring du module).
    Ce champ donne une direction concrète, pas un texte prêt à publier.
    """
    return (
        "Accroche suggérée : %s\n\n"
        "Angle à développer au BAT : reprendre l'angle ci-dessus, ton %s, "
        "s'appuyer sur les chiffres validés (93%% en 2023-2024, 97%% en "
        "2024-2025) si pertinent pour ce pilier. Corps définitif rédigé au "
        "moment du BAT, jamais avant.\n\n"
        "CTA prévu : %s\n"
        "Hashtags suggérés : %s"
    ) % (angle, TON_PAR_PILIER[pilier], cta, " ".join(hashtags_du_mois(mid)))


def objectifs_entry(pilier, cta, kpi):
    return [
        "Nourrir le pilier « %s »" % PILIER_NOM_LONG[pilier],
        "Étape du tunnel : %s" % ETAPE_TUNNEL_PAR_PILIER[pilier],
        "CTA : %s" % cta,
        "KPI cible : %s" % kpi,
    ]


# Le front-matter des .md parle le vocabulaire SOP-001 (draft -> BAT_soumis
# -> BAP_recu -> publié -> archivé) ; l'UI de ce calendrier parle un
# vocabulaire à 5 états propre à l'outil (a_rediger/bat_envoye/bat_valide/
# bap_recu/publie) — écart déjà documenté, pas un remplacement du circuit
# officiel (voir STATUT_PROJET.md, "Conventions établies"). On traduit ici,
# on ne fait jamais comme si les deux vocabulaires étaient le même champ.
STATUT_MD_VERS_CALENDRIER = {
    "draft": "a_rediger",
    "bat_soumis": "bat_envoye",
    "bap_recu": "bap_recu",
    "publie": "publie",
    "publié": "publie",
    "archive": "publie",
    "archivé": "publie",
}


def lire_statut_reel(repo_root, plateforme, eid):
    """Statut réel d'un post, lu dans son fichier .md s'il existe déjà.

    Ne jamais fabriquer un statut « en retard » ou « bloqué » par calcul de
    date : ça ne vaut que ce que vaut la source, et la seule source fiable
    ici est le front-matter du fichier lui-même. Pas de fichier -> le post
    n'a simplement pas encore été rédigé (statut par défaut : a_rediger).
    """
    chemin = os.path.join(repo_root, "contenu", plateforme, eid + ".md")
    if not os.path.isfile(chemin):
        return "a_rediger", None
    with codecs.open(chemin, "r", encoding="utf-8") as f:
        texte = f.read()
    m = re.search(r'^statut:\s*"?([\w_]+)"?\s*$', texte, re.MULTILINE)
    bap = re.search(r'^bap_recu_le:\s*"?([^"\n]*)"?\s*$', texte, re.MULTILINE)
    brut = (m.group(1) if m else "draft").strip().lower()
    statut = STATUT_MD_VERS_CALENDRIER.get(brut, "a_rediger")
    bap_val = bap.group(1).strip() if bap else ""
    if bap_val.lower() in ("", "null", "none"):
        bap_val = None
    return statut, bap_val


# Meta Ads : aucune campagne au mois 1. Les fenêtres recommandées sont
# septembre (rentrée) et janvier (reprise) — mais rien n'est engagé : le client
# décide mois par mois, par email, 7 jours avant. Tant qu'aucune décision n'est
# reçue, la liste reste vide. Ne rien y inscrire par anticipation.
META_ADS = []


def creneaux_de_la_periode(config):
    """Développe les créneaux de config/creneaux.json sur toute la période."""
    prog = config["programme"]
    # On démarre à la première publication possible, pas au premier jour du
    # contrat : rien ne peut partir avant que la chaîne visuel → BAT → BAP soit
    # bouclée. Planifier des créneaux antérieurs reviendrait à afficher au
    # client des publications que personne ne peut produire à temps.
    debut = datetime.date.fromisoformat(
        prog.get("premiere_publication") or prog["debut"]
    )
    fin = datetime.date.fromisoformat(prog["fin"])
    grille = []
    for canal, liste in config["creneaux"].items():
        for c in liste:
            grille.append((JOUR_INDEX[c["jour"]], c["heure"], c["pilier"], canal))

    creneaux = []
    d = debut
    while d <= fin:
        for jour_idx, heure, pilier_num, canal in grille:
            if d.weekday() == jour_idx:
                creneaux.append({
                    "date": d, "heure": heure,
                    "pilier_defaut": pilier_num, "plateforme": canal,
                })
        d += datetime.timedelta(days=1)
    creneaux.sort(key=lambda c: (c["date"], c["heure"]))
    return creneaux


def repartir_piliers(creneaux):
    """Ajuste les piliers pour atteindre 40/35/25 sur la période entière.

    Le pilier par défaut du créneau (mardi=Autorité, jeudi=Méthode,
    samedi=Preuve) donne un tiers chacun. Pour atteindre la cible, on convertit
    une partie des créneaux du pilier excédentaire vers le pilier déficitaire,
    à intervalle régulier — jamais en bloc, sinon un mois entier bascule.
    """
    total = len(creneaux)
    cible = {AUT: round(total * 0.40), MET: round(total * 0.35)}
    cible[PRE] = total - cible[AUT] - cible[MET]

    for c in creneaux:
        c["pilier"] = PILIER_PAR_NUM[c["pilier_defaut"]]

    def compte(p):
        return sum(1 for c in creneaux if c["pilier"] == p)

    # Preuve est le pilier le plus faible en cible : on lui retire d'abord.
    for source in (PRE, MET):
        surplus = compte(source) - cible[source]
        if surplus <= 0:
            continue
        candidats = [c for c in creneaux if c["pilier"] == source]
        pas = max(1, len(candidats) // surplus)
        convertis = 0
        for i in range(0, len(candidats), pas):
            if convertis >= surplus:
                break
            if compte(AUT) < cible[AUT]:
                candidats[i]["pilier"] = AUT
                convertis += 1
    return creneaux


def construire_semaines(creneaux):
    semaines, vues = [], {}
    for c in creneaux:
        iso_annee, iso_sem, _ = c["date"].isocalendar()
        cle = (iso_annee, iso_sem)
        vues.setdefault(cle, []).append(c["date"])
    for (iso_annee, iso_sem), dates in sorted(vues.items()):
        lundi = min(dates) - datetime.timedelta(days=min(dates).weekday())
        dimanche = lundi + datetime.timedelta(days=6)
        semaines.append({
            "id": "S%d" % iso_sem,
            "iso_annee": iso_annee,
            "label": "Semaine %d" % iso_sem,
            "dates": "%s – %s" % (fr_date_court(lundi), fr_date(dimanche)),
            "debut_iso": lundi.isoformat(),
            "fin_iso": dimanche.isoformat(),
            "mois": mois_id(dates[len(dates) // 2]),
        })
    return semaines


def main():
    config = charger_config()
    prog = config["programme"]
    themes = config["themes_mensuels"]

    creneaux = repartir_piliers(creneaux_de_la_periode(config))

    mois_ordonnes = sorted(themes.keys())
    MONTHS = []
    for i, mid in enumerate(mois_ordonnes, start=1):
        annee, mois = int(mid[:4]), int(mid[5:])
        MONTHS.append({
            "id": mid,
            "nom": "%s %d" % (FR_MOIS[mois].capitalize(), annee),
            "sous_titre": "Mois %d — %s" % (i, themes[mid]),
            "theme": themes[mid].upper(),
            "couleur": COULEUR_MOIS.get(mid, "#1B2D5C"),
            "priorite": mid == "2026-09",  # la rentrée est le pic de l'année
        })
    MOIS_PAR_ID = {m["id"]: m for m in MONTHS}

    codes = {"facebook": "FB", "whatsapp": "WA", "instagram": "IG", "tiktok": "TT"}
    compteurs, curseurs, entrees = {}, {}, []
    aujourdhui_iso = datetime.date.today().isoformat()

    for c in creneaux:
        mid = mois_id(c["date"])
        pilier = c["pilier"]
        pool = ANGLES[mid][pilier]
        cle = (mid, pilier)
        idx = curseurs.get(cle, 0)
        curseurs[cle] = idx + 1
        angle = pool[idx % len(pool)]
        # Au-delà du premier tour dans un pool, on marque le rappel plutôt que
        # de laisser deux créneaux porter un titre identique.
        if idx >= len(pool):
            angle = "%s — angle %d" % (angle, idx // len(pool) + 1)

        code = codes[c["plateforme"]]
        n = compteurs.get(code, 0) + 1
        compteurs[code] = n
        eid = "EXC-%s-%s-%03d" % (code, c["date"].strftime("%Y"), n)

        formats = FORMATS[pilier]
        format_ = formats[idx % len(formats)]
        cta = CTA_PAR_PILIER[pilier][idx % len(CTA_PAR_PILIER[pilier])]
        kpi_cible = KPI_PAR_PILIER[pilier]
        statut_reel, bap_val = lire_statut_reel(REPO_ROOT, c["plateforme"], eid)
        m = MOIS_PAR_ID[mid]

        historique = [{"date": aujourdhui_iso, "evt": "Créneau planifié — pipeline generate.py"}]
        if bap_val:
            historique.append({"date": bap_val, "evt": "BAP reçu par email"})

        entrees.append({
            "id": eid,
            "titre": angle,
            "pilier": pilier,
            "format": format_,
            "plateforme": c["plateforme"],
            "mois": mid,
            "date": "%s · %s WAT" % (fr_date(c["date"]), c["heure"]),
            "date_iso": c["date"].isoformat(),
            "jour": FR_JOURS[c["date"].weekday()],
            "heure": c["heure"],
            "tags": [c["plateforme"], pilier],
            "favori": False,
            "statut": statut_reel,
            "meta_ads": None,
            "resume": "%s. Pilier %s — mois « %s ». Angle planifié : le texte "
                      "définitif est rédigé au moment du BAT, puis validé par "
                      "email avant publication." % (angle, PILIER_NOM_LONG[pilier], m["theme"]),
            "objectifs": objectifs_entry(pilier, cta, kpi_cible),
            "description": description_entry(config, mid, m, pilier, c["plateforme"]),
            "visuel": direction_visuelle(pilier, format_, angle),
            "contenu": contenu_suggere(angle, pilier, cta, mid),
            "production": {
                "responsable": "Claude (rédaction) → Stéphane/Laurence (validation interne) → M. NDOMMIE (BAP)",
                "delai": "%s · %s WAT" % (fr_date(c["date"]), c["heure"]),
                "dependances": [
                    "Créneau %s confirmé" % FR_JOURS[c["date"].weekday()].capitalize(),
                    "Validation interne AORA (Stéphane/Laurence)",
                    "BAP client par email (bap_recu_le)",
                ],
            },
            "validation": {"statut": statut_reel, "bap_recu_le": bap_val},
            "historique": historique,
            "notes": INTERDITS_NOTE,
        })

    semaines = construire_semaines(creneaux)
    kpi = {m["id"]: "3 publications/semaine · pilier dominant selon le créneau"
           for m in MONTHS}

    sorties = {
        "entries.json": entrees,
        "weeks.json": semaines,
        "months.json": MONTHS,
        "pillars.json": PILLARS,
        "platforms.json": PLATFORMS,
        "platforms_hors_scope.json": [],
        "statuts.json": STATUTS,
        "meta_ads.json": META_ADS,
        "kpi.json": kpi,
        "meta.json": {"genere_le": fr_date(datetime.date.today())},
    }
    for nom, obj in sorties.items():
        with codecs.open(os.path.join(DATA, nom), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

    from collections import Counter
    total = len(entrees)
    cpt = Counter(e["pilier"] for e in entrees)
    print("Période      : %s → %s (%d mois)" % (prog["debut"], prog["fin"], len(MONTHS)))
    print("Publications : %d  (3/semaine, tous canaux confondus)" % total)
    for p in (AUT, MET, PRE):
        cible = {AUT: 40, MET: 35, PRE: 25}[p]
        print("  %-22s %3d  (%.1f%%  cible %d%%)" % (p, cpt[p], 100.0 * cpt[p] / total, cible))
    print("Par plateforme :", dict(Counter(e["plateforme"] for e in entrees)))
    print("Par mois       :", dict(Counter(e["mois"] for e in entrees)))
    print("Titres uniques : %d / %d" % (len({e["titre"] for e in entrees}), total))
    print("Campagnes Meta Ads :", len(META_ADS), "(aucune au mois 1 — décision client mois par mois)")


if __name__ == "__main__":
    main()
