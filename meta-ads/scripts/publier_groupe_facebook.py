#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publier_groupe_facebook.py — Publication organique dans un Groupe Facebook. EXPÉRIMENTAL.

⚠️ CE SCRIPT NE PUBLIE PAS, ET NE PUBLIERA PAS TANT QUE LA FAISABILITÉ N'EST PAS
PROUVÉE. Il simule : il construit et affiche ce qui partirait, sans appeler l'API.

Pourquoi cette prudence n'est pas excessive : depuis 2018, Meta restreint très
fortement la publication automatisée dans un Groupe. La permission
`publish_to_groups` n'est quasiment plus accordée à une app tierce — dans les
faits, seule une app détenue par un administrateur du groupe, installée dans ce
groupe, et passée en revue Meta (App Review) peut l'obtenir. Une app qui n'a pas
franchi ces étapes reçoit une erreur de permission, pas un post publié.

Conséquence pour l'équipe : ne jamais présenter cette fonctionnalité à
M. NDOMMIE comme acquise (interdiction 7). Le circuit existe ici en mode
expérimental, désactivé par défaut, avec fallback manuel — pas en promesse de
livraison automatique.

Périmètre budgétaire : ce circuit est ORGANIQUE. Il ne dépense rien et ne touche
ni le budget média Meta Ads ni le forfait AORA. Il est logé dans meta-ads/ parce
qu'il partage la surface d'API Meta, pas parce qu'il consomme du budget.

Usage :
    python3 meta-ads/scripts/publier_groupe_facebook.py --texte "…"
    python3 meta-ads/scripts/publier_groupe_facebook.py --groupe <group_id> --texte "…"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_activation import est_vide, lire_json  # noqa: E402

# Drapeau en dur, doublé du drapeau de configuration. Passer la publication en
# réel suppose d'éditer CE fichier ET meta_ads_groupes.json, volontairement, en
# ayant la preuve de faisabilité sous les yeux. Un seul interrupteur serait trop
# facile à basculer par distraction.
EXPERIMENTAL = True

# Les cinq éléments qui constituent une preuve de faisabilité. Une preuve
# incomplète n'est pas une preuve : c'est une supposition mieux rédigée.
PREUVE_REQUISE = [
    "app_id",
    "permission_publish_to_groups_obtenue_le",
    "reference_app_review",
    "app_installee_par_admin_groupe",
    "post_test_identifiant",
]


def etat_groupes(repo: Path):
    data, err = lire_json(repo / "meta-ads" / "config" / "meta_ads_groupes.json")
    if err:
        return None, err
    return data, None


def preuve_complete(groupe: dict):
    """Retourne (ok, manquants). Aucune tolérance : les 5 éléments ou rien."""
    preuve = groupe.get("preuve_faisabilite")
    if not isinstance(preuve, dict):
        return False, list(PREUVE_REQUISE)
    return (not [c for c in PREUVE_REQUISE if est_vide(preuve.get(c))],
            [c for c in PREUVE_REQUISE if est_vide(preuve.get(c))])


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Publication en Groupe Facebook — EXPÉRIMENTAL, simulation uniquement.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--groupe", type=str, default=None, help="group_id ciblé")
    ap.add_argument("--texte", type=str, default=None, help="Texte du post")
    ap.add_argument("--executer", action="store_true",
                    help="Sans effet tant que le mode expérimental est actif")
    args = ap.parse_args()

    repo = args.repo.resolve()
    data, err = etat_groupes(repo)
    if err:
        print(f"❌ meta_ads_groupes.json : {err}", file=sys.stderr)
        return 2

    experimental_config = data.get("experimental") is not False
    groupes = data.get("groupes") or []

    print("\n🧪 PUBLICATION EN GROUPE FACEBOOK — MODE EXPÉRIMENTAL\n")
    print(f"   Drapeau en dur (script)        : EXPERIMENTAL = {EXPERIMENTAL}")
    print(f"   Drapeau de configuration       : experimental = {data.get('experimental')}")
    print(f"   Groupes déclarés               : {len(groupes)}")

    if not groupes:
        print("\n   Aucun groupe déclaré dans meta_ads_groupes.json → groupes[].")
        print("   Rien à simuler. Le gabarit d'entrée attendu figure dans le fichier")
        print("   de config (_gabarit_entree_groupe).")

    for g in groupes:
        ok, manquants = preuve_complete(g)
        auto = g.get("publication_auto_disponible") is True
        print(f"\n   • {g.get('nom', '(sans nom)')} — group_id {g.get('group_id')}")
        print(f"     publication_auto_disponible : {auto}")
        if ok:
            print("     preuve de faisabilité       : ✅ complète (5/5)")
        else:
            print(f"     preuve de faisabilité       : ❌ incomplète — manque "
                  f"{', '.join(manquants)}")
        if auto and not ok:
            # Incohérence sérieuse : quelqu'un a activé l'auto sans la preuve.
            print("     ⚠️ CRITIQUE — publication_auto_disponible = true SANS preuve "
                  "complète.")
            print("        Cet écart doit être corrigé avant toute sortie du mode "
                  "expérimental.")
        print(f"     fallback                    : {g.get('fallback', 'publication manuelle')}")

    if args.texte:
        cible = args.groupe or "(groupe non précisé)"
        print(f"\n   ── Simulation ──")
        print(f"   Cible : {cible}")
        print(f"   Texte : {args.texte[:280]}{'…' if len(args.texte) > 280 else ''}")

    if EXPERIMENTAL or experimental_config:
        print("\n   ⛔ SIMULATION UNIQUEMENT — aucun appel API effectué.")
        if args.executer:
            print("      --executer est ignoré : le mode expérimental n'est pas une")
            print("      option de ligne de commande, il se lève dans le code et dans")
            print("      la configuration, preuve technique à l'appui.")
        print("\n   Pour publier aujourd'hui : un humain poste dans le groupe, à la main.")
        print("   C'est le fallback prévu, pas un contournement.\n")
        return 0

    # Chemin volontairement non implémenté. L'écrire « au cas où » donnerait
    # l'illusion d'une capacité qui n'existe pas et que Meta n'accorde pas.
    print("\n   ⛔ Mode expérimental levé, mais l'appel réel n'est pas implémenté.")
    print("      À implémenter uniquement le jour où la permission publish_to_groups")
    print("      est réellement accordée, contre preuve documentée — pas avant.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
