#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère le calendrier éditorial Excellence+ v3 — juillet-décembre 2026.
Transcrit fidèlement les posts Facebook juillet/août/septembre donnés par
l'utilisateur ; génère WhatsApp/Instagram/TikTok autour ; génère
octobre-décembre systématiquement à partir des axes donnés.
"""
import codecs
import datetime
import json
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA, exist_ok=True)

AUT, MET, PRE = "autorité_éducative", "methode_excellence", "la_preuve"

FR_MONTHS = ["", "janvier", "février", "mars", "avril", "mai", "juin",
             "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
FR_MONTHS_SHORT = ["", "jan", "fév", "mar", "avr", "mai", "juin",
                   "juil", "aoû", "sep", "oct", "nov", "déc"]


def fr_date(d):
    return "%d %s %d" % (d.day, FR_MONTHS[d.month], d.year)


def fr_date_short(d):
    return "%d %s" % (d.day, FR_MONTHS_SHORT[d.month])


def month_id(d):
    return "%04d-%02d" % (d.year, d.month)


# ---------------------------------------------------------------------------
# PLATEFORMES — couleurs natives (outil interne, usage fonctionnel de
# reconnaissance de plateforme — pas un visuel de marque Excellence+/AORA)
# ---------------------------------------------------------------------------
PLATFORMS = [
    {"id": "facebook", "nom": "Facebook", "icone": "\U0001F4D8", "couleur": "#1877F2"},
    {"id": "whatsapp", "nom": "WhatsApp", "icone": "\U0001F4AC", "couleur": "#25D366"},
    {"id": "instagram", "nom": "Instagram", "icone": "\U0001F4F8", "couleur": "#E1306C"},
    {"id": "tiktok", "nom": "TikTok", "icone": "\U0001F3B5", "couleur": "#010101"},
]
PLATFORMS_HORS_SCOPE = [
    {"id": "youtube", "nom": "YouTube", "icone": "▶", "couleur": "#FF0000", "badge": "Activation oct. 2026"},
    {"id": "linkedin", "nom": "LinkedIn", "icone": "in", "couleur": "#0A66C2", "badge": "Activation oct. 2026"},
]
PLATFORM_CODE = {"facebook": "FB", "whatsapp": "WA", "instagram": "IG", "tiktok": "TT",
                  "youtube": "YT", "linkedin": "LI"}

PILLARS = [
    {"id": AUT, "nom": "Autorité", "nom_long": "Autorité éducative", "couleur": "#C2570F", "part": 40, "phare": True},
    {"id": MET, "nom": "Méthode", "nom_long": "La méthode Excellence+", "couleur": "#1B2D5C", "part": 35, "phare": False},
    {"id": PRE, "nom": "Preuve", "nom_long": "La preuve", "couleur": "#1B6B3C", "part": 25, "phare": False},
]

STATUTS = [
    {"id": "a_rediger", "label": "À rédiger", "couleur": "#9CA0A8"},
    {"id": "bat_envoye", "label": "BAT envoyé", "couleur": "#F37021"},
    {"id": "bat_valide", "label": "BAT validé", "couleur": "#3B82C4"},
    {"id": "bap_recu", "label": "BAP reçu", "couleur": "#1B6B3C"},
    {"id": "publie", "label": "Publié", "couleur": "#22C55E"},
]

MONTHS = [
    {"id": "2026-07", "nom": "Juillet 2026", "sous_titre": "Mois 2 — Anticipation", "theme": "ANTICIPATION RENTRÉE",
     "couleur": "#1B2D5C", "priorite": False},
    {"id": "2026-08", "nom": "Août 2026", "sous_titre": "Mois 3 — Conversion intensive", "theme": "CONVERSION INTENSIVE",
     "couleur": "#F37021", "priorite": True},
    {"id": "2026-09", "nom": "Septembre 2026", "sous_titre": "Mois 4 — Fermeture", "theme": "FERMETURE & URGENCE",
     "couleur": "#C0392B", "priorite": False},
    {"id": "2026-10", "nom": "Octobre 2026", "sous_titre": "Mois 5 — Fidélisation", "theme": "FIDÉLISATION",
     "couleur": "#27AE60", "priorite": False},
    {"id": "2026-11", "nom": "Novembre 2026", "sous_titre": "Mois 6 — Autorité", "theme": "AUTORITÉ",
     "couleur": "#142850", "priorite": False},
    {"id": "2026-12", "nom": "Décembre 2026", "sous_titre": "Mois 7 — Bilan", "theme": "BILAN & PROJECTION",
     "couleur": "#D4AC0D", "priorite": False},
]
MONTH_BY_ID = {m["id"]: m for m in MONTHS}

META_ADS = [
    {"id": "ADS-1", "nom": "Campagne META ADS 1 — TEST", "periode": "14–27 juillet 2026", "budget": None,
     "mois": "2026-07", "debut_iso": "2026-07-14", "fin_iso": "2026-07-27"},
    {"id": "ADS-2", "nom": "Campagne META ADS 2 — CONVERSION", "periode": "4–24 août 2026", "budget": "30 000 FCFA",
     "mois": "2026-08", "debut_iso": "2026-08-04", "fin_iso": "2026-08-24"},
    {"id": "ADS-3", "nom": "Campagne META ADS 3 — FERMETURE", "periode": "8–20 septembre 2026", "budget": "10 000 FCFA",
     "mois": "2026-09", "debut_iso": "2026-09-08", "fin_iso": "2026-09-20"},
]

KPI_PAR_MOIS = {
    "2026-07": "200-350 nouveaux abonnés FB · 5-8 demandes WhatsApp/jour · 2-3 inscriptions Vacances Utiles",
    "2026-08": "5-8 messages WhatsApp/jour · 8-12 nouvelles inscriptions",
    "2026-09": "6-10 inscriptions finales · verrouillage portefeuille rentrée",
}

INTERDITS_NOTE = (
    "Ne jamais écrire « Excellence++ » (nom exact : Excellence+) · "
    "ne jamais mentionner le headcount enseignants · ne jamais nommer Prepdia · "
    "ne jamais mélanger budget AORA et budget Meta Ads · "
    "ne jamais publier sans BAP écrit (bap_recu_le non vide) · "
    "vocal WhatsApp non accepté comme BAP · "
    "ne jamais mentionner la Fondation Zacharias Tanee Fomum dans un post réseaux."
)


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += datetime.timedelta(days=1)


def build_weeks(start, end):
    """Retourne {iso_week_label: [dates]} et la liste ordonnée WEEKS avec mois dominant."""
    weeks_seen = {}
    for d in daterange(start, end):
        iso_year, iso_week, _ = d.isocalendar()
        weeks_seen.setdefault((iso_year, iso_week), []).append(d)
    WEEKS = []
    week_days = {}
    for (iso_year, iso_week), days in sorted(weeks_seen.items()):
        label = "S%d" % iso_week
        m = month_id(days[len(days) // 2])
        WEEKS.append({"id": label, "label": "Semaine %d" % iso_week,
                       "dates": "%s – %s" % (fr_date_short(days[0]), fr_date(days[-1])),
                       "mois": m,
                       "debut_iso": days[0].isoformat(), "fin_iso": days[-1].isoformat()})
        week_days[label] = days
    return WEEKS, week_days


def d_of(days, iso_weekday):
    match = [d for d in days if d.isoweekday() == iso_weekday]
    return match[0] if match else None


def make_id(platform, week_label, seq_counter):
    key = (platform, week_label)
    seq_counter[key] = seq_counter.get(key, 0) + 1
    return "EXC-%s-2026-%s-%03d" % (PLATFORM_CODE[platform], week_label, seq_counter[key])


def base_entry(entry_id, titre, pilier, plateforme, format_, date_obj, heure, mois, tags=None, meta_ads=None):
    m = MONTH_BY_ID[mois]
    return {
        "id": entry_id,
        "titre": titre,
        "pilier": pilier,
        "format": format_,
        "plateforme": plateforme,
        "mois": mois,
        "date": "%s · %s WAT" % (fr_date(date_obj), heure),
        "date_iso": date_obj.isoformat(),
        "heure": heure,
        "tags": tags or [],
        "favori": False,
        "statut": "a_rediger",
        "meta_ads": meta_ads,
        "resume": "%s. Pilier %s — mois « %s ». Statut à rédiger : aucun texte final, aucun BAT/BAP à ce stade." % (
            titre,
            {AUT: "Autorité éducative", MET: "La méthode Excellence+", PRE: "La preuve"}[pilier],
            m["theme"]),
        "notes": INTERDITS_NOTE,
    }


# ---------------------------------------------------------------------------
# JUILLET / AOÛT / SEPTEMBRE — Facebook transcrit fidèlement (titre, pilier)
# par semaine (S1..S4). "toute notre équipe" remplace tout chiffre headcount.
# ---------------------------------------------------------------------------
EXPLICIT_FB = {
    "2026-07": [
        [("Bulletin décevant : 5 réactions à adopter (et 3 à éviter)", AUT),
         ("Témoignage audio : éviter le redoublement", PRE),
         ("5 chiffres Excellence+ depuis le début", PRE),
         ("Sondage — Avez-vous déjà fait appel à un répétiteur ?", AUT)],
        [("Classe d'examen 2026-2027 : ce qu'il faut savoir", AUT),
         ("Témoignage — mention Très Bien au Bac", PRE),
         ("Portrait enseignant", MET),
         ("Vacances utiles ou pures vacances ?", AUT)],
        [("ANNONCE — Formule Vacances Utiles", MET),
         ("Combler les lacunes en 6 semaines", MET),
         ("Témoignage Bac S 2025", PRE),
         ("Quel rêve d'études pour votre enfant ?", AUT)],
        [("5 mythes sur les cours à domicile", AUT),
         ("Recrutement 2026 : nos critères", MET),
         ("Témoignage élève BEPC", PRE),
         ("Sondage — Votre priorité rentrée ?", AUT)],
    ],
    "2026-08": [
        [("🚨 Inscriptions rentrée 2026 ouvertes", AUT),
         ("Nos formules rentrée", MET),
         ("Témoignage Bac C 2025", PRE),
         ("Sondage — Avez-vous commencé à organiser la rentrée ?", AUT)],
        [("Choisir son répétiteur : 6 questions à poser", AUT),
         ("Notre engagement rentrée 2026", MET),
         ("Témoignage — une maman ET son élève", PRE),
         ("Sondage — Quelle classe à la rentrée ?", AUT),
         ("Post bonus — engagement", AUT)],
        [("Classe d'examen : formules dédiées", MET),
         ("Première séance Excellence+ : ce qui se passe", MET),
         ("Témoignage — mention Très Bien au BEPC", PRE),
         ("Tagguez un parent qui prépare la rentrée", AUT),
         ("Carrousel Instagram adapté Facebook", MET)],
        [("Ce qu'Excellence+ a accompli en 2025-2026", PRE),
         ("Une journée d'enseignant", MET),
         ("J-15 : les 5 dernières choses à prévoir", AUT),
         ("⏰ Plus que 2 semaines avant la rentrée", AUT),
         ("Post de relance inscriptions", AUT)],
    ],
    "2026-09": [
        [("Message de la direction — « C'est la rentrée »", MET),
         ("Toute notre équipe est prête", MET),
         ("5 premières semaines : ce qu'on peut attendre d'un enfant", AUT),
         ("Comment se passe la 1ère semaine pour vos enfants ?", AUT)],
        [("1ère semaine difficile ? 3 signes qu'il faut agir maintenant", AUT),
         ("Inscriptions encore ouvertes jusqu'au 20 septembre", AUT),
         ("Témoignage — une famille nouvelle en 2026", PRE)],
        [("Avant que le retard ne s'installe : agir dans les 15 premiers jours", AUT),
         ("⏰ Dernières inscriptions", AUT),
         ("Témoignage vidéo — succès rentrée 2025", PRE)],
        [("Premier mois d'école : 3 signaux à surveiller", AUT),
         ("🔔 Inscriptions fermées le 28 septembre", AUT),
         ("Merci aux familles qui nous ont fait confiance", PRE),
         ("Rentrée 2026 Excellence+ en chiffres", PRE)],
    ],
}

FB_DAYS_4 = [1, 3, 5, 7]        # lun/mer/ven/dim
FB_DAYS_5 = [1, 3, 5, 6, 7]     # lun/mer/ven/sam/dim

WA_THEMES = {
    "2026-07": ["Témoignage vidéo (priorité)", "Rappel Vacances Utiles", "Conseil vacances productives"],
    "2026-08": ["Rappel inscriptions — priorité abonnés", "Témoignage vidéo", "Photo coulisses pré-rentrée"],
    "2026-09": ["Photo terrain — cours en action", "Message de la direction", "Relance ciblée"],
}
WA_DAYS = [2, 4, 6]  # mar/jeu/sam
WA_PILIER_BY_THEME_IDX = {0: PRE, 1: AUT, 2: MET}  # approx: témoignage=preuve, rappel=autorité, coulisses=méthode

IG_DAYS = [3, 6]  # mer/sam
TT_DAYS = [5, 7]  # ven/dim

IG_RUBRIQUES_JAS = [
    ("Carrousel — {theme}, ce qu'il faut savoir", AUT),
    ("Post engageant — {theme}, votre avis ?", AUT),
    ("Carrousel — dans les coulisses de la rentrée, semaine {n}", MET),
    ("Reels — un conseil en 30 secondes ({n})", AUT),
]
TT_RUBRIQUES_JAS = [
    ("Script 60s — un conseil rapide sur {theme_lower}, semaine {n}", AUT),
    ("Vidéo tendance — coulisses du suivi ({n})", MET),
]

MONTH_THEME_LOWER = {
    "2026-07": "l'anticipation de la rentrée",
    "2026-08": "la conversion intensive",
    "2026-09": "la fermeture des inscriptions",
}


# ---------------------------------------------------------------------------
# OCTOBRE / NOVEMBRE / DÉCEMBRE — axes donnés (pas de posts explicites),
# génération systématique ancrée sur ces axes exacts.
# ---------------------------------------------------------------------------
AXES_OND = {
    "2026-10": {
        "facebook": ["Coulisses de l'accompagnement en cours", "Portrait enseignant",
                     "Vie de la communauté Excellence+", "Conseil suivi mi-trimestre",
                     "Témoignage élève en cours d'année"],
        "whatsapp": ["Message exclusif abonnés", "Conseil hebdo", "Sondage satisfaction"],
        "pilote": True,  # YouTube + LinkedIn premiers contenus pilote
    },
    "2026-11": {
        "facebook": ["Conseil examens de fin de trimestre", "Méthode de révision intensive",
                     "Préparer le premier bulletin 2026-2027", "Contenu pédagogique à valeur forte"],
        "whatsapp": ["Conseil hebdo", "Rappel méthode", "Message direct abonnés"],
        "pilote": False,
    },
    "2026-12": {
        "facebook": ["Bilan de l'année 2026", "Perspectives 2027", "Témoignage de fin d'année",
                     "Remerciements aux familles", "Teaser programme janvier 2027"],
        "whatsapp": ["Message chaleureux de fin d'année", "Bilan trimestre pour les abonnés", "Vœux"],
        "pilote": False,
    },
}
AXES_PILIER_GUESS = {
    "Coulisses de l'accompagnement en cours": MET, "Portrait enseignant": MET,
    "Vie de la communauté Excellence+": MET, "Conseil suivi mi-trimestre": AUT,
    "Témoignage élève en cours d'année": PRE, "Conseil examens de fin de trimestre": AUT,
    "Méthode de révision intensive": AUT, "Préparer le premier bulletin 2026-2027": AUT,
    "Contenu pédagogique à valeur forte": AUT, "Bilan de l'année 2026": PRE,
    "Perspectives 2027": MET, "Témoignage de fin d'année": PRE,
    "Remerciements aux familles": PRE, "Teaser programme janvier 2027": MET,
    "Message exclusif abonnés": MET, "Conseil hebdo": AUT, "Sondage satisfaction": AUT,
    "Rappel méthode": AUT, "Message direct abonnés": MET,
    "Message chaleureux de fin d'année": PRE, "Bilan trimestre pour les abonnés": PRE, "Vœux": PRE,
}


def main():
    start = datetime.date(2026, 7, 1)
    end = datetime.date(2026, 12, 31)
    WEEKS, week_days = build_weeks(start, end)
    weeks_by_month = {}
    for w in WEEKS:
        weeks_by_month.setdefault(w["mois"], []).append(w)

    entries = []
    seq = {}

    def add(entry):
        entries.append(entry)

    # ---- Juillet / Août / Septembre : Facebook explicite ----
    for mois, weeks_content in EXPLICIT_FB.items():
        weeks = weeks_by_month[mois]
        for wi, week_posts in enumerate(weeks_content):
            if wi >= len(weeks):
                break
            w = weeks[wi]
            days = week_days[w["id"]]
            day_pattern = FB_DAYS_5 if len(week_posts) >= 5 else FB_DAYS_4
            for pi, (titre, pilier) in enumerate(week_posts):
                if pi >= len(day_pattern):
                    break
                date_obj = d_of(days, day_pattern[pi])
                if not date_obj:
                    continue
                eid = make_id("facebook", w["id"], seq)
                add(base_entry(eid, titre, pilier, "facebook", "Image + texte / Carrousel",
                                date_obj, "18:30", mois, tags=["facebook", pilier]))

    # ---- Juillet / Août / Septembre : WhatsApp (rotation des 3 thèmes donnés) ----
    for mois, themes in WA_THEMES.items():
        for w in weeks_by_month[mois]:
            days = week_days[w["id"]]
            for ti, theme in enumerate(themes):
                date_obj = d_of(days, WA_DAYS[ti])
                if not date_obj:
                    continue
                heure = ["07:30", "12:00", "08:00"][ti]
                pilier = WA_PILIER_BY_THEME_IDX[ti]
                titre = "%s — semaine du %s" % (theme, fr_date_short(days[0]))
                eid = make_id("whatsapp", w["id"], seq)
                add(base_entry(eid, titre, pilier, "whatsapp", "Texte court",
                                date_obj, heure, mois, tags=["whatsapp", pilier]))

    # ---- Juillet / Août / Septembre : Instagram + TikTok (générés, ancrés sur le thème du mois) ----
    for mois in ("2026-07", "2026-08", "2026-09"):
        theme_lower = MONTH_THEME_LOWER[mois]
        for wk_i, w in enumerate(weeks_by_month[mois]):
            days = week_days[w["id"]]
            for ii, iso_wd in enumerate(IG_DAYS):
                date_obj = d_of(days, iso_wd)
                if not date_obj:
                    continue
                tmpl, pilier = IG_RUBRIQUES_JAS[(ii + wk_i) % len(IG_RUBRIQUES_JAS)]
                titre = tmpl.format(theme=theme_lower.capitalize(), theme_lower=theme_lower, n=wk_i + 1)
                eid = make_id("instagram", w["id"], seq)
                add(base_entry(eid, titre, pilier, "instagram", "Carrousel",
                                date_obj, "09:00" if ii == 0 else "19:00", mois, tags=["instagram", pilier]))
            for ti, iso_wd in enumerate(TT_DAYS):
                date_obj = d_of(days, iso_wd)
                if not date_obj:
                    continue
                tmpl, pilier = TT_RUBRIQUES_JAS[ti % len(TT_RUBRIQUES_JAS)]
                titre = tmpl.format(theme=theme_lower, theme_lower=theme_lower, n=wk_i + 1)
                eid = make_id("tiktok", w["id"], seq)
                add(base_entry(eid, titre, pilier, "tiktok", "Vidéo 60s",
                                date_obj, "17:00" if ti == 0 else "20:00", mois, tags=["tiktok", pilier]))

    # ---- Octobre / Novembre / Décembre : axes donnés, rotation systématique ----
    LAP_SUFFIX = ["", " — suite", " — le point cette semaine", " — nouvel angle", " — on y revient"]

    def with_lap(text, i, pool_len):
        lap = i // pool_len
        return text + LAP_SUFFIX[lap % len(LAP_SUFFIX)]

    for mois, axes in AXES_OND.items():
        fb_axes = axes["facebook"]
        wa_axes = axes["whatsapp"]
        fb_i = wa_i = 0
        for w in weeks_by_month[mois]:
            days = week_days[w["id"]]
            for wd in FB_DAYS_4:
                date_obj = d_of(days, wd)
                if not date_obj:
                    continue
                axe_base = fb_axes[fb_i % len(fb_axes)]
                axe = with_lap(axe_base, fb_i, len(fb_axes))
                pilier = AXES_PILIER_GUESS.get(axe_base, AUT)
                eid = make_id("facebook", w["id"], seq)
                add(base_entry(eid, axe, pilier, "facebook", "Image + texte / Carrousel",
                                date_obj, "18:30", mois, tags=["facebook", pilier]))
                fb_i += 1
            for wd in WA_DAYS:
                date_obj = d_of(days, wd)
                if not date_obj:
                    continue
                axe_base = wa_axes[wa_i % len(wa_axes)]
                axe = with_lap(axe_base, wa_i, len(wa_axes))
                pilier = AXES_PILIER_GUESS.get(axe_base, MET)
                eid = make_id("whatsapp", w["id"], seq)
                add(base_entry(eid, axe, pilier, "whatsapp", "Texte court",
                                date_obj, "12:00", mois, tags=["whatsapp", pilier]))
                wa_i += 1
            for ii, wd in enumerate(IG_DAYS):
                date_obj = d_of(days, wd)
                if not date_obj:
                    continue
                pilier = [AUT, MET][ii % 2]
                ig_idx = fb_i + ii
                titre = "Carrousel — %s" % with_lap(fb_axes[ig_idx % len(fb_axes)].lower(), ig_idx, len(fb_axes))
                eid = make_id("instagram", w["id"], seq)
                add(base_entry(eid, titre,
                                pilier, "instagram", "Carrousel", date_obj,
                                "09:00" if ii == 0 else "19:00", mois, tags=["instagram", pilier]))
            for ti, wd in enumerate(TT_DAYS):
                date_obj = d_of(days, wd)
                if not date_obj:
                    continue
                pilier = [MET, PRE][ti % 2]
                tt_idx = fb_i + ti + 1
                titre = "Vidéo — %s" % with_lap(fb_axes[tt_idx % len(fb_axes)].lower(), tt_idx, len(fb_axes))
                eid = make_id("tiktok", w["id"], seq)
                add(base_entry(eid, titre,
                                pilier, "tiktok", "Vidéo 45-60s", date_obj,
                                "17:00" if ti == 0 else "20:00", mois, tags=["tiktok", pilier]))

    # ---- Octobre : contenus pilote YouTube + LinkedIn (activation progressive) ----
    oct_weeks = weeks_by_month["2026-10"]
    if oct_weeks:
        last_week = oct_weeks[-1]
        days = week_days[last_week["id"]]
        date_yt = d_of(days, 3) or days[0]
        date_li = d_of(days, 5) or days[-1]
        eid = make_id("youtube", last_week["id"], seq)
        add(base_entry(eid, "Contenu pilote — présentation de la méthode Excellence+", MET,
                        "youtube", "Vidéo", date_yt, "18:00", "2026-10", tags=["youtube", "pilote"]))
        eid = make_id("linkedin", last_week["id"], seq)
        add(base_entry(eid, "Contenu pilote — positionnement institutionnel Excellence+", MET,
                        "linkedin", "Post texte", date_li, "09:00", "2026-10", tags=["linkedin", "pilote"]))

    entries.sort(key=lambda e: (e["date_iso"], e["plateforme"]))

    with codecs.open(os.path.join(DATA, "entries.json"), "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "weeks.json"), "w", encoding="utf-8") as f:
        json.dump(WEEKS, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "months.json"), "w", encoding="utf-8") as f:
        json.dump(MONTHS, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "pillars.json"), "w", encoding="utf-8") as f:
        json.dump(PILLARS, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "platforms.json"), "w", encoding="utf-8") as f:
        json.dump(PLATFORMS, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "platforms_hors_scope.json"), "w", encoding="utf-8") as f:
        json.dump(PLATFORMS_HORS_SCOPE, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "statuts.json"), "w", encoding="utf-8") as f:
        json.dump(STATUTS, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "meta_ads.json"), "w", encoding="utf-8") as f:
        json.dump(META_ADS, f, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(DATA, "kpi.json"), "w", encoding="utf-8") as f:
        json.dump(KPI_PAR_MOIS, f, ensure_ascii=False, indent=2)

    from collections import Counter
    c = Counter(e["pilier"] for e in entries)
    total = len(entries)
    print("Total entrées :", total)
    for p in (AUT, MET, PRE):
        print("  %s : %d (%.1f%%)" % (p, c[p], 100.0 * c[p] / total))
    print("Semaines :", len(WEEKS))
    print("Par plateforme :", dict(Counter(e["plateforme"] for e in entries)))
    print("Par mois :", dict(Counter(e["mois"] for e in entries)))


if __name__ == "__main__":
    main()
