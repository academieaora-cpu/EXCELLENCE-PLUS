#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier_conformite.py — Audit de conformité, exécuté par superviseur-publication-aora.

Ne modifie RIEN dans le dépôt. Relit l'état réel des fichiers — jamais un rapport Slack, jamais
une mémoire de conversation — et vérifie, pour chaque post touché par une programmation
(composio_id ou programme_le renseigné), que les deux garanties absolues du dispositif tiennent
encore, simultanément :

  1. BAP écrit       bap_recu_le ET bap_email_ref renseignés
  2. Visuel approuvé  présent dans visuels/approuves/ pour cet identifiant

Vérifie aussi :
  3. Idempotence      un composio_id ne doit apparaître que sur UN SEUL fichier
  4. Vocabulaire      un statut/texte évoquant une publication réelle sans publie_le renseigné

Ce script ne corrige rien et ne publie rien. Il dit ce qui ne tient pas, pour que
superviseur-publication-aora le rapporte — la décision reste humaine.

Usage :
    python3 scripts/verifier_conformite.py --repo <chemin_du_depot> --horizon 14
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ pyyaml requis (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)


def est_vide(v) -> bool:
    if v is None:
        return True
    return str(v).strip().strip('"').strip("'") in ("", "null", "None", "~", "A_REMPLIR")


def lire_post(chemin: Path):
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


def visuel_existe(repo: Path, meta: dict) -> bool:
    ref = meta.get("visuel_ref")
    if not est_vide(ref):
        candidat = repo / str(ref).strip().strip('"').strip("'")
        if candidat.is_file():
            return True
    approuves = repo / "visuels" / "approuves"
    pid = str(meta.get("id", "")).strip()
    if pid and approuves.is_dir():
        for f in approuves.iterdir():
            if f.is_file() and f.name.startswith(pid):
                return True
    return False


def charger_page_cible(repo: Path):
    fichier = repo / "config" / "page_cible.json"
    if not fichier.is_file():
        return None
    import json
    try:
        data = json.loads(fichier.read_text(encoding="utf-8"))
        return (data.get("facebook") or {}).get("id")
    except Exception:  # noqa: BLE001
        return None


def charger_comptes(repo: Path):
    """Retourne la liste des adresses client autorisées, ou None si le fichier manque/est vide."""
    fichier = repo / "config" / "comptes.json"
    if not fichier.is_file():
        return None
    import json
    try:
        data = json.loads(fichier.read_text(encoding="utf-8"))
        emails = ((data.get("client") or {}).get("emails_autorises")) or []
        return emails or None
    except Exception:  # noqa: BLE001
        return None


def charger_validation_formules(repo: Path) -> bool:
    """True si config/validation_formules.json existe et contient au moins une formule BAP."""
    fichier = repo / "config" / "validation_formules.json"
    if not fichier.is_file():
        return False
    import json
    try:
        data = json.loads(fichier.read_text(encoding="utf-8"))
        return bool((data.get("bap") or {}).get("formules_recevables"))
    except Exception:  # noqa: BLE001
        return False


def charger_contacts(repo: Path):
    """Retourne (numeros_valides, numero_france_present) — None si le fichier manque."""
    fichier = repo / "config" / "contacts.json"
    if not fichier.is_file():
        return None
    import json
    try:
        data = json.loads(fichier.read_text(encoding="utf-8"))
        numeros = data.get("whatsapp_posts") or []
        france_dans_posts = any("+33" in str(n) for n in numeros)
        return (numeros, france_dans_posts)
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--horizon", type=int, default=14, help="Jours à examiner (informatif)")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "contenu").is_dir():
        print(f"❌ {repo / 'contenu'} introuvable — ce n'est pas le dépôt attendu.", file=sys.stderr)
        return 2

    page_cible = charger_page_cible(repo)
    emails_autorises = charger_comptes(repo)
    formules_ok = charger_validation_formules(repo)
    contacts = charger_contacts(repo)

    par_id = {}
    critiques, avertissements = [], []

    for chemin in sorted((repo / "contenu").rglob("*.md")):
        meta, corps = lire_post(chemin)
        if not meta:
            continue

        post_id = str(meta.get("id", chemin.stem)).strip()
        composio_id = meta.get("composio_id")
        programme_le = meta.get("programme_le")

        # Un post non touché par une programmation n'a rien à vérifier ici.
        if est_vide(composio_id) and est_vide(programme_le):
            continue

        # Contrôle 4 — idempotence
        if not est_vide(composio_id):
            cid = str(composio_id).strip()
            par_id.setdefault(cid, []).append(post_id)

        # Contrôle 3 — double porte
        bap_ok = not est_vide(meta.get("bap_recu_le")) and not est_vide(meta.get("bap_email_ref"))
        visuel_ok = visuel_existe(repo, meta)
        if not (bap_ok and visuel_ok):
            manque = []
            if not bap_ok:
                manque.append("BAP (bap_recu_le/bap_email_ref)")
            if not visuel_ok:
                manque.append("visuel dans visuels/approuves/")
            critiques.append(
                f"{post_id} — programmé mais {' et '.join(manque)} manquant(s) — "
                f"fichier {chemin.relative_to(repo)}"
            )

        # Vocabulaire — publié sans publie_le
        statut = str(meta.get("statut", "")).lower()
        publie_le = meta.get("publie_le")
        if ("publi" in statut and "recu" not in statut) and est_vide(publie_le):
            avertissements.append(
                f"{post_id} — statut évoque une publication réelle mais publie_le est vide "
                f"(aucune confirmation de mise en ligne n'existe dans ce dispositif)"
            )

    for cid, ids in par_id.items():
        if len(ids) > 1:
            critiques.append(f"composio_id « {cid} » porté par {len(ids)} fichiers : {', '.join(ids)}")

    print(f"\n🔍 AUDIT DE CONFORMITÉ — horizon informatif {args.horizon} j\n")

    if page_cible:
        print(f"  Page cible enregistrée (config/page_cible.json) : id {page_cible}")
    else:
        print("  ⚠️ config/page_cible.json absent — la Page cible ne vit que dans la mémoire "
              "de conversation. Voir SKILL.md §6.")

    if emails_autorises:
        print(f"  Expéditeur(s) autorisé(s) (config/comptes.json) : {', '.join(emails_autorises)}")
    else:
        print("  ⚠️ config/comptes.json absent ou vide — aucune adresse client de référence : "
              "la routine 03h00 ne peut valider aucun BAT/BAP tant que ce fichier n'existe pas.")

    if formules_ok:
        print("  Formule BAP de référence (config/validation_formules.json) : présente")
    else:
        print("  ⚠️ config/validation_formules.json absent ou incomplet — la routine 03h00 ne "
              "peut reconnaître aucune validation client, même reçue de bonne foi. Vérifier "
              "aussi que les emails-types envoyés au client (community-manager-aora) demandent "
              "bien la formule de ce fichier, pas « BAT VALIDÉ »/« BAP VALIDÉ ».")

    if contacts:
        numeros, france_present = contacts
        if france_present:
            critiques.append(
                "config/contacts.json — le numéro France (+33) figure dans whatsapp_posts : "
                "il ne doit jamais être utilisé comme contact dans un post Excellence+."
            )
        else:
            print(f"  Numéros WhatsApp autorisés (config/contacts.json) : {', '.join(numeros)}")
    else:
        print("  ⚠️ config/contacts.json absent — aucun numéro WhatsApp de référence : risque "
              "qu'un post soit rédigé avec un numéro halluciné ou obsolète.")

    if critiques:
        print(f"\n  ⚠️ CRITIQUE ({len(critiques)})")
        for c in critiques:
            print(f"     {c}")
    if avertissements:
        print(f"\n  ⚠️ À corriger ({len(avertissements)})")
        for a in avertissements:
            print(f"     {a}")
    if not critiques and not avertissements:
        print("\n  ✅ Aucun écart détecté sur les posts programmés.")

    print()
    return 1 if critiques else 0


if __name__ == "__main__":
    sys.exit(main())
