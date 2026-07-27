#!/usr/bin/env python3
"""
AORA — Moteur publication Excellence+
Vérifie les posts BAP reçu et publie via Composio.
"""
import os, json, glob
from datetime import datetime, timezone
import yaml
import requests

WAT_OFFSET = 1
now_utc = datetime.now(timezone.utc)
now_wat_hour = (now_utc.hour + WAT_OFFSET) % 24
now_date = now_utc.strftime("%Y-%m-%d")

def load_post(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, None
    return yaml.safe_load(parts[1]), parts[2].strip()

def send_slack_alert(message):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        requests.post(webhook, json={"text": f"🚨 AORA Bot — {message}"})

def main():
    posts = glob.glob("contenu/**/*.md", recursive=True)
    published = 0
    for filepath in posts:
        meta, body = load_post(filepath)
        if not meta or meta.get("statut") in ["publié", "archivé", "draft"]:
            continue
        if meta.get("statut") == "BAP_recu":
            if not meta.get("bap_recu_le"):
                send_slack_alert(f"BAP manquant sur {meta.get('id')} — publication bloquée")
                continue
            pub_date = str(meta.get("date_publication", ""))
            pub_hour = int(meta.get("heure_publication", "08:00").split(":")[0])
            if pub_date == now_date and pub_hour == now_wat_hour:
                print(f"→ Publier : {meta.get('id')} sur {meta.get('plateforme')}")
                # Appel Composio ici selon plateforme
                published += 1
    print(f"Session terminée — {published} post(s) publié(s)")

if __name__ == "__main__":
    main()
