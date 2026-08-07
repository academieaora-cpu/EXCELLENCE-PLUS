#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publier_facebook_organique.py — Publication organique réelle sur la Page
Facebook Excellence+, HORS Composio.

⚠️ Route volontairement à part, jamais la route par défaut. Composio publie
déjà l'organique Facebook/Instagram (ROU-EXC-001) ; republier le même
contenu ici créerait exactement le doublon que publish_scheduled.yml a
causé avant sa suppression le 03/08/2026. Ce script ne traite donc que les
posts dont le front matter porte explicitement :

    canal_publication: meta_direct

Un post sans ce champ (valeur par défaut : composio) est refusé, pas
ignoré silencieusement — le refus doit être visible dans la sortie.

Circuit ORGANIQUE : aucun budget, aucune des quatre portes Meta Ads — voir
graph_organique.py pour le pourquoi de son emplacement dans meta-ads/.

Usage :
    python3 meta-ads/scripts/publier_facebook_organique.py --post <post.md>
    python3 meta-ads/scripts/publier_facebook_organique.py --post <post.md> --image <fichier.jpg> --executer
"""
import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_organique import (  # noqa: E402
    ApprobationManquante, ContenuRefuse, ErreurNonClassee, PermissionRefusee,
    RateLimitPersistant, RouteNonAutorisee, TokenInvalide, alerter, appeler,
    enregistrer, lire_front_matter, lire_registre, page_id_organique,
    url_visuel_public, verifier_route_et_approbation,
)


def publier(repo: Path, chemin_post: Path, image: str, executer: bool) -> int:
    repo = Path(repo).resolve()
    fm = lire_front_matter(chemin_post)
    post_id = fm.get("post_id", chemin_post.stem)

    print(f"\n🌱 PUBLICATION ORGANIQUE DIRECTE — FACEBOOK — {post_id}\n")

    verifier_route_et_approbation(fm, post_id)  # lève RouteNonAutorisee / ApprobationManquante

    registre = lire_registre(repo)
    if post_id in registre:
        print(f"   🕓 Déjà publié — {registre[post_id]}")
        print("      Aucun appel : republier créerait un second post.\n")
        return 0

    page_id = page_id_organique(repo)
    texte = fm.get("_corps") or fm.get("texte", "")

    if not executer:
        print("   🧪 DRY-RUN — rien n'a été envoyé.")
        print(f"      Page cible : {page_id}")
        print(f"      Image      : {image or '(aucune — post texte seul)'}")
        print(f"      Texte      : {texte[:200]}{'…' if len(texte) > 200 else ''}")
        print("\n   Ajouter --executer pour l'exécution réelle.\n")
        return 0

    token = os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip()
    if not token:
        msg = "`META_PAGE_ACCESS_TOKEN` absent — aucune publication tentée."
        print(f"   ⛔ {msg}\n", file=sys.stderr)
        alerter(f"⛔ {msg}\nPost `{post_id}` (Facebook).")
        return 1

    try:
        if image:
            reponse = appeler(f"{page_id}/photos", {
                "url": url_visuel_public(image), "caption": texte, "published": "true",
            }, token)
        else:
            reponse = appeler(f"{page_id}/feed", {"message": texte}, token)
    except (TokenInvalide, PermissionRefusee, ContenuRefuse,
            RateLimitPersistant, ErreurNonClassee) as err:
        alerter(f"🚫 *{type(err).__name__}* — `{err}`\nPost `{post_id}` (Facebook) non publié.")
        print(f"   ⛔ {type(err).__name__} — {err}\n", file=sys.stderr)
        return 1

    meta_id = reponse.get("post_id") or reponse.get("id")
    enregistrer(repo, post_id, {
        "plateforme": "facebook", "meta_post_id": meta_id, "page_id": page_id,
        "publie_le_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    alerter(f"✅ Publié `{post_id}` → `{meta_id}` (Page {page_id})")
    print(f"   ✅ Publié — {meta_id}\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Publication Facebook organique directe (hors Composio).")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--post", type=Path, required=True)
    ap.add_argument("--image", type=str, default=None,
                    help="Nom de fichier dans visuels/approuves/ (optionnel)")
    ap.add_argument("--executer", action="store_true")
    args = ap.parse_args()

    if not args.post.is_file():
        print(f"❌ post introuvable : {args.post}", file=sys.stderr)
        return 2

    try:
        return publier(args.repo, args.post, args.image, args.executer)
    except (RouteNonAutorisee, ApprobationManquante) as err:
        print(f"   ⛔ {err}\n", file=sys.stderr)
        return 1
    except ValueError as err:
        print(f"❌ {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
