#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publier_instagram_organique.py — Publication organique réelle sur le compte
Instagram Excellence+, HORS Composio.

Mêmes garde-fous que publier_facebook_organique.py : ne traite que les
posts dont canal_publication vaut explicitement meta_direct, exige un
bap_recu_le, partage le même registre d'idempotence — voir ce fichier et
graph_organique.py.

Contrainte propre à Instagram : la publication exige une URL d'image
joignable publiquement (jamais un fichier local envoyé en octets), et se
fait en deux temps — créer le conteneur média, puis le publier — jamais un
seul appel.

Usage :
    python3 meta-ads/scripts/publier_instagram_organique.py --post <post.md> --image <fichier.jpg>
    python3 meta-ads/scripts/publier_instagram_organique.py --post <post.md> --image <fichier.jpg> --executer
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_organique import (  # noqa: E402
    ApprobationManquante, ContenuRefuse, ErreurNonClassee, PermissionRefusee,
    RateLimitPersistant, RouteNonAutorisee, TokenInvalide, alerter, appeler,
    enregistrer, instagram_actor_id, lire_front_matter, lire_registre,
    url_visuel_public, verifier_route_et_approbation,
)

DELAI_CONTENEUR_SECONDES = 3  # laisser Meta traiter le média avant de publier


def publier(repo: Path, chemin_post: Path, image: str, executer: bool) -> int:
    repo = Path(repo).resolve()
    fm = lire_front_matter(chemin_post)
    post_id = fm.get("post_id", chemin_post.stem)

    print(f"\n🌱 PUBLICATION ORGANIQUE DIRECTE — INSTAGRAM — {post_id}\n")

    verifier_route_et_approbation(fm, post_id)

    if not image:
        print("   ⛔ Instagram exige une image — pas de post texte seul sur cette "
              "plateforme. Fournir --image.\n")
        return 1

    registre = lire_registre(repo)
    if post_id in registre:
        print(f"   🕓 Déjà publié — {registre[post_id]}\n")
        return 0

    ig_id = instagram_actor_id(repo)
    texte = fm.get("_corps") or fm.get("texte", "")
    url_image = url_visuel_public(image)

    if not executer:
        print("   🧪 DRY-RUN — rien n'a été envoyé.")
        print(f"      Compte IG : {ig_id}")
        print(f"      Image     : {url_image}")
        print(f"      Légende   : {texte[:200]}{'…' if len(texte) > 200 else ''}")
        print("\n   Ajouter --executer pour l'exécution réelle.\n")
        return 0

    token = os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip()
    if not token:
        msg = "`META_PAGE_ACCESS_TOKEN` absent — aucune publication tentée."
        print(f"   ⛔ {msg}\n", file=sys.stderr)
        alerter(f"⛔ {msg}\nPost `{post_id}` (Instagram).")
        return 1

    try:
        conteneur = appeler(f"{ig_id}/media", {"image_url": url_image, "caption": texte}, token)
        conteneur_id = conteneur.get("id")
        if not conteneur_id:
            raise ErreurNonClassee(f"pas d'id de conteneur retourné : {conteneur}")
        time.sleep(DELAI_CONTENEUR_SECONDES)
        reponse = appeler(f"{ig_id}/media_publish", {"creation_id": conteneur_id}, token)
    except (TokenInvalide, PermissionRefusee, ContenuRefuse,
            RateLimitPersistant, ErreurNonClassee) as err:
        alerter(f"🚫 *{type(err).__name__}* — `{err}`\nPost `{post_id}` (Instagram) non publié.")
        print(f"   ⛔ {type(err).__name__} — {err}\n", file=sys.stderr)
        return 1

    meta_id = reponse.get("id")
    enregistrer(repo, post_id, {
        "plateforme": "instagram", "meta_post_id": meta_id, "instagram_actor_id": ig_id,
        "publie_le_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    alerter(f"✅ Publié `{post_id}` → `{meta_id}` (IG {ig_id})")
    print(f"   ✅ Publié — {meta_id}\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Publication Instagram organique directe (hors Composio).")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--post", type=Path, required=True)
    ap.add_argument("--image", type=str, required=True,
                    help="Nom de fichier dans visuels/approuves/")
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
