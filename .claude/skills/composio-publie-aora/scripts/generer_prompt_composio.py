#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_prompt_composio.py — Produit la demande de publication à coller dans un
chat Claude où Composio est activé.

GitHub Actions n'a pas accès aux connecteurs MCP : la routine de 03h00 ne peut
pas appeler Composio elle-même. Elle produit donc une demande complète, qu'un
humain copie dans un chat normal. Effet secondaire utile : quelqu'un voit passer
chaque publication avant qu'elle parte.

Ne sortent ici que les publications ayant franchi les huit portes de
scripts/programmer_publications.py. Aucune ne s'y ajoute par un autre chemin.

Usage :
    python3 .claude/skills/composio-publie-aora/scripts/generer_prompt_composio.py
    python3 ... --horizon 3 --date 2026-08-09
    python3 ... --json          # pour rediriger vers Slack ou un autre canal
"""
import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RACINE / "scripts"))

try:
    from programmer_publications import (  # noqa: E402
        charger_liste_rouge, controler, horaire_utc, lire_post,
    )
except ImportError as err:
    print(f"❌ scripts/programmer_publications.py introuvable : {err}", file=sys.stderr)
    sys.exit(2)

from datetime import date, timedelta  # noqa: E402

FR_JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

ENTETE = """Tu vas programmer {n} publication{s} Excellence+ via Composio.

CONTEXTE — Dispositif AORA × Excellence+, contrat AORA-CCC-005.
Chacune de ces publications a franchi les huit portes de contrôle du dépôt :
BAP écrit reçu par email, visuel approuvé déposé par un humain, liste rouge,
canal ouvert, idempotence. Elles sont publiables en l'état.

MARCHE À SUIVRE
1. Cherche l'action Composio de programmation d'une publication sur Page
   Facebook (COMPOSIO_SEARCH_TOOLS). Ne devine pas le nom de l'action : les
   slugs changent, et une action inventée publie au mauvais endroit.
2. Vérifie que la connexion au compte Facebook d'Excellence+ est active.
3. Récapitule ce qui va partir et ATTENDS MA CONFIRMATION avant d'exécuter.
4. Exécute, puis rends-moi l'identifiant retourné par Composio pour chaque
   publication.

CE QUE TU NE FAIS PAS
· Ne modifie pas le texte. Il a été validé au BAP dans cette forme exacte ;
  une correction, même bonne, invalide la validation.
· N'invente aucune valeur manquante — identifiant de Page, numéro. Si quelque
  chose manque, arrête-toi et dis-le.
· Ne publie rien immédiatement : ce sont des publications PROGRAMMÉES, à la
  date et à l'heure indiquées.

Les heures sont données en UTC. Le fuseau local (WAT) est indiqué pour contrôle
seulement — le Cameroun est à UTC+1 toute l'année, sans heure d'été.
"""

PIED = """
APRÈS EXÉCUTION
Rends-moi, pour chaque publication, l'identifiant Composio. Je les écrirai dans
le dépôt (`composio_id` et `programme_le` du front-matter). Sans cette écriture,
la porte d'idempotence ne joue plus et la routine reprogrammerait les mêmes
publications au prochain passage.
"""


def bloc_publication(e: dict, i: int) -> str:
    lignes = [
        f"────────── PUBLICATION {i} — {e['id']}",
        f"Plateforme       : {e['plateforme']}",
        f"Programmer pour  : {e['utc']}  (soit {e['jour']} {e['date']} à {e['heure']} WAT)",
        f"Visuel à joindre : {e['visuel']}",
        "",
        "Texte exact à publier (ne rien changer) :",
        "«««",
        e["texte"].strip(),
        "»»»",
    ]
    if e.get("alt_text"):
        lignes += ["", f"Texte alternatif de l'image : {e['alt_text']}"]
    return "\n".join(lignes)


def collecter(repo: Path, jour_ref: date, horizon: int) -> list:
    cfg = repo / "config" / "creneaux.json"
    if not cfg.is_file():
        print(f"❌ {cfg} introuvable.", file=sys.stderr)
        sys.exit(2)
    config = json.loads(cfg.read_text(encoding="utf-8"))
    rouge = charger_liste_rouge(repo)
    limite = jour_ref + timedelta(days=horizon)

    sortie = []
    for chemin in sorted((repo / "contenu").rglob("*.md")):
        meta, corps = lire_post(chemin)
        if not meta:
            continue
        d = str(meta.get("date_publication", "")).strip()
        try:
            jour = date.fromisoformat(d)
        except ValueError:
            continue
        if not (jour_ref <= jour <= limite):
            continue
        etat, _ = controler(chemin, repo, config, rouge)
        if etat != "PRET":
            continue

        ref = meta.get("visuel_ref")
        visuel = str(ref).strip().strip('"').strip("'") if ref else ""
        if not (repo / visuel).is_file():
            pid = str(meta.get("id", "")).strip()
            approuves = repo / "visuels" / "approuves"
            for f in sorted(approuves.iterdir()) if approuves.is_dir() else []:
                if f.is_file() and f.name.startswith(pid):
                    visuel = str(f.relative_to(repo))
                    break

        sortie.append({
            "id": str(meta.get("id", chemin.stem)),
            "plateforme": str(meta.get("plateforme", "facebook")),
            "date": d,
            "jour": FR_JOURS[jour.weekday()],
            "heure": str(meta.get("heure_publication", "")).strip().strip('"'),
            "utc": horaire_utc(meta, config),
            "visuel": visuel,
            "alt_text": str(meta.get("alt_text", "")).strip().strip('"'),
            "texte": corps,
            "fichier": str(chemin.relative_to(repo)),
        })
    return sortie


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=RACINE)
    ap.add_argument("--horizon", type=int, default=7)
    ap.add_argument("--date", type=str, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    jour_ref = date.fromisoformat(args.date) if args.date else date.today()
    prets = collecter(repo, jour_ref, args.horizon)

    if args.json:
        print(json.dumps({"publications": prets}, ensure_ascii=False, indent=2))
        return 0

    if not prets:
        print("Aucune publication n'a franchi les huit portes sur cet horizon.")
        print("Ce n'est pas une panne : c'est qu'il n'y a rien à programmer.")
        print("Pour savoir ce qui bloque : python3 scripts/programmer_publications.py")
        return 0

    n = len(prets)
    print("=" * 72)
    print("  DEMANDE DE PUBLICATION — à coller dans un chat Claude avec Composio")
    print("=" * 72)
    print()
    print(ENTETE.format(n=n, s="s" if n > 1 else ""))
    for i, e in enumerate(prets, start=1):
        print(bloc_publication(e, i))
        print()
    print(PIED)
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
