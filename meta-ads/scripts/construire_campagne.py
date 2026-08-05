#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construire_campagne.py — Construit les objets campaign / adset / ad Meta Ads.

DRY-RUN PAR DÉFAUT. Le script affiche ce qui partirait et n'appelle rien. Il ne
bascule en exécution réelle que si les deux conditions sont réunies :

    1. le drapeau explicite --executer est passé,
    2. verifier_activation.py renvoie les QUATRE portes ouvertes.

L'une sans l'autre ne suffit pas. --executer sur des portes fermées n'est pas
une dérogation : c'est une erreur, et le script sort en échec sans rien tenter.

Mécanisme central : Click-to-WhatsApp — cohérent avec les scénarios budgétaires
validés. Le bouton pointe vers l'un des deux numéros Cameroun autorisés, jamais
le numéro France (même contrôle que le contrôle 9 de superviseur-publication-aora).

Placements : Facebook + Instagram uniquement. TikTok est hors Marketing API Meta ;
YouTube et LinkedIn sont hors périmètre contractuel (différés).

Usage :
    python3 meta-ads/scripts/construire_campagne.py --campagne <brief.md>
    python3 meta-ads/scripts/construire_campagne.py --campagne <brief.md> --json
    python3 meta-ads/scripts/construire_campagne.py --campagne <brief.md> --executer
"""
import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_activation import (  # noqa: E402
    PortesFermees,
    afficher,
    est_vide,
    exiger_portes_ouvertes,
    fcfa,
    lire_front_matter,
    lire_json,
    post_organique_boostable,
    verifier_portes,
)

# Version d'API épinglée : une version flottante change le comportement d'un
# appel sans qu'aucun commit ne l'explique.
API_VERSION = "v21.0"

PLACEMENTS_AUTORISES = {"facebook", "instagram"}
PLACEMENTS_REFUSES = {
    "tiktok": "hors Marketing API Meta — TikTok ne se pilote pas depuis ce pipeline",
    "youtube": "hors périmètre contractuel AORA-CCC-005 (différé)",
    "linkedin": "hors périmètre contractuel AORA-CCC-005 (différé)",
}

# Devises sans sous-unité : le montant s'envoie tel quel. Pour toutes les autres,
# l'API attend l'unité mineure (×100). Voir meta_ads_comptes.json → _devise_compte.
DEVISES_SANS_DECIMALE = {"XAF", "XOF", "JPY", "KRW", "CLP", "ISK", "VND"}


class BudgetRefuse(ValueError):
    """Plafond local dépassé — levée AVANT tout appel API, jamais après."""


class CreatifRefuse(ValueError):
    """Le créatif viole une règle absolue (numéro interdit, terme de liste rouge)."""


class ConfigurationIncomplete(ValueError):
    """Une valeur humaine manque — jamais remplacée par un défaut plausible."""


class PostNonBoostable(ValueError):
    """Le post organique référencé par un boost n'est pas éligible — voir motif."""


# ─────────────────────────────────────────────────────────────────────────────
# Conversion horaire — un seul endroit, comme côté organique
# ─────────────────────────────────────────────────────────────────────────────

def heure_utc(jour: str, heure: str) -> str:
    """WAT (UTC+1, sans heure d'été) → UTC ISO 8601.

    Le Cameroun ne pratique pas l'heure d'été : la conversion est constante toute
    l'année. Les runners GitHub Actions tournent en UTC — sans cette conversion,
    une campagne programmée à 06h00 WAT démarrerait à 07h00 WAT.
    """
    h = str(heure).strip().strip('"').strip("'") or "06:00"
    local = datetime.fromisoformat(f"{jour}T{h}:00")
    return (local - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+0000")


# ─────────────────────────────────────────────────────────────────────────────
# Idempotence — triple clé
# ─────────────────────────────────────────────────────────────────────────────

def empreinte_creatif(meta: dict, corps: str) -> str:
    """Hash stable du créatif : texte + référence visuelle + CTA.

    Deux briefs au texte identique produisent la même empreinte — c'est voulu :
    republier deux fois le même créatif est précisément ce qu'on veut empêcher.
    """
    matiere = "\n".join([
        str(meta.get("creatif_ref", "")).strip(),
        str(meta.get("visuel_ref", "")).strip(),
        str(meta.get("whatsapp_numero", "")).strip(),
        corps.strip(),
    ])
    return hashlib.sha256(matiere.encode("utf-8")).hexdigest()[:16]


def cle_idempotence(ad_account_id: str, empreinte: str, lancement_utc: str) -> str:
    """Triple clé (compte, créatif, date-heure de lancement programmée).

    Un retry GitHub Actions relance le même job avec les mêmes entrées : sans
    cette clé, il créerait une seconde campagne identique, avec un second budget.
    """
    brut = f"{ad_account_id}|{empreinte}|{lancement_utc}"
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()[:24]


def chemin_registre(repo: Path) -> Path:
    return repo / "meta-ads" / "campagnes" / "registre_idempotence.json"


def lire_registre(repo: Path) -> dict:
    registre, err = lire_json(chemin_registre(repo))
    if err or not isinstance(registre, dict):
        return {}
    return registre.get("cles", {}) if "cles" in registre else registre


def enregistrer_cle(repo: Path, cle: str, info: dict):
    """Écrit la clé APRÈS un appel API réussi. Avant, il n'y a rien à mémoriser."""
    chemin = chemin_registre(repo)
    registre, _ = lire_json(chemin)
    if not isinstance(registre, dict):
        registre = {}
    registre.setdefault("_lisez_moi", [
        "Registre d'idempotence des campagnes Meta Ads. Clé = sha256 tronqué de",
        "(ad_account_id, empreinte du créatif, date-heure de lancement UTC).",
        "Écrit uniquement après un appel API réussi. Ne jamais éditer à la main :",
        "supprimer une clé rend possible une seconde création de la même campagne,",
        "donc un second budget.",
    ])
    registre.setdefault("cles", {})[cle] = info
    chemin.write_text(json.dumps(registre, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Contrôles propres au créatif et au budget
# ─────────────────────────────────────────────────────────────────────────────

def valider_whatsapp(repo: Path, numero) -> str:
    """Le numéro du bouton Click-to-WhatsApp doit figurer dans config/contacts.json.

    Miroir du contrôle 9 de superviseur-publication-aora : le numéro France ne
    doit jamais apparaître dans un créatif Excellence+.
    """
    contacts, err = lire_json(repo / "config" / "contacts.json")
    if err:
        raise ConfigurationIncomplete(
            f"config/contacts.json : {err} — aucun numéro de référence, un numéro de "
            f"créatif ne peut pas être vérifié")

    autorises = contacts.get("whatsapp_posts") or []
    exclus = contacts.get("whatsapp_exclus") or {}
    if est_vide(numero):
        raise ConfigurationIncomplete(
            f"whatsapp_numero non renseigné dans le brief — numéros autorisés : "
            f"{', '.join(autorises)}")

    normaliser = lambda n: "".join(c for c in str(n) if c.isdigit())  # noqa: E731
    cible = normaliser(numero)

    for interdit, motif in exclus.items():
        if normaliser(interdit) == cible:
            raise CreatifRefuse(f"numéro « {numero} » interdit — {motif}")
    if cible.startswith("33"):
        raise CreatifRefuse(
            f"numéro « {numero} » : indicatif France (+33) — jamais dans un créatif "
            f"publicitaire Excellence+")
    for permis in autorises:
        if normaliser(permis) == cible:
            return permis
    raise CreatifRefuse(
        f"numéro « {numero} » absent de config/contacts.json → whatsapp_posts "
        f"({', '.join(autorises)}) — jamais de numéro inventé dans un créatif")


def valider_texte(repo: Path, corps: str):
    """Liste rouge — mêmes interdits absolus que le pipeline organique."""
    liste, err = lire_json(repo / "config" / "liste_rouge.json")
    termes = []
    if not err and isinstance(liste, dict):
        termes = liste.get("termes", [])
    elif not err and isinstance(liste, list):
        termes = liste
    if not termes:
        # Repli identique à scripts/programmer_publications.py — brand_guidelines §11.
        termes = ["Excellence++", "Prepdia", "La Réussite Plus", "Zacharias", "Fomum"]
    for terme in termes:
        if terme and terme.lower() in corps.lower():
            raise CreatifRefuse(f"terme interdit dans le créatif : « {terme} »")
    if "A_REMPLIR" in corps:
        raise CreatifRefuse("le créatif contient encore une valeur A_REMPLIR")


def montant_api(montant_fcfa: int, devise: str) -> int:
    """Convertit un montant en FCFA vers l'unité attendue par l'API Meta.

    Le facteur dépend de la devise du compte publicitaire — pas d'une convention
    générale. Une devise inconnue n'a pas de facteur par défaut : on refuse.
    """
    if est_vide(devise):
        raise ConfigurationIncomplete(
            "devise_compte non renseignée dans meta_ads_comptes.json — le facteur de "
            "conversion des budgets (×1 ou ×100) est indéterminé, et se tromper de "
            "facteur c'est dépenser 100 fois trop")
    d = str(devise).strip().upper()
    if d in DEVISES_SANS_DECIMALE:
        return int(montant_fcfa)
    raise ConfigurationIncomplete(
        f"devise_compte « {d} » : le compte publicitaire n'est pas en XAF. Les montants "
        f"des scénarios sont libellés en FCFA — la conversion FCFA → {d} est une "
        f"décision humaine (taux, arrondi), jamais une opération automatique du script")


def valider_budget(repo: Path, brief: dict) -> dict:
    """Plafond dur. Vérifié AVANT l'appel API, jamais après le rejet de Meta.

    Le plafond de meta_ads_budgets.json n'est pas une cible à approcher : c'est
    une limite que le script refuse de franchir, même « temporairement pour
    tester » (interdiction 6).
    """
    budgets, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_budgets.json")
    if err:
        raise ConfigurationIncomplete(f"meta_ads_budgets.json : {err}")

    plafond = budgets.get("montant_mensuel_fcfa")
    if not isinstance(plafond, int) or isinstance(plafond, bool) or plafond <= 0:
        raise ConfigurationIncomplete(
            f"montant_mensuel_fcfa non renseigné ou invalide ({plafond!r}) — aucun "
            f"plafond opposable, donc aucun budget constructible")

    quotidien = brief.get("budget_quotidien_fcfa")
    total = brief.get("budget_total_fcfa")
    if est_vide(quotidien) and est_vide(total):
        raise ConfigurationIncomplete(
            "le brief ne déclare ni budget_quotidien_fcfa ni budget_total_fcfa")

    for nom, valeur in (("budget_quotidien_fcfa", quotidien), ("budget_total_fcfa", total)):
        if not est_vide(valeur) and (not isinstance(valeur, int) or isinstance(valeur, bool)
                                     or valeur <= 0):
            raise BudgetRefuse(f"{nom} doit être un entier positif de FCFA, reçu {valeur!r}")

    # Un budget quotidien se compare au plafond MENSUEL sur 30 jours : un
    # quotidien anodin peut dépasser le plafond en fin de mois sans qu'aucune
    # ligne ne paraisse excessive.
    if not est_vide(quotidien):
        projete = quotidien * 30
        if projete > plafond:
            raise BudgetRefuse(
                f"budget_quotidien_fcfa {fcfa(quotidien)} × 30 j = {fcfa(projete)}, "
                f"au-dessus du plafond mensuel autorisé {fcfa(plafond)}")
    if not est_vide(total) and total > plafond:
        raise BudgetRefuse(
            f"budget_total_fcfa {fcfa(total)} au-dessus du plafond mensuel autorisé "
            f"{fcfa(plafond)}")

    return {"plafond_mensuel_fcfa": plafond,
            "budget_quotidien_fcfa": quotidien if not est_vide(quotidien) else None,
            "budget_total_fcfa": total if not est_vide(total) else None,
            "scenario_retenu": budgets.get("scenario_retenu")}


def valider_placements(brief: dict) -> list:
    demandes = brief.get("placements") or []
    if isinstance(demandes, str):
        demandes = [demandes]
    demandes = [str(p).strip().lower() for p in demandes]
    if not demandes:
        raise ConfigurationIncomplete("le brief ne déclare aucun placement")
    for p in demandes:
        if p in PLACEMENTS_REFUSES:
            raise CreatifRefuse(f"placement « {p} » refusé — {PLACEMENTS_REFUSES[p]}")
        if p not in PLACEMENTS_AUTORISES:
            raise CreatifRefuse(
                f"placement « {p} » inconnu — seuls {sorted(PLACEMENTS_AUTORISES)} "
                f"sont pilotés par ce pipeline")
    return demandes


def construire_ciblage(repo: Path) -> dict:
    """Ciblage géographique et démographique — refuse tant qu'il n'est pas résolu.

    Un ad set sans périmètre résolu ne plante pas : il cible plus large que prévu
    et dépense hors cible, silencieusement. C'est pour ça que le refus est ici.
    """
    ciblage, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_ciblage.json")
    if err:
        raise ConfigurationIncomplete(f"meta_ads_ciblage.json : {err}")

    if ciblage.get("ciblage_utilisable") is not True:
        raise ConfigurationIncomplete(
            "meta_ads_ciblage.json → ciblage_utilisable = false : la répartition des "
            "quartiers de Yaoundé entre les 4 zones pondérées n'est pas tranchée "
            "(conflit Odza / Santa Barbara documenté dans brand_guidelines.md §3 et "
            "STATUT_PROJET.md point 7). Voir _quartiers_non_resolus.")

    demo = ciblage.get("demographie") or {}
    if est_vide(demo.get("age_min")) or est_vide(demo.get("age_max")):
        raise ConfigurationIncomplete(
            "tranche d'âge non tranchée dans meta_ads_ciblage.json → demographie "
            "(35-70 selon brand_guidelines.md, 30-76 selon PE-EXC-001 — "
            "STATUT_PROJET.md point 2)")

    zones = ciblage.get("zones") or {}
    vides = [c for c, z in zones.items() if not (z or {}).get("quartiers")]
    if vides:
        raise ConfigurationIncomplete(
            f"zone(s) {', '.join(sorted(vides))} sans quartiers dans meta_ads_ciblage.json")

    somme = sum(int((z or {}).get("ponderation_pct") or 0) for z in zones.values())
    if somme != 100:
        raise ConfigurationIncomplete(
            f"les pondérations de zones totalisent {somme} % au lieu de 100 %")

    return {
        "geo_locations": {
            "cities": sorted({q for z in zones.values() for q in (z.get("quartiers") or [])}),
            "countries": ciblage.get("pays") or ["CM"],
        },
        "age_min": demo.get("age_min"),
        "age_max": demo.get("age_max"),
        "locales": ciblage.get("langues") or ["fr"],
        "_ponderation_zones": {c: z.get("ponderation_pct") for c, z in zones.items()},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Construction des objets
# ─────────────────────────────────────────────────────────────────────────────

def construire(repo: Path, chemin_brief: Path) -> dict:
    """Construit les trois objets API. Ne les envoie pas.

    Lève une exception typée dès qu'une valeur manque ou viole une règle — jamais
    de valeur de repli plausible : c'est le mécanisme qui empêche une campagne de
    partir sur une supposition.
    """
    meta, corps = lire_front_matter(chemin_brief)
    if meta is None:
        raise ConfigurationIncomplete(f"{chemin_brief} : front-matter illisible ou absent")

    comptes, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_comptes.json")
    if err:
        raise ConfigurationIncomplete(f"meta_ads_comptes.json : {err}")

    ad_account = comptes.get("ad_account_id")
    if est_vide(ad_account):
        raise ConfigurationIncomplete(
            "ad_account_id null dans meta_ads_comptes.json — identifiant Meta réel à "
            "obtenir de M. NDOMMIE ou du Business Manager AORA. Jamais deviné, jamais "
            "découvert par listing d'API : un compte atteignable n'est pas un compte "
            "autorisé")

    placements = valider_placements(meta)
    if "instagram" in placements and est_vide(comptes.get("instagram_actor_id")):
        raise ConfigurationIncomplete(
            "placement Instagram demandé mais instagram_actor_id null dans "
            "meta_ads_comptes.json")

    # Boost = promouvoir un post organique déjà publié, plutôt qu'un créatif
    # neuf. Le texte, le "creatif_ref" et l'empreinte d'idempotence viennent du
    # post référencé, jamais du brief lui-même — le brief ne fait que déclarer
    # QUOI booster, QUAND, et avec QUEL budget.
    est_boost = str(meta.get("type_campagne", "")).strip().lower() == "boost"
    post_meta = None
    if est_boost:
        ok, motif, post_meta = post_organique_boostable(repo, meta.get("post_ref"))
        if not ok:
            raise PostNonBoostable(motif)
        _, corps_post = lire_front_matter(repo / str(meta["post_ref"]).strip())
        corps_effectif = corps_post
        creatif_ref_effectif = f"boost:{meta['post_ref']}:{post_meta['plateforme_post_id']}"
        nom_defaut = f"Boost — {post_meta.get('id', meta['post_ref'])}"
    else:
        corps_effectif = corps
        creatif_ref_effectif = meta.get("creatif_ref")
        nom_defaut = None

    valider_texte(repo, corps_effectif)
    numero = valider_whatsapp(repo, meta.get("whatsapp_numero"))
    budget = valider_budget(repo, meta)
    ciblage = construire_ciblage(repo)
    devise = comptes.get("devise_compte")

    debut = str(meta.get("date_debut", "")).strip()
    if not debut:
        raise ConfigurationIncomplete("date_debut non renseignée dans le brief")
    lancement_utc = heure_utc(debut, meta.get("heure_debut", "06:00"))
    fin_utc = None
    if not est_vide(meta.get("date_fin")):
        fin_utc = heure_utc(str(meta["date_fin"]).strip(), meta.get("heure_fin", "23:59"))

    nom = str(meta.get("nom") or nom_defaut or meta.get("id") or chemin_brief.stem).strip()
    empreinte = empreinte_creatif({**meta, "creatif_ref": creatif_ref_effectif}, corps_effectif)
    cle = cle_idempotence(str(ad_account), empreinte, lancement_utc)

    campagne = {
        "name": f"EXC+ · {nom}",
        # Click-to-WhatsApp : l'objectif porte les conversations, pas le trafic.
        "objective": "OUTCOME_ENGAGEMENT",
        # PAUSED à la création, toujours. L'activation est un geste distinct et
        # explicite : créer et dépenser ne doivent jamais être la même action.
        "status": "PAUSED",
        "special_ad_categories": [],
    }

    adset = {
        "name": f"EXC+ · {nom} · Yaoundé",
        "optimization_goal": "CONVERSATIONS",
        "billing_event": "IMPRESSIONS",
        "destination_type": "WHATSAPP",
        "promoted_object": {"page_id": str(comptes["page_id"])},
        "targeting": {
            **ciblage,
            "publisher_platforms": placements,
        },
        "start_time": lancement_utc,
        "status": "PAUSED",
    }
    if fin_utc:
        adset["end_time"] = fin_utc
    if budget["budget_quotidien_fcfa"]:
        adset["daily_budget"] = montant_api(budget["budget_quotidien_fcfa"], devise)
    if budget["budget_total_fcfa"]:
        adset["lifetime_budget"] = montant_api(budget["budget_total_fcfa"], devise)

    lien_wa = "https://wa.me/" + "".join(c for c in numero if c.isdigit())

    if est_boost:
        # object_story_id référence le post déjà publié : {page_id}_{post_id}.
        # Aucun link_data neuf n'est construit — le contenu du post organique
        # n'est jamais retouché, seulement enveloppé dans un objet publicitaire.
        creatif = {
            "name": f"EXC+ · boost {post_meta.get('id', '')}",
            "object_story_id": f"{comptes['page_id']}_{post_meta['plateforme_post_id']}",
        }
    else:
        story = {
            "page_id": str(comptes["page_id"]),
            "link_data": {
                "message": corps_effectif.strip(),
                "link": lien_wa,
                "call_to_action": {
                    "type": "WHATSAPP_MESSAGE",
                    "value": {"app_destination": "WHATSAPP", "link": lien_wa},
                },
            },
        }
        if "instagram" in placements:
            story["instagram_actor_id"] = str(comptes["instagram_actor_id"])
        creatif = {"name": f"EXC+ · créatif {creatif_ref_effectif}", "object_story_spec": story}

    annonce = {"name": f"EXC+ · annonce {nom}", "status": "PAUSED"}

    return {
        "meta_brief": {
            "id": meta.get("id"),
            "type_campagne": "boost" if est_boost else "campagne",
            "creatif_ref": creatif_ref_effectif,
            "post_ref": meta.get("post_ref") if est_boost else None,
            "fichier": str(chemin_brief),
            "numero_whatsapp": numero,
            "devise_compte": devise,
        },
        "idempotence": {
            "cle": cle,
            "empreinte_creatif": empreinte,
            "ad_account_id": str(ad_account),
            "lancement_utc": lancement_utc,
        },
        "budget": budget,
        "endpoints": {
            "campaign": f"https://graph.facebook.com/{API_VERSION}/act_{str(ad_account).replace('act_', '')}/campaigns",
            "adset": f"https://graph.facebook.com/{API_VERSION}/act_{str(ad_account).replace('act_', '')}/adsets",
            "adcreative": f"https://graph.facebook.com/{API_VERSION}/act_{str(ad_account).replace('act_', '')}/adcreatives",
            "ad": f"https://graph.facebook.com/{API_VERSION}/act_{str(ad_account).replace('act_', '')}/ads",
        },
        "campaign": campagne,
        "adset": adset,
        "adcreative": creatif,
        "ad": annonce,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Construit une campagne Meta Ads — dry-run par défaut.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--campagne", type=Path, required=True, help="Brief de campagne (.md)")
    ap.add_argument("--mois", type=str, default=None, help="Mois évalué AAAA-MM (test)")
    ap.add_argument("--executer", action="store_true",
                    help="Exécution réelle — refusée si une porte est fermée")
    ap.add_argument("--json", action="store_true", help="Sortie machine")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not args.campagne.is_file():
        print(f"❌ brief introuvable : {args.campagne}", file=sys.stderr)
        return 2

    jour = None
    if args.mois:
        from verifier_activation import mois_depuis_argument
        jour = mois_depuis_argument(args.mois)

    # Les portes d'abord, toujours — avant même de lire le brief en détail.
    if args.executer:
        try:
            exiger_portes_ouvertes(repo, jour=jour, campagne=args.campagne)
        except PortesFermees as err:
            print("\n⛔ EXÉCUTION REFUSÉE — --executer ne contourne aucune porte.\n",
                  file=sys.stderr)
            afficher(verifier_portes(repo, jour=jour, campagne=args.campagne, tout=True),
                     jour or date.today(), args.campagne)
            print(f"❌ {err}\n", file=sys.stderr)
            return 1

    try:
        objets = construire(repo, args.campagne)
    except (BudgetRefuse, CreatifRefuse, ConfigurationIncomplete, PostNonBoostable) as err:
        etiquette = {"BudgetRefuse": "BUDGET REFUSÉ",
                     "CreatifRefuse": "CRÉATIF REFUSÉ",
                     "ConfigurationIncomplete": "CONFIGURATION INCOMPLÈTE",
                     "PostNonBoostable": "POST NON BOOSTABLE"}[type(err).__name__]
        print(f"\n⛔ {etiquette} — {err}\n", file=sys.stderr)
        print("   Aucun objet construit, aucun appel API tenté.\n", file=sys.stderr)
        return 1

    if args.json:
        # Sortie machine : uniquement du JSON sur stdout, pour rester pipeable.
        print(json.dumps(objets, ensure_ascii=False, indent=2))
        return 0

    print(f"\n🧱 CAMPAGNE CONSTRUITE (dry-run) — {objets['meta_brief']['id']}\n")
    print(f"   Clé d'idempotence : {objets['idempotence']['cle']}")
    print(f"   Lancement          : {objets['idempotence']['lancement_utc']} (UTC)")
    print(f"   Plafond mensuel    : {fcfa(objets['budget']['plafond_mensuel_fcfa'])}")
    print(f"   WhatsApp           : {objets['meta_brief']['numero_whatsapp']}")
    print(f"   Placements         : {objets['adset']['targeting']['publisher_platforms']}")
    print(f"\n{json.dumps(objets['campaign'], ensure_ascii=False, indent=2)}\n")

    if not args.executer:
        print("ℹ️  Dry-run — aucun appel API. Ajouter --executer (portes ouvertes requises).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
