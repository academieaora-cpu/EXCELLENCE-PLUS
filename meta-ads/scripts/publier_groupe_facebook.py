#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publier_groupe_facebook.py — Publication organique dans un Groupe Facebook. EXPÉRIMENTAL.

⚠️ CE SCRIPT NE PUBLIE PAS TANT QUE LA FAISABILITÉ N'EST PAS PROUVÉE, GROUPE
PAR GROUPE. Le garde-fou expérimental ci-dessous n'a pas changé et ne doit
jamais être allégé pour "simplifier" une exécution.

Pourquoi cette prudence n'est pas excessive : depuis 2018, Meta restreint
très fortement la publication automatisée dans un Groupe. La permission
`publish_to_groups` n'est quasiment plus accordée à une app tierce — dans
les faits, seule une app détenue par un administrateur du groupe, installée
dans ce groupe, et passée en revue Meta (App Review) peut l'obtenir. Une app
qui n'a pas franchi ces étapes reçoit une erreur de permission, pas un post
publié — c'est ce que le chemin réel ci-dessous rencontrera aujourd'hui pour
tout groupe qui n'a pas ces cinq preuves.

Conséquence pour l'équipe : ne jamais présenter cette fonctionnalité à
M. NDOMMIE comme acquise (interdiction 7). Le circuit reste désactivé par
défaut, avec fallback manuel — pas une promesse de livraison automatique.

Ce qui change dans cette version : le chemin "mode expérimental levé" est
désormais implémenté (appel Graph API réel), au lieu d'imprimer "non
implémenté". Rien ne change dans ce que le script FAIT tant que
`groupes[]` est vide ou que le double drapeau expérimental reste actif —
c'est-à-dire : rien, aujourd'hui, avec la configuration actuelle.

Périmètre budgétaire : ce circuit est ORGANIQUE. Il ne dépense rien et ne
touche ni le budget média Meta Ads ni le forfait AORA. Il est logé dans
meta-ads/ parce qu'il partage la surface d'API Meta, pas parce qu'il
consomme du budget.

Usage :
    python3 meta-ads/scripts/publier_groupe_facebook.py --texte "…"
    python3 meta-ads/scripts/publier_groupe_facebook.py --groupe <group_id> --post <post.md>
    python3 meta-ads/scripts/publier_groupe_facebook.py --groupe <group_id> --post <post.md> --executer
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_activation import est_vide, lire_json  # noqa: E402
from graph_organique import (  # noqa: E402
    ContenuRefuse, ErreurNonClassee, PermissionRefusee, RateLimitPersistant,
    TokenInvalide, alerter, appeler, lire_front_matter,
)

# Drapeau en dur, doublé du drapeau de configuration. Passer la publication
# en réel suppose d'éditer CE fichier ET meta_ads_groupes.json,
# volontairement, en ayant la preuve de faisabilité sous les yeux. Un seul
# interrupteur serait trop facile à basculer par distraction.
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
        description="Publication en Groupe Facebook — réel uniquement hors mode expérimental.")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--groupe", type=str, default=None, help="group_id ciblé")
    ap.add_argument("--texte", type=str, default=None, help="Texte du post (mode manuel)")
    ap.add_argument("--post", type=Path, default=None,
                    help="Fichier de post (front matter) — lit le texte et bap_recu_le")
    ap.add_argument("--bap-ref", type=str, default=None,
                    help="Référence BAP — requise avec --texte si --post n'est pas fourni")
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
        print("   Rien à faire. Le gabarit d'entrée attendu figure dans le fichier")
        print("   de config (_gabarit_entree_groupe).")

    cible = None
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
        if args.groupe and str(g.get("group_id")) == str(args.groupe):
            cible = g

    texte, bap_ref = args.texte, args.bap_ref
    if args.post:
        if not args.post.is_file():
            print(f"\n❌ post introuvable : {args.post}\n", file=sys.stderr)
            return 2
        fm = lire_front_matter(args.post)
        texte = fm.get("_corps") or fm.get("texte", "")
        bap_ref = fm.get("bap_recu_le") or fm.get("bap_email_ref")

    if texte:
        print(f"\n   ── Contenu ──")
        print(f"   Cible : {args.groupe or '(groupe non précisé)'}")
        print(f"   Texte : {texte[:280]}{'…' if len(texte) > 280 else ''}")
        print(f"   BAP   : {bap_ref or '❌ absente'}")

    if EXPERIMENTAL or experimental_config:
        print("\n   ⛔ SIMULATION UNIQUEMENT — aucun appel API effectué.")
        if args.executer:
            print("      --executer est ignoré : le mode expérimental n'est pas une")
            print("      option de ligne de commande, il se lève dans le code et dans")
            print("      la configuration, preuve technique à l'appui.")
        print("\n   Pour publier aujourd'hui : un humain poste dans le groupe, à la main.")
        print("   C'est le fallback prévu, pas un contournement.\n")
        return 0

    # ── Mode expérimental levé (code ET config) ──────────────────────────
    # L'appel réel n'est tenté que pour le groupe explicitement ciblé, avec
    # preuve complète, BAP au dossier, et --executer. Une condition
    # manquante refuse — elle ne simule pas non plus : au-delà du mode
    # expérimental, un refus doit être un refus, pas un silence.
    if not args.groupe:
        print("\n   ⛔ Mode expérimental levé mais --groupe non précisé — refusé.\n",
              file=sys.stderr)
        return 1
    if cible is None:
        print(f"\n   ⛔ Groupe {args.groupe} absent de meta_ads_groupes.json → groupes[] "
              f"— refusé.\n", file=sys.stderr)
        return 1
    ok, manquants = preuve_complete(cible)
    if not ok:
        print(f"\n   ⛔ Preuve de faisabilité incomplète pour ce groupe — manque "
              f"{', '.join(manquants)}. Refusé.\n", file=sys.stderr)
        return 1
    if cible.get("publication_auto_disponible") is not True:
        print("\n   ⛔ publication_auto_disponible n'est pas true pour ce groupe — "
              "refusé, même preuve complète.\n", file=sys.stderr)
        return 1
    if not texte:
        print("\n   ⛔ Aucun texte fourni (--texte ou --post) — refusé.\n", file=sys.stderr)
        return 1
    if not (bap_ref or "").strip():
        print(f"\n   ⛔ Aucune BAP au dossier pour {args.groupe} — via --post "
              f"(bap_recu_le) ou --bap-ref. Refusé.\n", file=sys.stderr)
        return 1
    if not args.executer:
        print("\n   🧪 DRY-RUN — rien n'a été envoyé. Ajouter --executer.\n")
        return 0

    token = os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip()
    if not token:
        msg = "`META_PAGE_ACCESS_TOKEN` absent — aucune publication tentée."
        print(f"\n   ⛔ {msg}\n", file=sys.stderr)
        alerter(f"⛔ {msg}\nGroupe `{args.groupe}`.")
        return 1

    try:
        reponse = appeler(f"{args.groupe}/feed", {"message": texte}, token)
    except (TokenInvalide, PermissionRefusee, ContenuRefuse,
            RateLimitPersistant, ErreurNonClassee) as e:
        alerter(f"🚫 *{type(e).__name__}* — `{e}`\nGroupe `{args.groupe}` — post refusé.\n"
                f"Rappel : `publish_to_groups` est rarement accordée par Meta — une "
                f"{type(e).__name__} ici n'est pas nécessairement un bug de ce script.")
        print(f"\n   ⛔ {type(e).__name__} — {e}\n", file=sys.stderr)
        return 1

    meta_id = reponse.get("id")
    alerter(f"✅ Publié dans le groupe `{cible.get('nom')}` (`{args.groupe}`) → `{meta_id}`")
    print(f"\n   ✅ Publié — {meta_id}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
