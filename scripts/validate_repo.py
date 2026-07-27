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
]

FORBIDDEN_TERMS = ["Excellence++"]
FORBIDDEN_TERMS_EXCEPTIONS = {
    "CLAUDE.md",
    "_base/identite/brand_guidelines.md",
    "_base/identite/plateforme_marque.md",
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


def main():
    checks = {
        "Fichiers de référence obligatoires": check_required_files(),
        "JSON": check_json(),
        "YAML (workflows)": check_yaml(),
        "Python (scripts/)": check_python(),
        "Frontmatter des posts (contenu/)": check_post_frontmatter(),
        "Termes interdits": check_forbidden_terms(),
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
