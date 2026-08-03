#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier_conformite.py — Audit de conformité, exécuté par superviseur-publication-aora.

Ne modifie RIEN dans le dépôt. Relit l'état réel des fichiers — jamais un rapport Slack, jamais
une mémoire de conversation.

Contrôles :
  1. Page cible        config/page_cible.json présent et cohérent (informatif si absent)
  2. Créneaux          TOUT post avec date_publication+heure_publication doit correspondre à une
                        entrée de config/creneaux.json pour sa plateforme — pas seulement les posts
                        déjà programmés : une dérive se rattrape mieux avant le BAP qu'après.
  3. Double porte       bap_recu_le ET bap_email_ref renseignés ET visuel dans visuels/approuves/,
                        pour tout post composio_id/programme_le renseigné — simultané, obligatoire
  4. Idempotence        un composio_id ne doit apparaître que sur UN SEUL fichier
  5. Vocabulaire        statut évoquant une publication réelle sans publie_le renseigné
  6. Contacts WhatsApp  tout numéro présent dans le corps du post doit figurer dans
                        config/contacts.json → whatsapp.numeros ; sinon numéro inconnu ou
                        placeholder A_REMPLIR encore présent
  7. Style du titre     si la première ligne du corps contient des caractères Unicode stylés,
                        vérifie qu'ils appartiennent à la famille déclarée dans
                        config/mise_en_forme.json (facebook.styles.accroche.style_yaytext) —
                        best-effort, silencieux si le post n'est pas encore stylé

Ce script ne corrige rien et ne publie rien. Il dit ce qui ne tient pas, pour que
superviseur-publication-aora le rapporte — la décision reste humaine.

Usage :
    python3 scripts/verifier_conformite.py --repo <chemin_du_depot> --horizon 14
"""
import argparse
import json
import re
import sys
import datetime as dt
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ pyyaml requis (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)

JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# Plages Unicode (Mathematical Alphanumeric Symbols) pour la détection best-effort du style.
PLAGES_STYLE = {
    "gras_serif": [(0x1D400, 0x1D419), (0x1D41A, 0x1D433), (0x1D7CE, 0x1D7D7)],       # Bold
    "gras_sans_serif": [(0x1D5D4, 0x1D5ED), (0x1D5EE, 0x1D607), (0x1D7EC, 0x1D7F5)],  # Sans Bold
}


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


def charger_json(repo: Path, nom: str):
    fichier = repo / "config" / nom
    if not fichier.is_file():
        return None
    try:
        return json.loads(fichier.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def creneau_correspond(creneaux_cfg: dict, plateforme: str, date_pub, heure_pub: str) -> bool:
    liste = (creneaux_cfg.get("creneaux") or {}).get(plateforme, [])
    if not liste or date_pub is None:
        return True  # pas de référence pour cette plateforme : on ne peut rien affirmer
    jour = JOURS_FR[date_pub.weekday()]
    heure_norm = str(heure_pub).strip().zfill(5)
    for c in liste:
        if c.get("jour") == jour and str(c.get("heure", "")).strip() == heure_norm:
            return True
    return False


def numeros_dans_texte(texte: str):
    return set(re.findall(r"\+\d{1,3}[\s.]?\d{2,3}[\s.]?\d{3}[\s.]?\d{3}", texte))


def normaliser_numero(n: str) -> str:
    return re.sub(r"[\s.]", "", n)


def detecter_famille_style(texte: str):
    for style, plages in PLAGES_STYLE.items():
        for cp_min, cp_max in plages:
            for ch in texte:
                if cp_min <= ord(ch) <= cp_max:
                    return style
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

    page_cible_cfg = charger_json(repo, "page_cible.json")
    creneaux_cfg = charger_json(repo, "creneaux.json")
    contacts_cfg = charger_json(repo, "contacts.json")
    mise_en_forme_cfg = charger_json(repo, "mise_en_forme.json")

    numeros_approuves = set()
    if contacts_cfg:
        numeros_approuves = {normaliser_numero(n) for n in (contacts_cfg.get("whatsapp") or {}).get("numeros", [])}

    style_attendu = None
    if mise_en_forme_cfg:
        acc = ((mise_en_forme_cfg.get("facebook") or {}).get("styles") or {}).get("accroche")
        if isinstance(acc, dict):
            style_attendu = acc.get("style_yaytext")

    par_id = {}
    critiques, avertissements, infos = [], [], []

    for chemin in sorted((repo / "contenu").rglob("*.md")):
        meta, corps = lire_post(chemin)
        if not meta:
            continue

        post_id = str(meta.get("id", chemin.stem)).strip()
        composio_id = meta.get("composio_id")
        programme_le = meta.get("programme_le")
        rel = chemin.relative_to(repo)

        # Contrôle 2 — créneaux, sur TOUT post daté (pas seulement les programmés)
        if creneaux_cfg and not est_vide(meta.get("date_publication")) and not est_vide(meta.get("heure_publication")):
            try:
                date_pub = meta["date_publication"]
                if isinstance(date_pub, str):
                    date_pub = dt.date.fromisoformat(date_pub)
                plateforme = str(meta.get("plateforme", "")).strip()
                if not creneau_correspond(creneaux_cfg, plateforme, date_pub, meta["heure_publication"]):
                    jour = JOURS_FR[date_pub.weekday()]
                    critiques.append(
                        f"{post_id} — programmé {jour} {meta['heure_publication']} : aucun créneau "
                        f"correspondant dans config/creneaux.json pour « {plateforme} » — "
                        f"fichier {rel}"
                    )
            except (ValueError, KeyError, TypeError):
                avertissements.append(f"{post_id} — date_publication/heure_publication illisible ({rel})")

        # Contrôle 6 — contacts WhatsApp
        if "A_REMPLIR" in corps:
            avertissements.append(f"{post_id} — placeholder A_REMPLIR encore présent dans le corps ({rel})")
        elif contacts_cfg:
            for num in numeros_dans_texte(corps):
                if normaliser_numero(num) not in numeros_approuves:
                    critiques.append(
                        f"{post_id} — numéro « {num} » absent de config/contacts.json → "
                        f"whatsapp.numeros — fichier {rel}"
                    )

        # Contrôle 7 — style du titre (best-effort, silencieux si rien à comparer)
        if style_attendu and corps.strip():
            premiere_ligne = corps.strip().splitlines()[0]
            famille_detectee = detecter_famille_style(premiere_ligne)
            if famille_detectee and famille_detectee != style_attendu:
                avertissements.append(
                    f"{post_id} — titre stylé en « {famille_detectee} », config/mise_en_forme.json "
                    f"attend « {style_attendu} » — fichier {rel}"
                )

        # Un post non touché par une programmation s'arrête ici pour les contrôles 3/4/5
        if est_vide(composio_id) and est_vide(programme_le):
            continue

        if not est_vide(composio_id):
            cid = str(composio_id).strip()
            par_id.setdefault(cid, []).append(post_id)

        bap_ok = not est_vide(meta.get("bap_recu_le")) and not est_vide(meta.get("bap_email_ref"))
        visuel_ok = visuel_existe(repo, meta)
        if not (bap_ok and visuel_ok):
            manque = []
            if not bap_ok:
                manque.append("BAP (bap_recu_le/bap_email_ref)")
            if not visuel_ok:
                manque.append("visuel dans visuels/approuves/")
            critiques.append(
                f"{post_id} — programmé mais {' et '.join(manque)} manquant(s) — fichier {rel}"
            )

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

    if page_cible_cfg:
        pid = (page_cible_cfg.get("facebook") or {}).get("id")
        print(f"  Page cible (config/page_cible.json) : id {pid}")
    else:
        infos.append("config/page_cible.json absent — la Page cible ne vit que dans la mémoire de conversation.")

    if not contacts_cfg:
        infos.append("config/contacts.json absent — contrôle des numéros WhatsApp non exécuté.")

    if not creneaux_cfg:
        infos.append("config/creneaux.json introuvable — contrôle des créneaux non exécuté.")

    if infos:
        print("  ℹ️  " + "\n  ℹ️  ".join(infos))

    if critiques:
        print(f"\n  ⚠️ CRITIQUE ({len(critiques)})")
        for c in critiques:
            print(f"     {c}")
    if avertissements:
        print(f"\n  ⚠️ À corriger ({len(avertissements)})")
        for a in avertissements:
            print(f"     {a}")
    if not critiques and not avertissements:
        print("\n  ✅ Aucun écart détecté.")

    print()
    return 1 if critiques else 0


if __name__ == "__main__":
    sys.exit(main())
