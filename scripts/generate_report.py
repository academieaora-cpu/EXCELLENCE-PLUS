#!/usr/bin/env python3
"""Génère le rapport hebdomadaire AORA × Excellence+"""
import glob, yaml, os, requests
from datetime import datetime

def main():
    stats = {"draft": 0, "BAT_soumis": 0, "BAP_recu": 0, "publié": 0}
    for f in glob.glob("contenu/**/*.md", recursive=True):
        with open(f) as fp:
            content = fp.read()
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        meta = yaml.safe_load(parts[1])
        statut = meta.get("statut", "draft")
        if statut in stats:
            stats[statut] += 1

    rapport = f"""
📊 RAPPORT HEBDOMADAIRE — Excellence+
Semaine du {datetime.now().strftime('%d/%m/%Y')}

Posts draft        : {stats['draft']}
BAT soumis         : {stats['BAT_soumis']}
BAP reçu (prêts)   : {stats['BAP_recu']}
Publiés            : {stats['publié']}

AORA × Excellence+ · Rapport auto-généré
    """.strip()

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        requests.post(webhook, json={"text": rapport})
    print(rapport)

if __name__ == "__main__":
    main()
