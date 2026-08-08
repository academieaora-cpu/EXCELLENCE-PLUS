#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
graph_organique.py — Moteur partagé pour la publication organique directe
sur la surface Graph API de Meta (Page Facebook, compte Instagram, Groupe),
HORS Composio et HORS Marketing API.

Un seul point d'appel HTTP, une seule politique d'erreurs, un seul registre
d'idempotence, importés par publier_facebook_organique.py,
publier_instagram_organique.py et publier_groupe_facebook.py — même logique
que publier_ads_facebook.py qui centralise l'appel Marketing API pour
publier_ads_instagram.py : écrire la même politique à trois endroits finit
par diverger, et sur du contenu public, cette divergence se voit.

Périmètre : ce module ne dépense rien, ne connaît aucun budget, ne touche
aucune des quatre portes Meta Ads. Il est logé dans meta-ads/ parce qu'il
partage la surface d'API Meta, pas parce qu'il consomme du budget — même
remarque que publier_groupe_facebook.py.

Secrets : META_PAGE_ACCESS_TOKEN (jeton Page longue durée, couvre aussi la
publication du compte Instagram lié à la Page). Distinct de
META_MARKETING_TOKEN (Ads) et des jetons Composio — un jeton compromis ne
doit jamais mettre en cause un autre circuit.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSION_API = "v26.0"
BASE = f"https://graph.facebook.com/{VERSION_API}"
REGISTRE = "meta-ads/registre_publication_directe.json"

MAX_TENTATIVES = 4
BACKOFF_SECONDES = [2, 4, 8, 16]

CODES_TOKEN = {102, 190, 463, 467}
CODES_RATE_LIMIT = {4, 17, 32, 613, 80000, 80004}
CODES_PERMISSION = {10, 100, 200, 294}


class TokenInvalide(RuntimeError):
    """Jeton expiré ou révoqué — alerte, arrêt, aucun retry automatique."""


class PermissionRefusee(RuntimeError):
    """Le jeton n'a pas le droit demandé (Page, compte IG, ou Groupe).

    Pour un Groupe, ceci est l'issue attendue tant que `publish_to_groups`
    n'a pas été accordée par Meta — ce n'est pas nécessairement un bug.
    """


class ContenuRefuse(RuntimeError):
    """Meta refuse le contenu — standards de la communauté, format média."""


class RateLimitPersistant(RuntimeError):
    """Rate limit non résolu après le plafond de tentatives."""


class ErreurNonClassee(RuntimeError):
    """Erreur que ce module ne sait pas nommer — arrêt franc, pas de supposition."""


class RouteNonAutorisee(RuntimeError):
    """Le post n'a pas explicitement demandé le canal meta_direct."""


class ApprobationManquante(RuntimeError):
    """Pas de bap_recu_le au dossier — l'exigence BAP ne dépend jamais de l'outil."""


def _classer_erreur(charge: dict, statut: int):
    """Traduit une erreur Graph en exception typée. Ne devine jamais."""
    err = (charge or {}).get("error") or {}
    code = err.get("code")
    sous_code = err.get("error_subcode")
    message = err.get("error_user_msg") or err.get("message") or f"HTTP {statut}"
    detail = f"code {code}" + (f"/{sous_code}" if sous_code else "") + f" — {message}"
    texte = message.lower()

    if code in CODES_TOKEN:
        return TokenInvalide(detail)
    if code in CODES_RATE_LIMIT:
        return None  # rejouable par le backoff, jamais une exception
    if code in CODES_PERMISSION or "publish_to_groups" in texte or "does not have permission" in texte:
        return PermissionRefusee(detail)
    if any(m in texte for m in ("community standard", "policy", "not allowed",
                                "media type", "unsupported", "invalid image")):
        return ContenuRefuse(detail)
    return ErreurNonClassee(detail)


def appeler(chemin: str, donnees: dict, token: str) -> dict:
    """POST Graph API avec backoff plafonné sur rate limit uniquement.

    Réessayer un token mort ou une permission refusée ne fait que répéter la
    même erreur, plus lentement — seul le rate limit est rejouable.
    """
    url = f"{BASE}/{chemin.lstrip('/')}"
    corps_donnees = dict(donnees)
    corps_donnees["access_token"] = token
    corps = urllib.parse.urlencode(corps_donnees).encode("utf-8")

    derniere = None
    for tentative in range(MAX_TENTATIVES):
        requete = urllib.request.Request(
            url, data=corps, headers={"Content-Type": "application/x-www-form-urlencoded"})
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
            raise ErreurNonClassee(f"réseau injoignable : {err}") from err

    raise RateLimitPersistant(
        f"rate limit non résolu après {MAX_TENTATIVES} tentatives — "
        f"dernière réponse : {json.dumps(derniere, ensure_ascii=False)[:300]}")


# ─────────────────────────────────────────────────────────────────────────
# Slack — fil Meta Ads (mêmes secrets), préfixe distinct : rien ici n'a de
# coût média, mais ça reste la surface d'API Meta.
# ─────────────────────────────────────────────────────────────────────────

def alerter(message: str) -> bool:
    message = f"🌱 *META ORGANIQUE DIRECT · Excellence+*\n{message}"
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
        print("⚠️  Slack Meta Ads non configuré — alerte non envoyée :", file=sys.stderr)
        print(message, file=sys.stderr)
        return False

    requete = urllib.request.Request(url, data=json.dumps(corps).encode("utf-8"), headers=entetes)
    try:
        with urllib.request.urlopen(requete, timeout=15) as rep:
            return 200 <= rep.status < 300
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        print(f"❌ Alerte Slack impossible : {err}", file=sys.stderr)
        return False


# ─────────────────────────────────────────────────────────────────────────
# Front matter — parseur minimal, volontairement sans dépendance PyYAML :
# suffisant pour des paires clé: valeur à plat.
# ─────────────────────────────────────────────────────────────────────────

def lire_front_matter(chemin_post: Path) -> dict:
    texte = chemin_post.read_text(encoding="utf-8")
    if not texte.startswith("---"):
        raise ValueError(f"{chemin_post} : pas de front matter YAML détecté")
    fin = texte.find("\n---", 3)
    if fin == -1:
        raise ValueError(f"{chemin_post} : front matter non fermé")
    bloc = texte[3:fin].strip("\n")
    corps = texte[fin + 4:].lstrip("\n")

    donnees = {}
    for ligne in bloc.splitlines():
        if not ligne.strip() or ligne.strip().startswith("#") or ":" not in ligne:
            continue
        cle, _, valeur = ligne.partition(":")
        donnees[cle.strip()] = valeur.strip().strip('"').strip("'")
    donnees["_corps"] = corps.strip()
    return donnees


def verifier_route_et_approbation(fm: dict, post_id: str) -> None:
    """Les deux gardes communes à toute publication organique directe.

    Lève une exception, jamais un simple bool — pour qu'un appelant ne
    puisse pas ignorer le refus par accident.
    """
    if (fm.get("canal_publication") or "composio").strip() != "meta_direct":
        raise RouteNonAutorisee(
            f"{post_id} : canal_publication absent ou = 'composio' — Composio est "
            f"la route par défaut de ce post, le publier ici créerait un doublon. "
            f"Ajouter `canal_publication: meta_direct` au front matter si voulu.")
    if not (fm.get("bap_recu_le") or "").strip():
        raise ApprobationManquante(
            f"{post_id} : aucun bap_recu_le au front matter — pas de BAP, pas de "
            f"publication, route directe ou non.")


# ─────────────────────────────────────────────────────────────────────────
# Registre d'idempotence — partagé Facebook + Instagram : un post_id ne se
# republie pas deux fois, quelle que soit la plateforme visée en second.
# ─────────────────────────────────────────────────────────────────────────

def lire_registre(repo: Path) -> dict:
    chemin = repo / REGISTRE
    if not chemin.is_file():
        return {}
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def enregistrer(repo: Path, cle: str, entree: dict) -> None:
    chemin = repo / REGISTRE
    donnees = lire_registre(repo)
    donnees[cle] = entree
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────
# Config — Page et compte Instagram, jamais devinés.
# ─────────────────────────────────────────────────────────────────────────

def page_id_organique(repo: Path) -> str:
    cible = json.loads((repo / "config" / "page_cible.json").read_text(encoding="utf-8"))
    # Structure réelle du fichier : {"facebook": {"id": "...", ...}} — vérifié
    # contre le dépôt le 07/08/2026, pas supposé.
    facebook = cible.get("facebook") or {}
    id_organique = str(facebook.get("id") or "").strip()
    if not id_organique:
        raise ValueError("config/page_cible.json → facebook.id est absent ou vide.")

    comptes_path = repo / "meta-ads" / "config" / "meta_ads_comptes.json"
    if comptes_path.is_file():
        comptes = json.loads(comptes_path.read_text(encoding="utf-8"))
        id_meta_ads = str(comptes.get("page_id") or "").strip()
        if id_meta_ads and id_meta_ads != id_organique:
            raise ValueError(
                f"page_id divergent : config/page_cible.json={id_organique!r} vs "
                f"meta-ads/config/meta_ads_comptes.json={id_meta_ads!r} — cohérence "
                f"refusée, aucun appel tenté.")
    return id_organique


def instagram_actor_id(repo: Path) -> str:
    comptes = json.loads(
        (repo / "meta-ads" / "config" / "meta_ads_comptes.json").read_text(encoding="utf-8"))
    ig_id = comptes.get("instagram_actor_id")
    if not ig_id or str(ig_id).strip().lower() in ("", "null", "none"):
        raise ValueError(
            "instagram_actor_id absent de meta-ads/config/meta_ads_comptes.json — "
            "identifiant humain requis (Business Manager), jamais deviné.")
    return str(ig_id)


def url_visuel_public(nom_fichier: str, branche: str = "main") -> str:
    """URL publique brute vers un visuel déjà poussé dans visuels/approuves/.

    Le dépôt est public (aucune authentification n'est nécessaire pour le
    cloner) — raw.githubusercontent.com sert donc de CDN gratuit pour ce
    que l'API Instagram exige de toute façon : une URL joignable, jamais un
    fichier local envoyé en octets. Si le visuel n'a pas encore été poussé
    sur `branche`, cette URL ne répondra pas — ce n'est pas une erreur de ce
    module.
    """
    return (f"https://raw.githubusercontent.com/academieaora-cpu/"
            f"EXCELLENCE-PLUS/{branche}/visuels/approuves/{nom_fichier}")
