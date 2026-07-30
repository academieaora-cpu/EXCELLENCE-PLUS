#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
traiter_bap.py — Consomme les fichiers déposés dans validation/BAP/ et, pour
chacun, enregistre la validation client sur la publication correspondante.

Point d'entrée UNIQUE des validations, quel que soit leur canal d'origine :
  · un humain (Laurence) dépose le fichier directement dans validation/BAP/
  · une routine qui lit Gmail écrit le même type de fichier après avoir
    repéré un email de validation

Les deux chemins convergent ici pour ne pas dupliquer la logique de
correspondance et de contrôle à deux endroits — une règle écrite deux fois
finit par diverger.

CONVENTION DE NOM (celle transmise, ex. « rentréscolaire_10_08_2026_06H00ᐧ) :

    <libellé-libre>_<JJ>_<MM>_<AAAA>_<HHhMM>[.extension]

    · <libellé-libre> : texte affiché à l'équipe, jamais interprété par le
      script. Peut contenir des underscores sans casser le nom.
    · JJ_MM_AAAA : date de PUBLICATION que ce BAP valide — c'est la clé de
      correspondance. Avec la cadence actuelle (3 créneaux/semaine, un par
      jour), une date correspond à au plus UNE publication : le rapprochement
      est donc fiable sans avoir à interpréter le libellé.
    · HHhMM : heure informative (dépôt ou réception) — n'entre PAS dans la
      correspondance, seulement journalisée.

Ce que fait ce script pour un fichier dont la date correspond à EXACTEMENT une
publication en attente (BAT_soumis, bap_recu_le vide) :
  1. re-contrôle liste rouge + A_REMPLIR (défense en profondeur : le texte a
     déjà été contrôlé au BAT, on ne fait pas confiance à un état qui a pu
     changer entre-temps)
  2. écrit bap_recu_le (date de traitement) et bap_email_ref (référence vers
     le fichier BAP archivé — une preuve retenue dans le dépôt, pas une
     mention libre)
  3. cherche un visuel dans visuels/en_production/ dont le nom commence par
     l'identifiant de la publication, et le déplace vers visuels/approuves/
  4. archive le fichier BAP dans validation/BAP/traites/ (idempotence : un
     fichier déjà archivé n'est plus repris)

Ce que fait ce script si la date ne correspond à AUCUNE ou à PLUSIEURS
publications : rien. Le fichier reste dans validation/BAP/, non traité, et
l'anomalie est journalisée pour qu'un humain tranche. Deviner ici serait
publier sur la foi d'une supposition.

⚠️ Le déplacement automatique vers approuves/ est une exception documentée à
la règle « aucune automatisation n'y touche » — voir brand_guidelines.md §11.
Elle ne s'applique QU'ICI, sur la base d'un BAP vérifié, jamais ailleurs.

Usage :
    python3 scripts/traiter_bap.py
    python3 scripts/traiter_bap.py --dry-run
    python3 scripts/traiter_bap.py --date 2026-08-09   # date de traitement (test)
"""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))

from programmer_publications import charger_liste_rouge, est_vide, lire_post  # noqa: E402

MOTIF_NOM = re.compile(
    r"^(?P<libelle>.+)_(?P<jour>\d{2})_(?P<mois>\d{2})_(?P<annee>\d{4})_"
    r"(?P<heure>\d{2})[Hh](?P<minute>\d{2})(?:\.[A-Za-z0-9]+)?$"
)


def parser_nom(nom_fichier: str):
    """Extrait la date de publication visée et l'heure informative.

    Retourne (date_visee, heure_texte, libelle) ou (None, None, None) si le
    nom ne suit pas la convention — dans ce cas le fichier est signalé, pas
    deviné.
    """
    m = MOTIF_NOM.match(nom_fichier)
    if not m:
        return None, None, None
    try:
        d = date(int(m["annee"]), int(m["mois"]), int(m["jour"]))
    except ValueError:
        return None, None, None
    h, mi = m["heure"], m["minute"]
    if not (0 <= int(h) <= 23 and 0 <= int(mi) <= 59):
        return None, None, None
    return d, f"{h}h{mi}", m["libelle"]


def posts_en_attente(repo: Path):
    """Publications BAT_soumis, sans BAP, indexées par date_publication."""
    index = {}
    for chemin in sorted((repo / "contenu").rglob("*.md")):
        meta, _ = lire_post(chemin)
        if not meta:
            continue
        if not est_vide(meta.get("bap_recu_le")):
            continue
        if not est_vide(meta.get("composio_id")) or not est_vide(meta.get("publie_le")):
            continue
        d = str(meta.get("date_publication", "")).strip()
        try:
            jour = date.fromisoformat(d)
        except ValueError:
            continue
        index.setdefault(jour, []).append(chemin)
    return index


def trouver_visuel(repo: Path, post_id: str):
    dossier = repo / "visuels" / "en_production"
    if not dossier.is_dir() or not post_id:
        return None
    for f in sorted(dossier.iterdir()):
        if f.is_file() and f.name.startswith(post_id):
            return f
    return None


def controler_texte(chemin: Path, repo: Path, rouge: list):
    """Re-contrôle liste rouge + A_REMPLIR avant d'enregistrer le BAP."""
    meta, corps = lire_post(chemin)
    for terme in rouge:
        if terme and terme.lower() in corps.lower():
            return f"terme interdit détecté à la revalidation : « {terme} »"
    if "A_REMPLIR" in corps or any("A_REMPLIR" in str(v) for v in meta.values()):
        return "valeur A_REMPLIR détectée à la revalidation"
    return None


def ecrire_bap(chemin: Path, aujourdhui: date, ref_bap: str):
    """Renseigne bap_recu_le / bap_email_ref / statut dans le front-matter,
    par remplacement textuel ciblé — pas de réécriture YAML complète, pour ne
    modifier que ces trois lignes et rien d'autre dans le fichier."""
    brut = chemin.read_text(encoding="utf-8")

    def poser(champ, valeur, texte):
        motif = re.compile(rf"^{champ}:.*$", re.MULTILINE)
        ligne = f'{champ}: "{valeur}"'
        if motif.search(texte):
            return motif.sub(ligne, texte, count=1)
        return texte  # champ absent : on ne l'invente pas dans un template inconnu

    brut = poser("bap_recu_le", aujourdhui.isoformat(), brut)
    brut = poser("bap_email_ref", ref_bap, brut)
    brut = poser("statut", "BAP_recu", brut).replace('statut: "BAP_recu"', "statut: BAP_recu")
    chemin.write_text(brut, encoding="utf-8")


def traiter(repo: Path, aujourdhui: date, dry_run: bool):
    dossier = repo / "validation" / "BAP"
    archives = dossier / "traites"
    rouge = charger_liste_rouge(repo)
    attente = posts_en_attente(repo)

    traites, signales = [], []

    for fichier in sorted(dossier.iterdir()):
        if not fichier.is_file() or fichier.name == ".gitkeep":
            continue

        jour_vise, heure, libelle = parser_nom(fichier.name)
        if jour_vise is None:
            signales.append((fichier.name, "nom de fichier hors convention "
                              "<libellé>_JJ_MM_AAAA_HHhMM — non traité"))
            continue

        candidats = attente.get(jour_vise, [])
        if len(candidats) == 0:
            signales.append((fichier.name, f"aucune publication en attente le {jour_vise.isoformat()}"))
            continue
        if len(candidats) > 1:
            noms = ", ".join(c.name for c in candidats)
            signales.append((fichier.name, f"{len(candidats)} publications le {jour_vise.isoformat()} "
                              f"({noms}) — correspondance ambiguë, à trancher à la main"))
            continue

        post = candidats[0]
        meta, _ = lire_post(post)
        post_id = str(meta.get("id", post.stem)).strip()

        erreur = controler_texte(post, repo, rouge)
        if erreur:
            signales.append((fichier.name, f"{post_id} — {erreur}, BAP non enregistré"))
            continue

        ref_archive = f"validation/BAP/traites/{fichier.name}"
        visuel = trouver_visuel(repo, post_id)

        detail = {
            "bap": fichier.name, "post": str(post.relative_to(repo)), "id": post_id,
            "date": jour_vise.isoformat(), "heure_bap": heure, "libelle": libelle,
            "visuel_deplace": str(visuel.name) if visuel else None,
        }

        if dry_run:
            traites.append(detail)
            continue

        ecrire_bap(post, aujourdhui, ref_archive)
        archives.mkdir(parents=True, exist_ok=True)
        shutil.move(str(fichier), str(archives / fichier.name))

        if visuel:
            (repo / "visuels" / "approuves").mkdir(parents=True, exist_ok=True)
            shutil.move(str(visuel), str(repo / "visuels" / "approuves" / visuel.name))

        traites.append(detail)

    return traites, signales


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=RACINE)
    ap.add_argument("--date", type=str, default=None, help="Date de traitement (test)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    aujourdhui = date.fromisoformat(args.date) if args.date else date.today()

    dossier = repo / "validation" / "BAP"
    if not dossier.is_dir():
        print(f"❌ {dossier} introuvable.", file=sys.stderr)
        return 2

    traites, signales = traiter(repo, aujourdhui, args.dry_run)

    entete = "ESSAI À BLANC — rien n'a été modifié" if args.dry_run else "TRAITEMENT DES BAP"
    print(f"\n📋 {entete} — {aujourdhui.strftime('%d/%m/%Y')}\n")

    if traites:
        verbe = "seraient enregistrés" if args.dry_run else "enregistrés"
        print(f"  ✅ {len(traites)} BAP {verbe}")
        for t in traites:
            ligne = f"     {t['bap']} → {t['id']} (publication du {t['date']})"
            if t["visuel_deplace"]:
                ligne += f" · visuel « {t['visuel_deplace']} » déplacé vers approuves/"
            else:
                ligne += " · ⚠️ aucun visuel trouvé dans en_production/ — à déposer manuellement"
            print(ligne)

    if signales:
        print(f"\n  ⚠️  {len(signales)} fichier(s) non traité(s), à examiner")
        for nom, motif in signales:
            print(f"     {nom} — {motif}")

    if not (traites or signales):
        print("  Aucun fichier à traiter dans validation/BAP/.")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
