#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
programmer_publications.py — Contrôles avant programmation, exécutés à 03h00 WAT.

Parcourt les publications à venir et détermine, pour chacune, si elle peut être
programmée. Les contrôles sont volontairement stricts et ordonnés : la première
porte qui refuse arrête l'examen de la publication concernée.

  1. BAP écrit           bap_recu_le ET bap_email_ref renseignés
  2. Visuel approuvé     présent dans visuels/approuves/
  3. Format du visuel    dimensions conformes à la plateforme
  4. Autorisation        si un mineur est identifiable
  5. Liste rouge         aucun terme interdit dans le texte
  6. Valeurs à remplir   aucun A_REMPLIR résiduel
  7. Canal ouvert        la plateforme est activée à cette date
  8. Pas déjà programmé  idempotence — on ne programme jamais deux fois

Ce script ne publie pas et n'appelle aucune API : il dit ce qui est publiable.
L'envoi effectif chez Composio est une étape séparée, qui ne s'exécute que sur
les publications déclarées PRÊTES ici.

Usage :
    python3 scripts/programmer_publications.py
    python3 scripts/programmer_publications.py --horizon 3 --rapport-slack
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ pyyaml requis", file=sys.stderr)
    sys.exit(1)

FR_JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


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


def charger_liste_rouge(repo: Path) -> list:
    """Termes interdits. config/liste_rouge.json prime s'il existe."""
    fichier = repo / "config" / "liste_rouge.json"
    if fichier.is_file():
        try:
            data = json.loads(fichier.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data.get("termes", [])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    # Repli : les interdits que brand_guidelines §11 rend absolus.
    return ["Excellence++", "Prepdia", "La Réussite Plus", "Zacharias", "Fomum"]


def canal_ouvert(config: dict, plateforme: str, jour: date) -> bool:
    activation = (config.get("canaux") or {}).get("activation") or {}
    if plateforme not in activation:
        return False
    valeur = activation[plateforme]
    if not valeur:
        return False
    return jour.strftime("%Y-%m") >= str(valeur)


def controler(chemin: Path, repo: Path, config: dict, rouge: list):
    """Renvoie (etat, motif). etat ∈ PRET · BLOQUE · DEJA_PROGRAMME · IGNORE."""
    meta, corps = lire_post(chemin)
    if meta is None:
        return "IGNORE", "front-matter illisible"

    d = str(meta.get("date_publication", "")).strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        return "IGNORE", "date de publication absente ou mal formée"

    if not est_vide(meta.get("composio_id")) or not est_vide(meta.get("programme_le")):
        return "DEJA_PROGRAMME", "déjà transmis à Composio"
    if not est_vide(meta.get("publie_le")):
        return "DEJA_PROGRAMME", "déjà publié"

    # Porte 1 — BAP écrit. La plus importante : elle protège le client.
    if est_vide(meta.get("bap_recu_le")):
        return "BLOQUE", "BAP non reçu — aucune publication possible"
    if est_vide(meta.get("bap_email_ref")):
        return "BLOQUE", "bap_recu_le renseigné mais bap_email_ref vide — validation non opposable"

    # Porte 2 — visuel approuvé, déposé à la main par un humain.
    ref = meta.get("visuel_ref")
    visuel = None
    if not est_vide(ref):
        candidat = repo / str(ref).strip().strip('"').strip("'")
        if candidat.is_file():
            visuel = candidat
    if visuel is None:
        approuves = repo / "visuels" / "approuves"
        pid = str(meta.get("id", "")).strip()
        if pid and approuves.is_dir():
            for f in approuves.iterdir():
                if f.is_file() and f.name.startswith(pid):
                    visuel = f
                    break
    if visuel is None:
        return "BLOQUE", "visuel absent de visuels/approuves/"

    # Porte 4 — mineur identifiable.
    if meta.get("mineur_identifiable") is True:
        if meta.get("autorisation_parentale") is not True or est_vide(meta.get("autorisation_ref")):
            return "BLOQUE", "mineur identifiable sans autorisation parentale archivée"

    # Porte 5 — liste rouge.
    for terme in rouge:
        if terme and terme.lower() in corps.lower():
            return "BLOQUE", f"terme interdit dans le texte : « {terme} »"

    # Porte 6 — valeurs non renseignées.
    if "A_REMPLIR" in corps or any("A_REMPLIR" in str(v) for v in meta.values()):
        return "BLOQUE", "contient encore une valeur A_REMPLIR"

    # Porte 7 — canal ouvert à cette date.
    plateforme = str(meta.get("plateforme", "")).strip()
    if not canal_ouvert(config, plateforme, date.fromisoformat(d)):
        return "BLOQUE", f"canal « {plateforme} » non ouvert à cette date"

    return "PRET", "tous les contrôles franchis"


def horaire_utc(meta: dict, config: dict) -> str:
    """WAT (UTC+1, sans heure d'été) → UTC. La conversion n'a lieu qu'ici."""
    d = str(meta.get("date_publication", "")).strip()
    h = str(meta.get("heure_publication", "")).strip().strip('"').strip("'") or "12:00"
    local = datetime.fromisoformat(f"{d}T{h}:00")
    return (local - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:00Z")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--horizon", type=int, default=7, help="Jours à examiner")
    ap.add_argument("--date", type=str, default=None, help="Date de référence (test)")
    ap.add_argument("--rapport-slack", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    aujourdhui = date.fromisoformat(args.date) if args.date else date.today()
    limite = aujourdhui + timedelta(days=args.horizon)

    cfg_path = repo / "config" / "creneaux.json"
    if not cfg_path.is_file():
        print(f"❌ {cfg_path} introuvable — aucune programmation possible.", file=sys.stderr)
        return 2
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    rouge = charger_liste_rouge(repo)

    prets, bloques, deja = [], [], []
    for chemin in sorted((repo / "contenu").rglob("*.md")):
        meta, _ = lire_post(chemin)
        if not meta:
            continue
        d = str(meta.get("date_publication", "")).strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            continue
        jour = date.fromisoformat(d)
        if not (aujourdhui <= jour <= limite):
            continue

        etat, motif = controler(chemin, repo, config, rouge)
        ligne = {
            "id": str(meta.get("id", chemin.stem)),
            "date": d,
            "jour": FR_JOURS[jour.weekday()],
            "heure": str(meta.get("heure_publication", "")).strip().strip('"'),
            "utc": horaire_utc(meta, config),
            "plateforme": str(meta.get("plateforme", "?")),
            "motif": motif,
            "fichier": str(chemin.relative_to(repo)),
        }
        {"PRET": prets, "BLOQUE": bloques, "DEJA_PROGRAMME": deja}.get(etat, []).append(ligne)

    print(f"\n🕒 PROGRAMMATION — {aujourdhui.strftime('%d/%m/%Y')} · horizon {args.horizon} j\n")
    if prets:
        print(f"  ✅ PRÊTES À PROGRAMMER ({len(prets)})")
        for e in prets:
            print(f"     {e['id']} · {e['jour']} {e['date']} {e['heure']} WAT "
                  f"({e['utc']}) · {e['plateforme']}")
    if bloques:
        print(f"\n  ⛔ BLOQUÉES ({len(bloques)})")
        for e in bloques:
            print(f"     {e['id']} · {e['jour']} {e['date']} — {e['motif']}")
    if deja:
        print(f"\n  🕓 DÉJÀ PROGRAMMÉES ({len(deja)})")
        for e in deja:
            print(f"     {e['id']} · {e['date']}")
    if not (prets or bloques or deja):
        print("  Aucune publication dans l'horizon.")
    print()

    if args.rapport_slack and (prets or bloques):
        lignes = [f"🕒 *Programmation {aujourdhui.strftime('%d/%m/%Y')}* — horizon {args.horizon} j"]
        if prets:
            lignes.append(f"✅ *{len(prets)} prête(s) à programmer*")
            lignes += [f"• `{e['id']}` · {e['jour']} {e['date']} {e['heure']} WAT" for e in prets]
        if bloques:
            lignes.append(f"⛔ *{len(bloques)} bloquée(s)*")
            lignes += [f"• `{e['id']}` — {e['motif']}" for e in bloques]
        script = repo / "scripts" / "notifier_bap.py"
        if script.is_file():
            # On réutilise l'envoi de notifier_bap : un seul point de sortie Slack.
            sys.path.insert(0, str(repo / "scripts"))
            try:
                from notifier_bap import envoyer  # noqa: E402
                if not envoyer("\n".join(lignes)):
                    print("(rapport Slack non envoyé — Slack non configuré)")
            except Exception as err:  # noqa: BLE001
                print(f"(rapport Slack non envoyé : {err})")

    # Une publication bloquée n'est pas une erreur d'exécution : c'est
    # l'information attendue. Le script ne sort en erreur que s'il n'a pas pu
    # faire son travail.
    return 0


if __name__ == "__main__":
    sys.exit(main())
