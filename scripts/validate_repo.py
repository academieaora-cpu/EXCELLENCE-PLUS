#!/usr/bin/env python3
"""AORA — Validation CI du repo Excellence+"""
import glob
import json
import py_compile
import sys

import yaml

REQUIRED_FILES = [
    "_base/identite/brand_guidelines.md",
    "_base/identite/plateforme_marque.md",
    "calendrier/semaine_active.json",
    "_base/couleurs/palette_excellence.json",
    "config/creneaux.json",
]

FORBIDDEN_TERMS = ["Excellence++"]
FORBIDDEN_TERMS_EXCEPTIONS = {
    "CLAUDE.md",
    "_base/identite/brand_guidelines.md",
    "_base/identite/plateforme_marque.md",
    # Documentation qui ÉNONCE l'interdiction, au même titre que les trois
    # fichiers ci-dessus. L'exception vaut pour la doc, jamais pour un gabarit
    # de contenu ou de créatif : le corps d'un gabarit finit copié dans un vrai
    # livrable, et le terme interdit avec lui.
    "meta-ads/README.md",
}


def check_required_files():
    return [f"{f} est absent" for f in REQUIRED_FILES if not glob.glob(f)]


def check_json():
    errors = []
    for f in glob.glob("**/*.json", recursive=True):
        try:
            json.load(open(f, encoding="utf-8"))
        except Exception as e:
            errors.append(f"{f}: {e}")
    return errors


def check_yaml():
    errors = []
    for f in glob.glob(".github/workflows/*.yml"):
        try:
            yaml.safe_load(open(f, encoding="utf-8"))
        except Exception as e:
            errors.append(f"{f}: {e}")
    return errors


def check_python():
    errors = []
    for f in glob.glob("scripts/*.py"):
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(str(e))
    return errors


def check_post_frontmatter():
    errors = []
    for f in glob.glob("contenu/**/*.md", recursive=True):
        content = open(f, encoding="utf-8").read()
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{f}: frontmatter YAML manquant ou mal formé")
            continue
        try:
            yaml.safe_load(parts[1])
        except Exception as e:
            errors.append(f"{f}: {e}")
    return errors


def check_forbidden_terms():
    errors = []
    for f in glob.glob("**/*.md", recursive=True) + glob.glob("**/*.json", recursive=True):
        if f in FORBIDDEN_TERMS_EXCEPTIONS:
            continue
        content = open(f, encoding="utf-8").read()
        for term in FORBIDDEN_TERMS:
            if term in content:
                errors.append(f'{f}: contient le terme interdit "{term}"')
    return errors


def check_placeholders_valides():
    """Un A_REMPLIR dans un post DÉJÀ VALIDÉ est une erreur bloquante.

    Portée volontairement étroite : un brouillon a le droit de contenir des
    valeurs à remplir, c'est son état normal. Ce qui ne doit jamais arriver,
    c'est qu'un post porte un BAP client et parte en publication avec un
    numéro WhatsApp factice. Contrôler plus large rendrait la CI rouge en
    permanence pendant la production — et une CI rouge en permanence n'est
    plus lue par personne.
    """
    errors = []
    for f in glob.glob("contenu/**/*.md", recursive=True):
        with open(f, encoding="utf-8") as fp:
            content = fp.read()
        if "A_REMPLIR" not in content:
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            meta = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            continue
        bap = meta.get("bap_recu_le")
        if bap not in (None, "", "null"):
            errors.append(
                f"{f}: BAP reçu le {bap} mais contient encore A_REMPLIR — "
                f"publication impossible en l'état"
            )
    return errors


def main():
    checks = {
        "Fichiers de référence obligatoires": check_required_files(),
        "JSON": check_json(),
        "YAML (workflows)": check_yaml(),
        "Python (scripts/)": check_python(),
        "Frontmatter des posts (contenu/)": check_post_frontmatter(),
        "Termes interdits": check_forbidden_terms(),
        "Valeurs A_REMPLIR dans un post validé": check_placeholders_valides(),
    }

    failed = False
    for name, errors in checks.items():
        if errors:
            failed = True
            print(f"✗ {name}")
            for e in errors:
                print(f"    {e}")
        else:
            print(f"✓ {name}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
