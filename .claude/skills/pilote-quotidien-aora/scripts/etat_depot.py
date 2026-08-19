#!/usr/bin/env python3
"""
État du dépôt — AORA x Excellence+
Inventaire des créneaux, calcul de l'avance et du quota de production du jour.

Usage :
    python etat_depot.py --repo /chemin/vers/EXCELLENCE-PLUS
    python etat_depot.py --repo . --json
    python etat_depot.py --repo . --horizon 21

Codes de sortie : 0 = OK · 2 = config introuvable · 3 = planning en PAUSE
"""

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

ETATS = {
    "PUBLIE": "✅",
    "PROGRAMME": "🕓",
    "PRET": "🟢",
    "TEXTE_SEUL": "🟡",
    "VIDE": "⬜",
}


def lire_frontmatter(chemin: Path) -> dict:
    brut = chemin.read_text(encoding="utf-8")
    if not brut.lstrip().startswith("---"):
        return {}
    parties = brut.split("---", 2)
    if len(parties) < 3:
        return {}
    meta = {}
    for ligne in parties[1].splitlines():
        if ":" in ligne and not ligne.strip().startswith("#"):
            cle, _, val = ligne.partition(":")
            meta[cle.strip()] = val.strip().strip('"').strip("'")
    return meta


def creneaux_attendus(config: dict, debut: date, horizon: int) -> list:
    """Génère les créneaux prévus par la config sur l'horizon."""
    base = config["creneaux"].get("facebook", [])
    saison = config.get("creneaux_saisonniers", {})
    attendus = []

    for delta in range(horizon + 1):
        jour = debut + timedelta(days=delta)
        nom_jour = JOURS[jour.weekday()]
        mois_cle = jour.strftime("%Y-%m")

        grille = list(base)
        grille += saison.get(mois_cle, {}).get("facebook_supplementaire", [])

        for c in grille:
            if c["jour"] == nom_jour:
                attendus.append(
                    {
                        "date": jour.isoformat(),
                        "jour": nom_jour,
                        "heure": c["heure"],
                        "pilier": c["pilier"],
                    }
                )
    return sorted(attendus, key=lambda x: (x["date"], x["heure"]))


def indexer_posts(repo: Path) -> dict:
    index = {}
    dossier = repo / "contenu" / "facebook"
    if not dossier.exists():
        return index
    for f in sorted(dossier.glob("*.md")):
        meta = lire_frontmatter(f)
        d = meta.get("date_publication")
        if d:
            index.setdefault(d, []).append({"fichier": f, "meta": meta})
    return index


def visuels_approuves(repo: Path, config: dict) -> set:
    dossier = repo / config.get("depot", {}).get("dossier_approuves", "visuels/approuves")
    if not dossier.exists():
        return set()
    ids = set()
    for f in dossier.iterdir():
        if f.is_file():
            m = re.match(r"(EXC-[A-Z]{2}-\d{4}-\d+)", f.name)
            if m:
                ids.add(m.group(1))
    return ids


def classer(creneau: dict, index: dict, approuves: set) -> dict:
    """Détermine l'état d'un créneau."""
    for c in index.get(creneau["date"], []):
        meta = c["meta"]
        if meta.get("heure_publication") != creneau["heure"]:
            continue
        pid = meta.get("facebook_post_id", "null")
        post_id = meta.get("id", "?")
        if pid and pid not in ("null", "None", ""):
            etat = "PUBLIE" if meta.get("publie_le", "null") not in ("null", "") else "PROGRAMME"
        elif post_id in approuves:
            etat = "PRET"
        else:
            etat = "TEXTE_SEUL"
        return {**creneau, "etat": etat, "id": post_id, "fichier": str(c["fichier"])}
    return {**creneau, "etat": "VIDE", "id": None, "fichier": None}


def calculer_avance(inventaire: list, aujourdhui: date) -> dict:
    """Avance = jours jusqu'au dernier créneau CONSÉCUTIVEMENT couvert.

    Un trou casse la chaîne. Un créneau couvert situé après un trou ne rassure
    personne : le trou, lui, sera visible sur la page.
    """
    couvert = {"PUBLIE", "PROGRAMME", "PRET"}
    dernier = None
    for c in inventaire:
        if date.fromisoformat(c["date"]) < aujourdhui:
            continue
        if c["etat"] in couvert:
            dernier = c
        else:
            break
    if dernier is None:
        return {"jours": 0, "dernier_creneau": None}
    return {
        "jours": (date.fromisoformat(dernier["date"]) - aujourdhui).days,
        "dernier_creneau": f"{dernier['jour']} {dernier['date']} {dernier['heure']}",
    }


def calculer_quota(avance_jours: int, objectif: int = 14) -> dict:
    """Le quota s'adapte à l'écart. Plafond à 3 : au-delà, la qualité chute
    et le stock devient du remplissage."""
    if avance_jours < 7:
        return {"quota": 3, "phase": "RATTRAPAGE"}
    if avance_jours < 12:
        return {"quota": 2, "phase": "CONSOLIDATION"}
    if avance_jours < objectif:
        return {"quota": 1, "phase": "CONSOLIDATION"}
    return {"quota": 1, "phase": "MAINTIEN"}


def main() -> int:
    ap = argparse.ArgumentParser(description="État du dépôt Excellence+")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--horizon", type=int, default=None)
    ap.add_argument("--date", type=str, default=None, help="Date de référence (test)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg_path = args.repo / "config" / "creneaux.json"
    if not cfg_path.exists():
        print(f"❌ Config introuvable : {cfg_path}", file=sys.stderr)
        return 2
    config = json.loads(cfg_path.read_text(encoding="utf-8"))

    aujourdhui = date.fromisoformat(args.date) if args.date else date.today()
    horizon = args.horizon or config.get("horizon_jours", 14)

    pause = args.repo / "PAUSE"
    if pause.exists():
        print(f"⏸️  PLANNING EN PAUSE\n{pause.read_text(encoding='utf-8').strip()}")
        return 3

    attendus = creneaux_attendus(config, aujourdhui, horizon)
    index = indexer_posts(args.repo)
    approuves = visuels_approuves(args.repo, config)
    inventaire = [classer(c, index, approuves) for c in attendus]

    avance = calculer_avance(inventaire, aujourdhui)
    quota = calculer_quota(avance["jours"], config.get("horizon_jours", 14))
    compte = {e: sum(1 for c in inventaire if c["etat"] == e) for e in ETATS}

    rapport = {
        "date": aujourdhui.isoformat(),
        "horizon_jours": horizon,
        "creneaux_total": len(inventaire),
        "compte": compte,
        "avance": avance,
        "quota_du_jour": quota["quota"],
        "phase": quota["phase"],
        "visuels_a_monter": compte["TEXTE_SEUL"],
        "inventaire": inventaire,
    }

    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
        return 0

    print(f"\n📊 ÉTAT DU DÉPÔT — {aujourdhui.strftime('%d/%m/%Y')} · horizon {horizon} j\n")
    for c in inventaire:
        d = date.fromisoformat(c["date"])
        print(
            f"  {ETATS[c['etat']]} {c['jour']:<9} {d.strftime('%d/%m')} {c['heure']} "
            f"P{c['pilier']}  {c['id'] or '—'}"
        )
    print(
        f"\n  ✅ {compte['PUBLIE']} publiés · 🕓 {compte['PROGRAMME']} programmés · "
        f"🟢 {compte['PRET']} prêts · 🟡 {compte['TEXTE_SEUL']} texte seul · "
        f"⬜ {compte['VIDE']} vides"
    )
    print(f"\n  AVANCE   {avance['jours']} j — {avance['dernier_creneau'] or 'aucun créneau couvert'}")
    print(f"  PHASE    {quota['phase']} → quota du jour : {quota['quota']} post(s)")
    print(f"  GOULOT   {compte['TEXTE_SEUL']} visuel(s) à monter puis à déposer dans approuves/\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
