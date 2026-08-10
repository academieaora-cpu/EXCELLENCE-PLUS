#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_data.py — Fusionne les dix objets JSON en un unique data.js.

Lit depuis ./data/ :
  entries.json, weeks.json, months.json, pillars.json, platforms.json,
  platforms_hors_scope.json, statuts.json, meta_ads.json, kpi.json, meta.json

Écrit ./data.js avec, en global :
  window.ENTRIES / WEEKS / MONTHS / PILLARS / PLATFORMS /
  PLATFORMS_HORS_SCOPE / STATUTS / META_ADS / KPI / META

Utilise ensure_ascii=True : data.js est 100% ASCII (\\uXXXX pour les accents),
ce qui supprime toute corruption d'encodage au passage Python -> JS.
"""
import json
import os
import codecs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load(name, default):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return default
    with codecs.open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def js_const(name, obj):
    return "window.%s = %s;\n" % (name, json.dumps(obj, ensure_ascii=True, indent=2))


def main():
    entries = load("entries.json", [])
    weeks = load("weeks.json", [])
    months = load("months.json", [])
    pillars = load("pillars.json", [])
    platforms = load("platforms.json", [])
    platforms_hors_scope = load("platforms_hors_scope.json", [])
    statuts = load("statuts.json", [])
    meta_ads = load("meta_ads.json", [])
    kpi = load("kpi.json", {})
    meta = load("meta.json", {})

    out = (
        "/* data.js - genere par build_data.py - NE PAS editer a la main */\n"
        + js_const("ENTRIES", entries)
        + js_const("WEEKS", weeks)
        + js_const("MONTHS", months)
        + js_const("PILLARS", pillars)
        + js_const("PLATFORMS", platforms)
        + js_const("PLATFORMS_HORS_SCOPE", platforms_hors_scope)
        + js_const("STATUTS", statuts)
        + js_const("META_ADS", meta_ads)
        + js_const("KPI", kpi)
        + js_const("META", meta)
    )
    out_path = os.path.join(os.path.dirname(DATA), "data.js")
    with codecs.open(out_path, "w", encoding="utf-8") as f:
        f.write(out)

    print("data.js écrit — %d entrées · %d semaines · %d mois · %d piliers · "
          "%d plateformes · %d hors-scope · %d statuts · %d campagnes ads"
          % (len(entries), len(weeks), len(months), len(pillars), len(platforms),
             len(platforms_hors_scope), len(statuts), len(meta_ads)))


if __name__ == "__main__":
    main()
