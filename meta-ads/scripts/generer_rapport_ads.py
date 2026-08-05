#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_rapport_ads.py — État des campagnes Meta Ads. Vocabulaire strict.

Les quatre mots ne sont pas interchangeables, et ce script ne les échange jamais :

  « programmée »  créée dans Meta, diffusion future. Rien n'est dépensé.
  « active »      en diffusion réelle, de l'argent part en ce moment.
  « terminée »    date de fin atteinte ou budget épuisé.
  « en ligne »    employé UNIQUEMENT après confirmation par l'API que le statut
                  Meta est ACTIVE — jamais déduit d'un appel de création réussi.

Un appel de création qui réussit prouve que Meta a accepté l'objet, rien de plus.
La campagne est créée en PAUSED ; entre « créée » et « en diffusion » il y a une
activation, une revue publicitaire, et un budget qui commence à courir. Confondre
les deux fait croire à l'équipe qu'un contrôle existe là où il n'y en a pas —
c'est exactement l'écart que le contrôle 5 de superviseur-publication-aora
signale côté organique.

Par défaut, ce script lit le dépôt et n'appelle rien : il rapporte donc des
statuts DÉCLARÉS, et le dit. Avec --confirmer-api, il interroge l'API en lecture
seule (GET) pour obtenir les statuts réels. Lire n'est pas dépenser — mais lire
demande quand même un compte et un token, donc reste optionnel.

Usage :
    python3 meta-ads/scripts/generer_rapport_ads.py
    python3 meta-ads/scripts/generer_rapport_ads.py --confirmer-api
    python3 meta-ads/scripts/generer_rapport_ads.py --slack
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_activation import (  # noqa: E402
    cle_mois,
    est_vide,
    lire_json,
    toutes_ouvertes,
    verifier_portes,
)
from verifier_conformite_ads import PREFIXE_GABARIT, campagnes  # noqa: E402

API_VERSION = "v21.0"

# Correspondance dossier → mot autorisé. Le dossier dit où en est le processus
# interne ; il ne prouve rien sur l'état réel chez Meta.
MOT_PAR_DOSSIER = {
    "en_preparation": "en préparation",
    "autorisees": "autorisée (non créée chez Meta)",
    "actives": "programmée",   # « active » exige une confirmation d'API, pas un dossier
    "terminees": "terminée",
}


def statut_meta(campaign_id: str, token: str):
    """GET lecture seule du statut réel. Retourne (statut, erreur)."""
    url = (f"https://graph.facebook.com/{API_VERSION}/{campaign_id}?"
           + urllib.parse.urlencode({"fields": "status,effective_status,name",
                                     "access_token": token}))
    try:
        with urllib.request.urlopen(url, timeout=20) as rep:
            data = json.loads(rep.read().decode("utf-8", errors="replace"))
            return data.get("effective_status") or data.get("status"), None
    except urllib.error.HTTPError as err:
        brut = err.read().decode("utf-8", errors="replace")
        return None, f"HTTP {err.code} — {brut[:200]}"
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        return None, str(err)


def main() -> int:
    ap = argparse.ArgumentParser(description="Rapport d'état des campagnes Meta Ads.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--confirmer-api", action="store_true",
                    help="Interroge l'API en lecture seule pour obtenir les statuts réels")
    ap.add_argument("--slack", action="store_true", help="Poste le rapport dans le fil Meta Ads")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "meta-ads").is_dir():
        print(f"❌ {repo / 'meta-ads'} introuvable.", file=sys.stderr)
        return 2

    aujourdhui = date.today()
    portes = verifier_portes(repo, tout=True)
    budgets, _ = lire_json(repo / "meta-ads" / "config" / "meta_ads_budgets.json")
    registre, err_registre = lire_json(
        repo / "meta-ads" / "campagnes" / "registre_idempotence.json")
    cles = (registre or {}).get("cles", {}) if not err_registre else {}

    liste = campagnes(repo)
    gabarits = 0
    for dossier in ("en_preparation", "autorisees", "actives", "terminees"):
        base = repo / "meta-ads" / "campagnes" / dossier
        if base.is_dir():
            for chemin in base.glob("*.md"):
                texte = chemin.read_text(encoding="utf-8", errors="replace")
                if f"id: {PREFIXE_GABARIT}" in texte:
                    gabarits += 1

    par_dossier = {d: [] for d in MOT_PAR_DOSSIER}
    for dossier, chemin, meta, _ in liste:
        par_dossier[dossier].append((chemin, meta))

    confirmations = {}
    if args.confirmer_api:
        token = os.environ.get("META_MARKETING_TOKEN", "").strip()
        if not token:
            confirmations["_erreur"] = ("META_MARKETING_TOKEN absent — statuts réels non "
                                        "vérifiables, le rapport reste déclaratif")
        elif not cles:
            confirmations["_erreur"] = ("aucune campagne au registre d'idempotence — rien "
                                        "à confirmer auprès de l'API")
        else:
            for cle, info in cles.items():
                cid = (info.get("identifiants") or {}).get("campaign_id")
                if cid:
                    statut, err = statut_meta(cid, token)
                    confirmations[cle] = {"campaign_id": cid, "statut": statut, "erreur": err}

    lignes = []
    lignes.append(f"\n📊 RAPPORT META ADS — {aujourdhui.strftime('%d/%m/%Y')} "
                  f"(mois {cle_mois(aujourdhui)})\n")

    etat_portes = "ouvertes" if toutes_ouvertes(portes) else "FERMÉES"
    fermees = [p.numero for p in portes if not p.ouverte]
    lignes.append(f"   Portes : {etat_portes}"
                  + (f" — porte(s) {', '.join(map(str, fermees))}" if fermees else ""))

    plafond = (budgets or {}).get("montant_mensuel_fcfa")
    scenario = (budgets or {}).get("scenario_retenu")
    if est_vide(plafond):
        lignes.append("   Budget : aucun plafond autorisé — aucune campagne ne peut être "
                      "créée (porte 2 fermée)")
    else:
        lignes.append(f"   Budget : scénario « {scenario} », plafond {plafond} FCFA/mois")

    lignes.append("")
    total_reelles = sum(len(v) for v in par_dossier.values())
    if total_reelles == 0:
        lignes.append("   Aucune campagne réelle dans meta-ads/campagnes/."
                      + (f" ({gabarits} gabarit(s) ignoré(s))" if gabarits else ""))
        lignes.append("   Rien n'est programmé, rien n'est actif, rien n'est dépensé.")
    else:
        for dossier, mot in MOT_PAR_DOSSIER.items():
            entrees = par_dossier[dossier]
            if not entrees:
                continue
            lignes.append(f"   {mot.upper()} ({len(entrees)})")
            for chemin, meta in entrees:
                ligne = f"      · {meta.get('id')} — {meta.get('nom', '')}"
                confirme = meta.get("statut_meta_confirme_le")
                if dossier == "actives":
                    if est_vide(confirme):
                        ligne += ("  [statut Meta NON confirmé — dite « programmée », "
                                  "pas « en ligne »]")
                    else:
                        ligne += f"  [statut Meta confirmé le {confirme}]"
                lignes.append(ligne)
            lignes.append("")

    if args.confirmer_api:
        lignes.append("   ── Confirmation API (lecture seule) ──")
        if "_erreur" in confirmations:
            lignes.append(f"      ⚠️ {confirmations['_erreur']}")
        for cle, info in confirmations.items():
            if cle == "_erreur":
                continue
            if info.get("erreur"):
                lignes.append(f"      · {info['campaign_id']} — non vérifiable : "
                              f"{info['erreur']}")
            else:
                statut = info.get("statut")
                mot = "EN LIGNE" if statut == "ACTIVE" else f"statut Meta « {statut} »"
                lignes.append(f"      · {info['campaign_id']} — {mot}")
        lignes.append("")
    else:
        lignes.append("   ℹ️  Statuts DÉCLARÉS (lecture du dépôt). Aucun n'est confirmé "
                      "auprès de Meta :")
        lignes.append("      relancer avec --confirmer-api pour un statut réel. Sans cela, "
                      "aucune")
        lignes.append("      campagne ne peut être dite « en ligne ».")
        lignes.append("")

    # Rappel de séparation budgétaire — deux systèmes de suivi, jamais un seul tableau.
    lignes.append("   Le budget média Meta Ads ci-dessus est distinct du forfait de "
                  "gestion AORA")
    lignes.append("   (facturation AORA-EXCPLUS-2026-001). Les deux ne se cumulent ni ne "
                  "se compensent.")
    lignes.append("")

    rapport = "\n".join(lignes)

    if args.json:
        print(json.dumps({
            "date": aujourdhui.isoformat(),
            "portes_toutes_ouvertes": toutes_ouvertes(portes),
            "portes_fermees": fermees,
            "plafond_mensuel_fcfa": plafond,
            "scenario_retenu": scenario,
            "campagnes": {d: [str(m.get("id")) for _, m in v] for d, v in par_dossier.items()},
            "gabarits_ignores": gabarits,
            "confirmations_api": confirmations,
            "_vocabulaire": {
                "programmee": "créée dans Meta, diffusion future",
                "active": "en diffusion réelle, budget en cours de consommation",
                "terminee": "date de fin atteinte ou budget épuisé",
                "en_ligne": "réservé au statut Meta ACTIVE confirmé par appel API",
            },
        }, ensure_ascii=False, indent=2))
    else:
        print(rapport)

    if args.slack:
        from publier_ads_facebook import alerter
        alerter(rapport)

    return 0


if __name__ == "__main__":
    sys.exit(main())
