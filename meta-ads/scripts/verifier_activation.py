#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier_activation.py — Les quatre portes bloquantes du pipeline Meta Ads.

POINT DE VÉRITÉ UNIQUE. Aucun autre script de meta-ads/scripts/ ne réimplémente
cette logique : ils importent tous `exiger_portes_ouvertes()` et s'arrêtent si elle
lève. Une règle écrite à deux endroits finit par diverger — et ici, diverger veut
dire dépenser de l'argent qui n'a pas été autorisé.

Les portes, dans cet ordre, aucune ne suffit seule :

  1. Activation temporelle   le mois courant est explicitement autorisé
  2. Autorisation budgétaire  BAB écrite, scénario retenu, plafond chiffré
  3. Créatif validé           BAP contenu ET visuel dans visuels/approuves/
  4. Cohérence du compte      les identifiants visés = ceux de meta_ads_comptes.json

Différence avec le pipeline organique : la porte 2 n'existe pas côté Composio.
C'est celle du budget, et elle est propre à ce pipeline.

Ce script ne publie rien, ne dépense rien, ne modifie aucun fichier. Il dit
lesquelles des quatre portes sont ouvertes, et il ne rend jamais un verdict
implicite : l'absence de refus n'est pas une autorisation, seule la liste
complète des quatre ✅ l'est.

Usage :
    python3 meta-ads/scripts/verifier_activation.py
    python3 meta-ads/scripts/verifier_activation.py --campagne meta-ads/campagnes/en_preparation/EXC-ADS-2026-001.md
    python3 meta-ads/scripts/verifier_activation.py --mois 2026-09 --json

Code de sortie : 0 si les quatre portes sont ouvertes, 1 si au moins une est
fermée, 2 si le script n'a pas pu faire son travail (dépôt introuvable).
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ pyyaml requis (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)


# Clés de mois telles qu'elles s'écrivent dans meta_ads_activation.json :
# sans accent, en minuscules, suffixées par l'année → « aout_2026 ».
MOIS_FR = [
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
]

# Emplacements acceptés pour les scénarios budgétaires. Le fichier fait foi sur
# les montants ; sans lui, aucun montant n'est opposable (voir porte 2).
SCENARIOS_ATTENDUS = [
    "scenarios_budget_metaads.pdf",
    "scenarios_budget_metaads.md",
    "meta-ads/scenarios_budget_metaads.pdf",
    "meta-ads/scenarios_budget_metaads.md",
]


class PortesFermees(RuntimeError):
    """Levée dès qu'un script tente une action réelle avec une porte fermée."""

    def __init__(self, portes):
        self.portes = portes
        fermees = [p for p in portes if not p.ouverte]
        detail = " · ".join(f"porte {p.numero} ({p.nom}) : {p.motif}" for p in fermees)
        super().__init__(f"{len(fermees)} porte(s) fermée(s) — {detail}")


class Porte:
    def __init__(self, numero: int, nom: str, ouverte: bool, motif: str, critique: bool = False):
        self.numero = numero
        self.nom = nom
        self.ouverte = ouverte
        self.motif = motif
        # `critique` = un écart qui ne se rattrape pas s'il passe (mauvais compte,
        # budget non autorisé), par opposition à « pas encore configuré ».
        self.critique = critique

    def __repr__(self):
        return f"<Porte {self.numero} {'ouverte' if self.ouverte else 'fermée'}>"

    def en_dict(self):
        return {
            "numero": self.numero,
            "nom": self.nom,
            "ouverte": self.ouverte,
            "motif": self.motif,
            "critique": self.critique,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Lecture — aucune de ces fonctions n'invente de valeur de repli.
# ─────────────────────────────────────────────────────────────────────────────

def est_vide(v) -> bool:
    """Même définition que côté organique (scripts/programmer_publications.py)."""
    if v is None:
        return True
    return str(v).strip().strip('"').strip("'") in ("", "null", "None", "~", "A_REMPLIR")


def fcfa(montant) -> str:
    """Montant lisible : séparateur de milliers par espace, comme en français.

    Formater le nombre seul, jamais la phrase qui le contient : un .replace()
    appliqué à toute la chaîne mange aussi les virgules de ponctuation.
    """
    try:
        return f"{int(montant):,}".replace(",", " ") + " FCFA"
    except (TypeError, ValueError):
        return f"{montant} FCFA"


def lire_json(chemin: Path):
    """Retourne (données, erreur). Un JSON illisible n'est jamais traité comme vide."""
    if not chemin.is_file():
        return None, f"{chemin.name} introuvable"
    try:
        return json.loads(chemin.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as err:
        return None, f"{chemin.name} illisible ({err})"


def lire_front_matter(chemin: Path):
    """Front-matter YAML d'un .md. Retourne (meta, corps) ou (None, '')."""
    if not chemin.is_file():
        return None, ""
    brut = chemin.read_text(encoding="utf-8")
    if not brut.lstrip().startswith("---"):
        return None, ""
    parties = brut.split("---", 2)
    if len(parties) < 3:
        return None, ""
    try:
        meta = yaml.safe_load(parties[1]) or {}
    except yaml.YAMLError:
        return None, ""
    return (meta if isinstance(meta, dict) else None), parties[2]


def cle_mois(jour: date) -> str:
    return f"{MOIS_FR[jour.month - 1]}_{jour.year}"


def mois_depuis_argument(valeur: str) -> date:
    """« 2026-09 » → premier jour du mois. Sert aux tests et aux mois futurs."""
    annee, mois = valeur.split("-")
    return date(int(annee), int(mois), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Porte 1 — Activation temporelle
# ─────────────────────────────────────────────────────────────────────────────

def porte_1_activation(repo: Path, jour: date) -> Porte:
    data, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_activation.json")
    if err:
        return Porte(1, "activation temporelle", False,
                     f"{err} — sans ce fichier, aucun mois n'est autorisé", critique=True)

    cle = cle_mois(jour)
    entree = data.get(cle)
    if entree is None:
        return Porte(1, "activation temporelle", False,
                     f"mois « {cle} » absent du fichier — un mois non déclaré n'est pas "
                     f"un mois autorisé")

    autorise = entree.get("autorise") if isinstance(entree, dict) else None
    if autorise is True:
        return Porte(1, "activation temporelle", True, f"{cle} explicitement autorisé")

    # null et false sont traités identiquement : seul true ouvre.
    if autorise is None:
        motif = entree.get("en_attente_de") if isinstance(entree, dict) else None
        return Porte(1, "activation temporelle", False,
                     f"{cle} non tranché (autorise: null)"
                     + (f" — en attente de : {motif}" if motif else ""))
    raison = entree.get("raison") if isinstance(entree, dict) else None
    return Porte(1, "activation temporelle", False,
                 f"{cle} refusé (autorise: false)" + (f" — {raison}" if raison else ""))


# ─────────────────────────────────────────────────────────────────────────────
# Porte 2 — Autorisation budgétaire écrite (BAB)
# ─────────────────────────────────────────────────────────────────────────────

def porte_2_budget(repo: Path) -> Porte:
    data, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_budgets.json")
    if err:
        return Porte(2, "autorisation budgétaire (BAB)", False,
                     f"{err} — aucun plafond opposable", critique=True)

    manquants = [c for c in ("scenario_retenu", "montant_mensuel_fcfa", "autorisation_ecrite_ref")
                 if est_vide(data.get(c))]
    if manquants:
        return Porte(2, "autorisation budgétaire (BAB)", False,
                     f"champ(s) non renseigné(s) : {', '.join(manquants)}")

    # Le fichier de scénarios fait foi sur les montants. Absent, un montant
    # configuré n'est adossé à rien de vérifiable — on refuse plutôt que de
    # faire confiance à un chiffre sans source.
    if not any((repo / c).is_file() for c in SCENARIOS_ATTENDUS):
        return Porte(2, "autorisation budgétaire (BAB)", False,
                     "scenarios_budget_metaads.pdf (ou .md) absent du dépôt — le montant "
                     "configuré n'est adossé à aucune source de vérité versionnée",
                     critique=True)

    montant = data.get("montant_mensuel_fcfa")
    if not isinstance(montant, int) or isinstance(montant, bool) or montant <= 0:
        return Porte(2, "autorisation budgétaire (BAB)", False,
                     f"montant_mensuel_fcfa doit être un entier positif de FCFA, reçu "
                     f"{montant!r}", critique=True)

    # La référence doit pointer vers un fichier réellement présent dans
    # BAB_budget/ : un champ rempli avec un chemin qui n'existe pas est une
    # autorisation imaginaire.
    ref = str(data.get("autorisation_ecrite_ref")).strip()
    dossier_bab = (repo / "meta-ads" / "validation" / "BAB_budget").resolve()
    cible = (repo / ref).resolve()
    if dossier_bab not in cible.parents:
        return Porte(2, "autorisation budgétaire (BAB)", False,
                     f"autorisation_ecrite_ref « {ref} » pointe hors de "
                     f"meta-ads/validation/BAB_budget/", critique=True)
    if not cible.is_file():
        return Porte(2, "autorisation budgétaire (BAB)", False,
                     f"autorisation_ecrite_ref « {ref} » ne correspond à aucun fichier — "
                     f"la trace écrite de M. NDOMMIE n'est pas archivée", critique=True)

    return Porte(2, "autorisation budgétaire (BAB)", True,
                 f"scénario « {data['scenario_retenu']} », plafond {fcfa(montant)}/mois, "
                 f"trace : {ref}")


# ─────────────────────────────────────────────────────────────────────────────
# Porte 3 — Créatif validé (BAP contenu + visuel approuvé)
# ─────────────────────────────────────────────────────────────────────────────

def _visuel_approuve(repo: Path, creatif_ref: str, visuel_ref=None):
    """Même double logique que côté organique : chemin explicite, sinon préfixe d'id.

    Le dossier de référence reste `visuels/approuves/` — celui du pipeline
    organique. Y déposer un fichier EST le geste humain de validation du visuel ;
    créer un second dossier d'approuvés propre aux ads dupliquerait ce geste et
    donc la source de vérité.
    """
    if not est_vide(visuel_ref):
        candidat = repo / str(visuel_ref).strip().strip('"').strip("'")
        if candidat.is_file():
            return candidat
    approuves = repo / "visuels" / "approuves"
    if creatif_ref and approuves.is_dir():
        for f in sorted(approuves.iterdir()):
            if f.is_file() and f.name.startswith(creatif_ref):
                return f
    return None


def post_organique_boostable(repo: Path, post_ref: str):
    """Éligibilité d'un post organique au boost. Retourne (ok, motif, meta_du_post).

    Fonction partagée entre porte_3_creatif (mode boost) et construire_campagne.py
    — une seule définition de ce qu'est un post "boostable", jamais deux.

    Cinq conditions simultanées :
      1. publie_le non vide — pas simplement composio_id/programme_le. Un post
         PROGRAMMÉ n'est pas encore PUBLIÉ ; les confondre est exactement l'erreur
         que le contrôle 5 de superviseur-publication-aora existe pour signaler.
      2. bap_recu_le ET bap_email_ref non vides, DIRECTEMENT sur ce post — vérifié
         explicitement plutôt que supposé via publie_le. Un post publié devrait
         déjà avoir franchi la porte BAP organique (programmer_publications.py
         l'exige), mais faire dépendre l'éligibilité au boost d'une chaîne de
         confiance indirecte est plus fragile qu'une vérification directe : les
         deux coûtent le même prix à vérifier, seule la seconde ne suppose rien.
      3. plateforme_post_id non vide — l'identifiant réel du post chez Meta,
         nécessaire pour construire object_story_id. Ce champ n'est aujourd'hui
         renseigné nulle part dans le dépôt : le mécanisme qui confirmerait une
         mise en ligne réelle n'existe pas encore (composio-publie-aora/SKILL.md
         §2). Tant qu'il manque, AUCUN post n'est boostable — ce n'est pas un bug
         de ce contrôle, c'est la porte qui tient.
      4. plateforme dans {facebook, instagram} — seules boostables par la
         Marketing API depuis ce pipeline.
      5. ne_pas_booster n'est pas true — exclusion explicite, poste par poste.
    """
    if est_vide(post_ref):
        return False, "post_ref non renseigné", None
    chemin = repo / str(post_ref).strip().strip('"').strip("'")
    if not chemin.is_file():
        return False, f"post_ref « {post_ref} » introuvable", None
    meta, _ = lire_front_matter(chemin)
    if meta is None:
        return False, f"{post_ref} : front-matter illisible", None
    if est_vide(meta.get("publie_le")):
        return False, (f"{post_ref} : publie_le vide — un post programmé mais non "
                       f"confirmé publié ne peut pas être boosté"), None
    if est_vide(meta.get("bap_recu_le")) or est_vide(meta.get("bap_email_ref")):
        return False, (f"{post_ref} : bap_recu_le/bap_email_ref vide sur le post organique — "
                       f"le BAP qui a autorisé la publication doit être vérifiable directement, "
                       f"pas seulement supposé parce que publie_le est renseigné"), None
    if meta.get("ne_pas_booster") is True:
        return False, f"{post_ref} : ne_pas_booster = true — exclusion explicite", None
    plateforme = str(meta.get("plateforme", "")).strip().lower()
    if plateforme not in ("facebook", "instagram"):
        return False, (f"{post_ref} : plateforme « {plateforme} » non éligible au "
                       f"boost (Facebook/Instagram uniquement)"), None
    if est_vide(meta.get("plateforme_post_id")):
        return False, (f"{post_ref} : plateforme_post_id vide — identifiant Meta réel "
                       f"du post requis, jamais déduit de composio_id"), None
    return True, "post organique publié, éligible", meta


def porte_3_creatif(repo: Path, campagne: Path = None) -> Porte:
    if campagne is None:
        return Porte(3, "créatif validé (BAP contenu)", False,
                     "aucune campagne cible fournie (--campagne) — une porte ne peut pas "
                     "s'ouvrir dans le vide")

    meta, _ = lire_front_matter(campagne)
    if meta is None:
        return Porte(3, "créatif validé (BAP contenu)", False,
                     f"{campagne.name} : front-matter illisible ou absent")

    if str(meta.get("type_campagne", "")).strip().lower() == "boost":
        ok, motif, _ = post_organique_boostable(repo, meta.get("post_ref"))
        return Porte(3, "créatif validé (BAP contenu)", ok,
                     f"{campagne.name} (boost) : {motif}")

    creatif_ref = str(meta.get("creatif_ref", "")).strip()
    if est_vide(creatif_ref):
        return Porte(3, "créatif validé (BAP contenu)", False,
                     f"{campagne.name} : creatif_ref non renseigné")

    # Condition 1 — BAP contenu écrit.
    dossier_bap = repo / "meta-ads" / "validation" / "BAP_contenu"
    fiche_bap, bap_recu, bap_ref = None, None, None
    if dossier_bap.is_dir():
        for f in sorted(dossier_bap.glob("*.md")):
            m, _ = lire_front_matter(f)
            if m and str(m.get("creatif_ref", "")).strip() == creatif_ref:
                fiche_bap, bap_recu, bap_ref = f, m.get("bap_recu_le"), m.get("bap_email_ref")
                break

    manque = []
    if fiche_bap is None:
        manque.append(f"aucune fiche BAP pour « {creatif_ref} » dans "
                      f"meta-ads/validation/BAP_contenu/")
    else:
        if est_vide(bap_recu):
            manque.append(f"bap_recu_le vide dans {fiche_bap.name}")
        if est_vide(bap_ref):
            manque.append(f"bap_email_ref vide dans {fiche_bap.name} — validation non opposable")

    # Condition 2 — visuel approuvé, simultanée, jamais alternative.
    visuel = _visuel_approuve(repo, creatif_ref, meta.get("visuel_ref"))
    if visuel is None:
        manque.append(f"aucun visuel pour « {creatif_ref} » dans visuels/approuves/")

    if manque:
        return Porte(3, "créatif validé (BAP contenu)", False, " ; ".join(manque))
    return Porte(3, "créatif validé (BAP contenu)", True,
                 f"BAP {bap_recu} ({fiche_bap.name}) + visuel {visuel.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Porte 4 — Cohérence du compte cible
# ─────────────────────────────────────────────────────────────────────────────

def porte_4_compte(repo: Path, campagne: Path = None) -> Porte:
    data, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_comptes.json")
    if err:
        return Porte(4, "cohérence du compte cible", False,
                     f"{err} — aucun identifiant de référence", critique=True)

    ad_account = data.get("ad_account_id")
    page_id = data.get("page_id")

    absents = [c for c in ("ad_account_id", "page_id") if est_vide(data.get(c))]
    if absents:
        return Porte(4, "cohérence du compte cible", False,
                     f"{', '.join(absents)} non renseigné(s) dans meta_ads_comptes.json — "
                     f"identifiant Meta réel à obtenir de M. NDOMMIE ou du Business Manager "
                     f"AORA, jamais à deviner")

    # La Page cible du pipeline payant doit être celle du pipeline organique.
    # Deux fichiers qui se contredisent valent une valeur absente.
    page_organique, err_page = lire_json(repo / "config" / "page_cible.json")
    if not err_page and isinstance(page_organique, dict):
        attendu = (page_organique.get("facebook") or {}).get("id")
        if attendu and str(attendu).strip() != str(page_id).strip():
            return Porte(4, "cohérence du compte cible", False,
                         f"page_id « {page_id} » ≠ config/page_cible.json « {attendu} » — "
                         f"les deux fichiers se contredisent sur la Page cible",
                         critique=True)

    if campagne is not None:
        meta, _ = lire_front_matter(campagne)
        if meta is None:
            return Porte(4, "cohérence du compte cible", False,
                         f"{campagne.name} : front-matter illisible")
        for champ, reference in (("ad_account_id", ad_account),
                                 ("page_id", page_id),
                                 ("instagram_actor_id", data.get("instagram_actor_id"))):
            vise = meta.get(champ)
            if est_vide(vise):
                continue  # Un champ non visé par la campagne n'est pas une divergence.
            if str(vise).strip() != str(reference).strip():
                return Porte(4, "cohérence du compte cible", False,
                             f"{campagne.name} vise {champ} « {vise} », la référence est "
                             f"« {reference} » — un budget parti sur le mauvais compte ne "
                             f"se rattrape pas", critique=True)

    return Porte(4, "cohérence du compte cible", True,
                 f"ad_account_id {ad_account} · page_id {page_id}")


# ─────────────────────────────────────────────────────────────────────────────
# API publique
# ─────────────────────────────────────────────────────────────────────────────

def verifier_portes(repo: Path, jour: date = None, campagne: Path = None, tout=False):
    """Évalue les portes dans l'ordre. S'arrête à la première fermée (sauf tout=True).

    tout=True force l'évaluation des quatre portes — utile pour un rapport
    d'état. En chemin d'exécution, on s'arrête à la première fermée : inutile
    d'aller plus loin, et ça évite de laisser croire qu'une porte plus loin a
    été « presque » franchie.
    """
    repo = Path(repo).resolve()
    jour = jour or date.today()
    portes = []
    for evaluer in (
        lambda: porte_1_activation(repo, jour),
        lambda: porte_2_budget(repo),
        lambda: porte_3_creatif(repo, campagne),
        lambda: porte_4_compte(repo, campagne),
    ):
        porte = evaluer()
        portes.append(porte)
        if not porte.ouverte and not tout:
            break
    return portes


def toutes_ouvertes(portes) -> bool:
    return len(portes) == 4 and all(p.ouverte for p in portes)


def exiger_portes_ouvertes(repo: Path, jour: date = None, campagne: Path = None):
    """Appelée en tête de tout script qui pourrait toucher l'API Meta.

    Lève PortesFermees si une seule porte n'est pas ouverte. Ne retourne
    silencieusement que dans le cas où les quatre le sont.
    """
    portes = verifier_portes(repo, jour=jour, campagne=campagne)
    if not toutes_ouvertes(portes):
        raise PortesFermees(portes)
    return portes


def afficher(portes, jour: date, campagne: Path = None):
    print(f"\n🔐 PORTES META ADS — {jour.strftime('%d/%m/%Y')} "
          f"(mois évalué : {cle_mois(jour)})")
    if campagne:
        print(f"   Campagne : {campagne}")
    print()
    noms = {1: "Activation temporelle", 2: "Autorisation budgétaire (BAB)",
            3: "Créatif validé (BAP contenu)", 4: "Cohérence du compte cible"}
    evaluees = {p.numero: p for p in portes}
    for numero in (1, 2, 3, 4):
        porte = evaluees.get(numero)
        if porte is None:
            print(f"   ⏹️  Porte {numero} — {noms[numero]} : non évaluée "
                  f"(arrêt à la première porte fermée)")
            continue
        marque = "✅" if porte.ouverte else ("🛑" if porte.critique else "❌")
        print(f"   {marque} Porte {numero} — {noms[numero]}")
        print(f"      {porte.motif}")
    print()
    if toutes_ouvertes(portes):
        print("   ✅ Les quatre portes sont ouvertes — exécution réelle possible.\n")
    else:
        fermees = [p.numero for p in portes if not p.ouverte]
        print(f"   ⛔ VERROUILLÉ — porte(s) fermée(s) : {', '.join(map(str, fermees))}.")
        print("      Aucun appel à l'API Meta ne sera tenté, aucune dépense possible.\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Les quatre portes bloquantes Meta Ads.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--campagne", type=Path, default=None,
                    help="Brief de campagne à évaluer (portes 3 et 4)")
    ap.add_argument("--mois", type=str, default=None,
                    help="Mois à évaluer au format AAAA-MM (défaut : mois courant)")
    ap.add_argument("--tout", action="store_true",
                    help="Évaluer les quatre portes au lieu de s'arrêter à la première fermée")
    ap.add_argument("--json", action="store_true", help="Sortie machine")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "meta-ads").is_dir():
        print(f"❌ {repo / 'meta-ads'} introuvable — ce n'est pas le dépôt attendu.",
              file=sys.stderr)
        return 2

    jour = mois_depuis_argument(args.mois) if args.mois else date.today()
    portes = verifier_portes(repo, jour=jour, campagne=args.campagne, tout=args.tout)

    if args.json:
        print(json.dumps({
            "mois": cle_mois(jour),
            "campagne": str(args.campagne) if args.campagne else None,
            "toutes_ouvertes": toutes_ouvertes(portes),
            "portes": [p.en_dict() for p in portes],
        }, ensure_ascii=False, indent=2))
    else:
        afficher(portes, jour, args.campagne)

    return 0 if toutes_ouvertes(portes) else 1


if __name__ == "__main__":
    sys.exit(main())
