#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publier_ads_instagram.py — Exécution réelle d'une campagne Meta Ads (placement Instagram).

Ce script ne recopie PAS le moteur de publication : il importe celui de
`publier_ads_facebook.py` et lui passe `plateforme="instagram"`.

Pourquoi : sur la Marketing API, Facebook et Instagram partagent le même compte
publicitaire, les mêmes endpoints Graph et les mêmes objets campaign/adset/ad. Ce
qui change tient en deux points — `publisher_platforms` contient `instagram`, et
l'`object_story_spec` porte un `instagram_actor_id`, tous deux gérés dans
`construire_campagne.py`.

Dupliquer ici la politique de retry, le classement typé des erreurs et le registre
d'idempotence produirait deux copies vouées à diverger. Sur un pipeline qui engage
de l'argent réel, la version qui dérive est celle qu'on ne relit plus.

Prérequis spécifique : `instagram_actor_id` renseigné dans
`meta-ads/config/meta_ads_comptes.json`. Il est null au 05/08/2026 — identifiant
Meta réel à obtenir de M. NDOMMIE ou du Business Manager AORA, jamais à deviner.
`construire_campagne.py` refuse de construire tant qu'il manque.

Rappel calendrier : `config/creneaux.json` → `canaux.activation.instagram` vaut
`2026-09`. Cette date gouverne le pipeline organique ; côté payant, c'est la
porte 1 (`meta_ads_activation.json`) qui fait foi. Les deux doivent rester
cohérentes — un canal organique fermé et une campagne payante ouverte au même
mois est un écart à signaler, pas à arbitrer dans le code.

Usage :
    python3 meta-ads/scripts/publier_ads_instagram.py --campagne <brief.md>
    python3 meta-ads/scripts/publier_ads_instagram.py --campagne <brief.md> --executer
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publier_ads_facebook import publier  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Publie une campagne Meta Ads — placement Instagram.")
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

    return publier(args.repo, args.campagne, "instagram", args.executer, jour)


if __name__ == "__main__":
    sys.exit(main())
