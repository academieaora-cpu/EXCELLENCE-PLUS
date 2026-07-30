#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notifier_bap.py — Alerte Slack au moment où le client valide.

Détecte la transition `bap_recu_le: null` → `bap_recu_le: <date>` dans les
fichiers de contenu, entre deux commits. C'est le seul signal fiable de
validation client : la règle absolue (brand_guidelines §11) veut qu'un humain
ayant l'email sous les yeux renseigne ce champ lui-même. Le commit qui porte
ce geste est donc l'événement à écouter — pas une boîte mail, pas une API.

Contrôle en même temps la complétude exigée avant publication :
  - `bap_recu_le` ET `bap_email_ref` doivent être renseignés tous les deux
  - le visuel doit être présent dans visuels/approuves/

Un BAP à moitié renseigné est signalé en avertissement, pas en feu vert : sans
référence email, la validation n'est pas opposable.

Usage :
    python3 scripts/notifier_bap.py --avant <SHA> --apres <SHA>
    python3 scripts/notifier_bap.py --avant HEAD~1 --apres HEAD --dry-run
    python3 scripts/notifier_bap.py --test          # vérifie le câblage Slack

Variables d'environnement — l'une OU l'autre :
    SLACK_WEBHOOK_URL                webhook entrant Slack
    SLACK_BOT_TOKEN + SLACK_CHANNEL  jeton de bot (chat.postMessage)

Aucune des deux → mode dry-run forcé : le message s'affiche, rien n'est envoyé.
Un webhook absent ne fait pas échouer la CI ; il rendrait rouge un dépôt dont le
contenu est pourtant correct.

Codes de sortie : 0 = OK (avec ou sans notification) · 1 = erreur d'exécution
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ pyyaml requis : pip install pyyaml", file=sys.stderr)
    sys.exit(1)

FR_JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
FR_MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

SHA_VIDE = "0000000000000000000000000000000000000000"


def est_vide(valeur) -> bool:
    """Un champ non renseigné peut prendre plusieurs formes selon qui l'a écrit."""
    if valeur is None:
        return True
    texte = str(valeur).strip().strip('"').strip("'")
    return texte in ("", "null", "None", "~", "A_REMPLIR")


def lire_frontmatter(brut: str) -> dict:
    """Extrait le front-matter YAML. Retourne {} si le fichier n'en a pas."""
    if not brut.lstrip().startswith("---"):
        return {}
    parties = brut.split("---", 2)
    if len(parties) < 3:
        return {}
    try:
        meta = yaml.safe_load(parties[1])
        return meta if isinstance(meta, dict) else {}
    except yaml.YAMLError:
        return {}


def git(*args, cwd=None):
    """Exécute git et retourne stdout, ou None si la commande échoue."""
    res = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
    return res.stdout if res.returncode == 0 else None


def fichiers_modifies(avant: str, apres: str, repo: Path) -> list:
    """Fichiers .md de contenu/ touchés entre deux commits."""
    if avant == SHA_VIDE:
        sortie = git("ls-tree", "-r", "--name-only", apres, cwd=repo)
    else:
        sortie = git("diff", "--name-only", avant, apres, cwd=repo)
    if sortie is None:
        return []
    return [
        ligne for ligne in sortie.splitlines()
        if ligne.startswith("contenu/") and ligne.endswith(".md")
    ]


def version_a(sha: str, chemin: str, repo: Path) -> dict:
    """Front-matter du fichier tel qu'il était à ce commit. {} s'il n'existait pas."""
    if sha == SHA_VIDE:
        return {}
    brut = git("show", f"{sha}:{chemin}", cwd=repo)
    return lire_frontmatter(brut) if brut else {}


def visuel_present(meta: dict, repo: Path) -> bool:
    """Le visuel approuvé existe-t-il ? Deux façons de le désigner."""
    ref = meta.get("visuel_ref")
    if not est_vide(ref):
        chemin = str(ref).strip().strip('"').strip("'")
        if (repo / chemin).is_file():
            return True
    post_id = str(meta.get("id", "")).strip()
    if not post_id or "[" in post_id:
        return False
    approuves = repo / "visuels" / "approuves"
    if not approuves.is_dir():
        return False
    return any(f.name.startswith(post_id) for f in approuves.iterdir() if f.is_file())


def date_lisible(meta: dict) -> str:
    """« lundi 10 août 2026 · 12h30 WAT » — à partir des champs du post."""
    d = str(meta.get("date_publication", "")).strip()
    h = str(meta.get("heure_publication", "")).strip().strip('"').strip("'")
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", d)
    if not m:
        return d or "date non renseignée"
    from datetime import date as _date
    annee, mois, jour = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        jsem = FR_JOURS[_date(annee, mois, jour).weekday()]
    except ValueError:
        return d
    libelle = f"{jsem} {jour} {FR_MOIS[mois]} {annee}"
    return f"{libelle} · {h.replace(':', 'h')} WAT" if h else libelle


def analyser(chemin: str, avant: str, apres: str, repo: Path):
    """Retourne un événement si le BAP vient d'arriver sur ce fichier, sinon None."""
    meta_avant = version_a(avant, chemin, repo)
    fichier = repo / chemin
    if not fichier.is_file():
        return None
    meta_apres = lire_frontmatter(fichier.read_text(encoding="utf-8"))
    if not meta_apres:
        return None

    # L'événement, c'est la transition — pas l'état. Un BAP déjà renseigné
    # avant ce commit a déjà été annoncé.
    if not est_vide(meta_avant.get("bap_recu_le")):
        return None
    if est_vide(meta_apres.get("bap_recu_le")):
        return None

    ref_email = meta_apres.get("bap_email_ref")
    return {
        "id": str(meta_apres.get("id", "?")).strip(),
        "fichier": chemin,
        "titre": str(meta_apres.get("titre_interne", "")).strip().strip('"'),
        "plateforme": str(meta_apres.get("plateforme", "?")).strip(),
        "quand": date_lisible(meta_apres),
        "bap_recu_le": str(meta_apres.get("bap_recu_le")).strip().strip('"'),
        "ref_email": "" if est_vide(ref_email) else str(ref_email).strip().strip('"'),
        "ref_email_manquante": est_vide(ref_email),
        "visuel_ok": visuel_present(meta_apres, repo),
    }


def composer(evenements: list) -> str:
    """Message Slack. Le point d'attention passe avant la bonne nouvelle."""
    incomplets = [e for e in evenements if e["ref_email_manquante"]]
    complets = [e for e in evenements if not e["ref_email_manquante"]]
    lignes = []

    if incomplets:
        lignes.append("⚠️ *BAP INCOMPLET — publication impossible en l'état*")
        for e in incomplets:
            lignes.append(f"• `{e['id']}` — {e['quand']}")
            lignes.append(f"    `bap_recu_le` renseigné, `bap_email_ref` vide.")
        lignes.append(
            "_Les deux champs sont requis (brand_guidelines §11). "
            "Sans référence email, la validation n'est pas opposable._"
        )
        if complets:
            lignes.append("")

    if complets:
        pluriel = "s" if len(complets) > 1 else ""
        lignes.append(f"✅ *BAP reçu — {len(complets)} publication{pluriel} validée{pluriel} par le client*")
        for e in complets:
            lignes.append(f"• `{e['id']}` · {e['plateforme']} — {e['quand']}")
            if e["titre"]:
                lignes.append(f"    _{e['titre']}_")
            lignes.append(f"    validé le {e['bap_recu_le']} · réf. {e['ref_email']}")
            if e["visuel_ok"]:
                lignes.append("    🟢 visuel approuvé présent — *prêt à programmer*")
            else:
                lignes.append("    🟡 visuel absent de `visuels/approuves/` — à déposer avant programmation")

    return "\n".join(lignes)


def envoyer(message: str) -> bool:
    """Poste sur Slack par webhook, sinon par jeton de bot. False si aucun des deux."""
    import urllib.request
    import urllib.error

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    jeton = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    canal = os.environ.get("SLACK_CHANNEL", "").strip()

    if webhook:
        url = webhook
        entetes = {"Content-Type": "application/json"}
        corps = {"text": message}
    elif jeton and canal:
        url = "https://slack.com/api/chat.postMessage"
        entetes = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {jeton}",
        }
        corps = {"channel": canal, "text": message}
    else:
        print("❌ Ni SLACK_WEBHOOK_URL ni SLACK_BOT_TOKEN+SLACK_CHANNEL.", file=sys.stderr)
        return False

    requete = urllib.request.Request(
        url, data=json.dumps(corps).encode("utf-8"), headers=entetes
    )
    try:
        with urllib.request.urlopen(requete, timeout=15) as rep:
            charge = rep.read().decode("utf-8", errors="replace")
            if not (200 <= rep.status < 300):
                print(f"❌ Slack a répondu {rep.status} : {charge}", file=sys.stderr)
                return False
            # chat.postMessage répond 200 même en cas d'erreur métier.
            if url.endswith("chat.postMessage"):
                rep_json = json.loads(charge)
                if not rep_json.get("ok"):
                    print(f"❌ Slack : {rep_json.get('error')}", file=sys.stderr)
                    return False
            return True
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        print(f"❌ Envoi Slack impossible : {err}", file=sys.stderr)
        return False


def message_test() -> str:
    return (
        "🔧 *Test de câblage — alerte BAP*\n"
        "Si ce message s'affiche dans le canal, la chaîne "
        "`dépôt → GitHub Actions → Slack` fonctionne.\n"
        "_Les vraies alertes partiront à chaque `bap_recu_le` renseigné sur `main`._"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Alerte Slack à la réception d'un BAP")
    ap.add_argument("--avant", help="SHA du commit précédent")
    ap.add_argument("--apres", default="HEAD", help="SHA du commit courant")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--dry-run", action="store_true", help="Affiche sans envoyer")
    ap.add_argument("--test", action="store_true", help="Envoie un message de test")
    args = ap.parse_args()

    if args.test:
        if args.dry_run:
            print(f"--- message de test (non envoyé) ---\n{message_test()}")
            return 0
        print("Envoi du message de test…")
        if envoyer(message_test()):
            print("✅ Message envoyé — vérifie le canal Slack.")
            return 0
        return 1

    if not args.avant:
        ap.error("--avant est requis (sauf avec --test)")

    repo = args.repo.resolve()
    configure = bool(
        os.environ.get("SLACK_WEBHOOK_URL", "").strip()
        or (os.environ.get("SLACK_BOT_TOKEN", "").strip()
            and os.environ.get("SLACK_CHANNEL", "").strip())
    )
    dry = args.dry_run or not configure

    chemins = fichiers_modifies(args.avant, args.apres, repo)
    if not chemins:
        print("Aucun fichier de contenu modifié — rien à signaler.")
        return 0

    evenements = [e for e in (analyser(c, args.avant, args.apres, repo) for c in chemins) if e]
    if not evenements:
        print(f"{len(chemins)} fichier(s) de contenu modifié(s), aucun BAP nouvellement reçu.")
        return 0

    message = composer(evenements)

    if dry:
        motif = "--dry-run" if args.dry_run else "Slack non configuré"
        print(f"--- message Slack ({motif}, non envoyé) ---\n{message}")
        return 0

    print(f"{len(evenements)} BAP détecté(s) — envoi Slack…")
    return 0 if envoyer(message) else 1


if __name__ == "__main__":
    sys.exit(main())
