#!/usr/bin/env python3
"""
État de la semaine cible — redaction-hebdo-excellence-plus

Calcule la semaine cible (lundi à samedi, respectivement 5 et 10 jours après la date
d'exécution), lit les créneaux actifs par canal depuis config/creneaux.json, croise avec
calendrier/calendrier_editorial.json et l'état réel du dépôt (fichiers contenu/<canal>/*.md),
et rend un inventaire déterministe : ce qui existe déjà, ce qu'il reste à rédiger, et le
prochain numéro d'ID disponible.

La partie créative (dériver un angle, rédiger, vérifier les sources, appliquer les portes
bloquantes) reste au skill — ce script ne fait que l'inventaire factuel, comme
pilote-quotidien-aora/scripts/etat_depot.py le fait pour la routine quotidienne.

Usage :
    python3 etat_semaine.py --repo <chemin_du_dépôt> [--date AAAA-MM-JJ]

--date sert à simuler une exécution à une date donnée (tests, rattrapage). Sans --date,
utilise la date du jour. La date fournie devrait être un mercredi ; sinon un avertissement est
émis sur stderr mais le calcul continue (déclenchement manuel un autre jour reste possible).

Sortie : JSON sur stdout.
Codes de sortie : 0 = ok, 2 = config/creneaux.json introuvable, 3 = PAUSE existe.
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

JOURS_FR = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi",
            4: "vendredi", 5: "samedi", 6: "dimanche"}
ID_PATTERN = re.compile(r"EXC-([A-Z]{2})-(\d{4})-(\d{3})")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True, help="Chemin vers la racine du dépôt cloné")
    p.add_argument("--date", default=None, help="AAAA-MM-JJ — date d'exécution simulée")
    return p.parse_args()


def lire_statut_frontmatter(fichier: Path):
    """Extrait la valeur du champ 'statut:' dans le front-matter YAML d'un fichier .md."""
    try:
        texte = fichier.read_text(encoding="utf-8")
    except OSError:
        return None
    if not texte.startswith("---"):
        return None
    parties = texte.split("---", 2)
    if len(parties) < 3:
        return None
    for ligne in parties[1].splitlines():
        if ligne.strip().startswith("statut:"):
            return ligne.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def main():
    args = parse_args()
    repo = Path(args.repo)

    if (repo / "PAUSE").exists():
        motif = (repo / "PAUSE").read_text(encoding="utf-8").strip()
        print(json.dumps({"pause": True, "motif": motif}, ensure_ascii=False))
        sys.exit(3)

    creneaux_path = repo / "config" / "creneaux.json"
    if not creneaux_path.exists():
        print(json.dumps({"erreur": "config/creneaux.json introuvable"}, ensure_ascii=False))
        sys.exit(2)

    creneaux_data = json.loads(creneaux_path.read_text(encoding="utf-8"))

    if args.date:
        trigger = date.fromisoformat(args.date)
    else:
        trigger = date.today()

    if trigger.weekday() != 2:
        print(
            f"Avertissement : {trigger.isoformat()} n'est pas un mercredi "
            f"(jour {trigger.weekday()} — {JOURS_FR[trigger.weekday()]}). "
            "Calcul poursuivi quand même (déclenchement manuel possible).",
            file=sys.stderr,
        )

    lundi_cible = trigger + timedelta(days=5)
    samedi_cible = trigger + timedelta(days=10)

    # --- calendrier éditorial existant (peut être absent en tout début de projet) ---
    calendrier_path = repo / "calendrier" / "calendrier_editorial.json"
    posts_existants = []
    if calendrier_path.exists():
        cal = json.loads(calendrier_path.read_text(encoding="utf-8"))
        posts_existants = cal.get("posts", [])

    # --- prochain ID disponible : max(calendrier existant, fichiers réellement sur disque) + 1 ---
    max_id = 0
    for p in posts_existants:
        m = ID_PATTERN.match(p.get("id", ""))
        if m:
            max_id = max(max_id, int(m.group(3)))
    contenu_dir = repo / "contenu"
    if contenu_dir.exists():
        for md in contenu_dir.rglob("*.md"):
            m = ID_PATTERN.search(md.stem)
            if m:
                max_id = max(max_id, int(m.group(3)))

    resultat = {
        "date_execution": trigger.isoformat(),
        "jour_execution": JOURS_FR[trigger.weekday()],
        "semaine_cible": {
            "lundi": lundi_cible.isoformat(),
            "samedi": samedi_cible.isoformat(),
        },
        "prochain_numero_id": max_id + 1,
        "canaux": {},
    }

    canaux_creneaux = creneaux_data.get("creneaux", {})
    activation = creneaux_data.get("canaux", {}).get("activation", {})

    for canal, liste_creneaux in canaux_creneaux.items():
        if canal.startswith("_"):
            continue
        date_activation = activation.get(canal)
        slots_canal = []

        for c in liste_creneaux:
            jour_nom = c.get("jour")
            offsets = [k for k, v in JOURS_FR.items() if v == jour_nom]
            if not offsets:
                continue
            date_slot = lundi_cible + timedelta(days=offsets[0])
            if not (lundi_cible <= date_slot <= samedi_cible):
                continue

            actif = True
            if date_activation:
                actif = date_slot.strftime("%Y-%m") >= date_activation

            entree = next(
                (p for p in posts_existants
                 if p.get("date") == date_slot.isoformat() and p.get("plateforme") == canal),
                None,
            )

            fichier_existant = None
            statut_fichier = None
            if entree and entree.get("fichier"):
                fp = repo / entree["fichier"]
                if fp.exists():
                    fichier_existant = entree["fichier"]
                    statut_fichier = lire_statut_frontmatter(fp)

            a_rediger = actif and (
                entree is None
                or fichier_existant is None
                or statut_fichier in (None, "a_rediger")
            )

            slots_canal.append({
                "date": date_slot.isoformat(),
                "jour": jour_nom,
                "heure": c.get("heure"),
                "pilier": c.get("pilier"),
                "canal_actif_ce_mois": actif,
                "entree_calendrier_existante": entree is not None,
                "id_existant": entree.get("id") if entree else None,
                "theme_pre_ecrit": entree.get("theme") if entree else None,
                "format_pre_ecrit": entree.get("format") if entree else None,
                "fichier_deja_redige": fichier_existant,
                "statut_actuel": statut_fichier,
                "a_rediger": a_rediger,
            })

        resultat["canaux"][canal] = slots_canal

    print(json.dumps(resultat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
