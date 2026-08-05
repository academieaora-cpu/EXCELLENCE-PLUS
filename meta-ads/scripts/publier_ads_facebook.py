#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publier_ads_facebook.py — Exécution réelle d'une campagne Meta Ads (placement Facebook).

C'est le seul fichier du pipeline qui contient un appel HTTP vers l'API Marketing
de Meta. `publier_ads_instagram.py` importe ce moteur au lieu de le recopier : les
deux placements passent par le même compte publicitaire et les mêmes endpoints
Graph, et une politique de retry écrite à deux endroits finirait par diverger —
sur de l'argent réel, cette divergence se paie.

Rien ne part sans, dans cet ordre :

  1. les quatre portes de verifier_activation.py, toutes ouvertes ;
  2. le drapeau explicite --executer ;
  3. une clé d'idempotence (ad_account_id, empreinte du créatif, lancement UTC)
     absente du registre ;
  4. un plafond budgétaire respecté, vérifié avant l'appel — jamais après le
     refus de Meta.

Politiques d'échec typées — jamais un except générique. Une erreur qu'on ne sait
pas nommer est une erreur qu'on ne sait pas traiter : elle s'arrête et alerte.

Usage :
    python3 meta-ads/scripts/publier_ads_facebook.py --campagne <brief.md>
    python3 meta-ads/scripts/publier_ads_facebook.py --campagne <brief.md> --executer
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construire_campagne import (  # noqa: E402
    BudgetRefuse,
    ConfigurationIncomplete,
    CreatifRefuse,
    construire,
    enregistrer_cle,
    lire_registre,
)
from verifier_activation import (  # noqa: E402
    PortesFermees,
    afficher,
    exiger_portes_ouvertes,
    verifier_portes,
)

# Plafond de tentatives sur rate limit. Au-delà, on alerte plutôt que d'insister :
# une boucle de retry qui ne s'arrête jamais finit par ressembler à une attaque.
MAX_TENTATIVES = 4
BACKOFF_SECONDES = [2, 4, 8, 16]

# Codes d'erreur Meta regroupés par politique de traitement.
CODES_TOKEN = {102, 190, 463, 467}
CODES_RATE_LIMIT = {4, 17, 32, 613, 80000, 80004}
CODES_PERMISSION = {200, 294, 10}


class TokenInvalide(RuntimeError):
    """Token expiré ou révoqué — alerte, arrêt, aucun retry automatique."""


class BudgetRejeteParMeta(RuntimeError):
    """Budget refusé par l'API — alerte, aucun ajustement automatique du montant."""


class CreatifRefuseEnRevue(RuntimeError):
    """Créatif refusé en revue publicitaire — alerte avec motif exact, pas de re-soumission."""


class RateLimitPersistant(RuntimeError):
    """Rate limit non résolu après le plafond de tentatives — alerte."""


class ErreurMetaNonClassee(RuntimeError):
    """Erreur API que ce script ne sait pas nommer — arrêt franc, pas de supposition."""


# ─────────────────────────────────────────────────────────────────────────────
# Slack — fil dédié Meta Ads, secrets distincts de ceux du pipeline organique
# ─────────────────────────────────────────────────────────────────────────────

def alerter(message: str) -> bool:
    """Poste dans le fil Meta Ads. Secrets propres, jamais ceux de Composio.

    Un budget et un post organique ne se surveillent pas dans le même fil :
    mélanger les deux, c'est finir par ne plus lire ni l'un ni l'autre.
    """
    message = f"💸 *META ADS · Excellence+*\n{message}"
    webhook = os.environ.get("SLACK_WEBHOOK_URL_METAADS", "").strip()
    jeton = os.environ.get("SLACK_BOT_TOKEN_METAADS", "").strip()
    canal = os.environ.get("SLACK_CHANNEL_METAADS", "").strip()

    if webhook:
        url, entetes, corps = webhook, {"Content-Type": "application/json"}, {"text": message}
    elif jeton and canal:
        url = "https://slack.com/api/chat.postMessage"
        entetes = {"Content-Type": "application/json; charset=utf-8",
                   "Authorization": f"Bearer {jeton}"}
        corps = {"channel": canal, "text": message}
    else:
        print("⚠️  Slack Meta Ads non configuré (SLACK_WEBHOOK_URL_METAADS ou "
              "SLACK_BOT_TOKEN_METAADS + SLACK_CHANNEL_METAADS) — alerte non envoyée :",
              file=sys.stderr)
        print(message, file=sys.stderr)
        return False

    requete = urllib.request.Request(url, data=json.dumps(corps).encode("utf-8"),
                                     headers=entetes)
    try:
        with urllib.request.urlopen(requete, timeout=15) as rep:
            return 200 <= rep.status < 300
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        print(f"❌ Alerte Slack Meta Ads impossible : {err}", file=sys.stderr)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Appel API — classement typé des échecs
# ─────────────────────────────────────────────────────────────────────────────

def _classer_erreur(charge: dict, statut: int):
    """Traduit une erreur Graph en exception typée. Ne devine jamais."""
    err = (charge or {}).get("error") or {}
    code = err.get("code")
    sous_code = err.get("error_subcode")
    message = err.get("error_user_msg") or err.get("message") or f"HTTP {statut}"
    detail = f"code {code}" + (f"/{sous_code}" if sous_code else "") + f" — {message}"

    if code in CODES_TOKEN:
        return TokenInvalide(detail)
    if code in CODES_RATE_LIMIT:
        return None  # Rejouable : traité par le backoff, pas par une exception.
    if code in CODES_PERMISSION:
        return ErreurMetaNonClassee(
            f"permission refusée ({detail}) — le token n'a pas les droits sur ce compte")

    texte = f"{message} {err.get('error_user_title', '')}".lower()
    if any(m in texte for m in ("budget", "spend cap", "daily_budget", "lifetime_budget",
                                "minimum budget")):
        return BudgetRejeteParMeta(detail)
    if any(m in texte for m in ("policy", "review", "disapprove", "rejected", "ad account "
                                "is disabled", "creative")):
        return CreatifRefuseEnRevue(detail)
    return ErreurMetaNonClassee(detail)


def appeler(url: str, charge: dict, token: str) -> dict:
    """POST Graph avec backoff plafonné sur rate limit uniquement.

    Le backoff ne s'applique qu'au rate limit : réessayer un budget refusé ou un
    token mort ne fait que répéter la même erreur, plus lentement.
    """
    donnees = dict(charge)
    donnees["access_token"] = token
    corps = urllib.parse.urlencode(
        {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in donnees.items()}
    ).encode("utf-8")

    derniere = None
    for tentative in range(MAX_TENTATIVES):
        requete = urllib.request.Request(
            url, data=corps,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(requete, timeout=30) as rep:
                return json.loads(rep.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as err:
            brut = err.read().decode("utf-8", errors="replace")
            try:
                charge_err = json.loads(brut)
            except json.JSONDecodeError:
                charge_err = {"error": {"message": brut[:400]}}
            typee = _classer_erreur(charge_err, err.code)
            if typee is not None:
                raise typee from err
            derniere = charge_err
            if tentative < MAX_TENTATIVES - 1:
                attente = BACKOFF_SECONDES[tentative]
                print(f"   ⏳ rate limit — nouvelle tentative dans {attente}s "
                      f"({tentative + 1}/{MAX_TENTATIVES})")
                time.sleep(attente)
        except urllib.error.URLError as err:
            raise ErreurMetaNonClassee(f"réseau injoignable : {err}") from err

    raise RateLimitPersistant(
        f"rate limit non résolu après {MAX_TENTATIVES} tentatives — "
        f"dernière réponse : {json.dumps(derniere, ensure_ascii=False)[:300]}")


# ─────────────────────────────────────────────────────────────────────────────
# Publication
# ─────────────────────────────────────────────────────────────────────────────

def publier(repo: Path, chemin_brief: Path, plateforme: str, executer: bool,
            jour: date = None) -> int:
    repo = Path(repo).resolve()

    # Porte d'entrée — avant toute lecture de brief, avant tout appel.
    if executer:
        try:
            exiger_portes_ouvertes(repo, jour=jour, campagne=chemin_brief)
        except PortesFermees as err:
            print(f"\n⛔ PUBLICATION {plateforme.upper()} REFUSÉE — "
                  f"--executer ne contourne aucune porte.\n", file=sys.stderr)
            afficher(verifier_portes(repo, jour=jour, campagne=chemin_brief, tout=True),
                     jour or date.today(), chemin_brief)
            print(f"❌ {err}\n", file=sys.stderr)
            return 1

    try:
        objets = construire(repo, chemin_brief)
    except (BudgetRefuse, CreatifRefuse, ConfigurationIncomplete) as err:
        print(f"\n⛔ {type(err).__name__} — {err}\n", file=sys.stderr)
        print("   Aucun appel API tenté.\n", file=sys.stderr)
        return 1

    if plateforme not in objets["adset"]["targeting"]["publisher_platforms"]:
        print(f"\n⛔ Le brief ne déclare pas le placement « {plateforme} » — "
              f"placements demandés : "
              f"{objets['adset']['targeting']['publisher_platforms']}\n", file=sys.stderr)
        return 1

    cle = objets["idempotence"]["cle"]
    deja = lire_registre(repo)
    if cle in deja:
        print(f"\n🕓 DÉJÀ CRÉÉE — clé d'idempotence {cle} présente au registre.")
        print(f"   {json.dumps(deja[cle], ensure_ascii=False, indent=2)}")
        print("   Aucun appel API : recréer cette campagne créerait un second budget.\n")
        return 0

    if not executer:
        print(f"\n🧪 DRY-RUN {plateforme.upper()} — rien n'a été envoyé.")
        print(f"   Clé d'idempotence : {cle}")
        print(f"   Lancement          : {objets['idempotence']['lancement_utc']} (UTC)")
        print(f"   Endpoints visés    : {objets['endpoints']['campaign']}")
        print("\nℹ️  Ajouter --executer pour l'exécution réelle (portes ouvertes requises).\n")
        return 0

    token = os.environ.get("META_MARKETING_TOKEN", "").strip()
    if not token:
        message = ("`META_MARKETING_TOKEN` absent de l'environnement — aucune campagne "
                   "créée. Ce secret est distinct de ceux du pipeline Composio.")
        print(f"\n⛔ {message}\n", file=sys.stderr)
        alerter(f"⛔ *Publication interrompue*\n{message}")
        return 1

    identifiants = {}
    try:
        campagne = appeler(objets["endpoints"]["campaign"], objets["campaign"], token)
        identifiants["campaign_id"] = campagne.get("id")

        adset = dict(objets["adset"])
        adset["campaign_id"] = identifiants["campaign_id"]
        reponse_adset = appeler(objets["endpoints"]["adset"], adset, token)
        identifiants["adset_id"] = reponse_adset.get("id")

        creatif = appeler(objets["endpoints"]["adcreative"], objets["adcreative"], token)
        identifiants["creative_id"] = creatif.get("id")

        annonce = dict(objets["ad"])
        annonce["adset_id"] = identifiants["adset_id"]
        annonce["creative"] = {"creative_id": identifiants["creative_id"]}
        reponse_ad = appeler(objets["endpoints"]["ad"], annonce, token)
        identifiants["ad_id"] = reponse_ad.get("id")

    except TokenInvalide as err:
        alerter(f"🔑 *Token Meta Marketing invalide ou expiré*\n`{err}`\n"
                f"Campagne `{objets['meta_brief']['id']}` non créée. "
                f"Aucun retry automatique — le token doit être renouvelé à la main.")
        print(f"\n⛔ Token invalide — {err}\n", file=sys.stderr)
        return 1
    except BudgetRejeteParMeta as err:
        alerter(f"💰 *Budget rejeté par l'API Meta*\n`{err}`\n"
                f"Campagne `{objets['meta_brief']['id']}` non créée. "
                f"Aucun ajustement automatique du montant : toute modification de "
                f"plafond repasse par une BAB écrite.")
        print(f"\n⛔ Budget rejeté par Meta — {err}\n", file=sys.stderr)
        return 1
    except CreatifRefuseEnRevue as err:
        alerter(f"🚫 *Créatif refusé en revue publicitaire*\nMotif exact renvoyé par "
                f"l'API : `{err}`\nCampagne `{objets['meta_brief']['id']}`. "
                f"Aucune re-soumission automatique.")
        print(f"\n⛔ Créatif refusé — {err}\n", file=sys.stderr)
        return 1
    except RateLimitPersistant as err:
        alerter(f"⏳ *Rate limit Meta non résolu*\n`{err}`\n"
                f"Campagne `{objets['meta_brief']['id']}` non créée.")
        print(f"\n⛔ Rate limit persistant — {err}\n", file=sys.stderr)
        return 1
    except ErreurMetaNonClassee as err:
        alerter(f"❓ *Erreur Meta non classée*\n`{err}`\n"
                f"Campagne `{objets['meta_brief']['id']}`. Arrêt : une erreur que le "
                f"pipeline ne sait pas nommer ne se traite pas automatiquement.")
        print(f"\n⛔ Erreur non classée — {err}\n", file=sys.stderr)
        return 1

    enregistrer_cle(repo, cle, {
        "campagne": objets["meta_brief"]["id"],
        "creatif_ref": objets["meta_brief"]["creatif_ref"],
        "plateforme": plateforme,
        "ad_account_id": objets["idempotence"]["ad_account_id"],
        "lancement_utc": objets["idempotence"]["lancement_utc"],
        "identifiants": identifiants,
        "statut_a_la_creation": "PAUSED",
    })

    # Vocabulaire strict : la campagne est PROGRAMMÉE, pas « en ligne ». Elle est
    # créée en PAUSED — seule une lecture d'API confirmant le statut ACTIVE
    # autoriserait le mot « active » (voir generer_rapport_ads.py).
    alerter(f"✅ *Campagne programmée* `{objets['meta_brief']['id']}`\n"
            f"Statut à la création : `PAUSED` · lancement "
            f"{objets['idempotence']['lancement_utc']} UTC\n"
            f"Identifiants : `{json.dumps(identifiants, ensure_ascii=False)}`")
    print(f"\n✅ Campagne programmée (statut PAUSED) — {identifiants}\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Publie une campagne Meta Ads — placement Facebook.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--campagne", type=Path, required=True)
    ap.add_argument("--mois", type=str, default=None, help="Mois évalué AAAA-MM (test)")
    ap.add_argument("--executer", action="store_true",
                    help="Exécution réelle — refusée si une porte est fermée")
    args = ap.parse_args()

    if not args.campagne.is_file():
        print(f"❌ brief introuvable : {args.campagne}", file=sys.stderr)
        return 2

    jour = None
    if args.mois:
        from verifier_activation import mois_depuis_argument
        jour = mois_depuis_argument(args.mois)

    return publier(args.repo, args.campagne, "facebook", args.executer, jour)


if __name__ == "__main__":
    sys.exit(main())
