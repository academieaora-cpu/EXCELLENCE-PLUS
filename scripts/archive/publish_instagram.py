#!/usr/bin/env python3
"""AORA — Publication Instagram (Graph API) pour Excellence+"""
import os
import time
import requests

GRAPH_URL = "https://graph.facebook.com/v19.0"


def _raw_url(image_path):
    # L'API Instagram exige une image_url publique — le repo GitHub sert de source
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    return f"https://raw.githubusercontent.com/{repo}/main/{image_path}"


def publish(meta, body):
    """Publie un post Instagram en 2 temps : création du conteneur média, puis publication."""
    account_id = os.environ["INSTAGRAM_ACCOUNT_ID"]
    token = os.environ["FB_ACCESS_TOKEN"]
    image_path = meta.get("visuel_ref")

    container = requests.post(
        f"{GRAPH_URL}/{account_id}/media",
        params={"access_token": token},
        data={"image_url": _raw_url(image_path), "caption": body},
    )
    container.raise_for_status()
    creation_id = container.json()["id"]

    time.sleep(5)  # laisser Instagram traiter le média avant publication

    resp = requests.post(
        f"{GRAPH_URL}/{account_id}/media_publish",
        params={"access_token": token},
        data={"creation_id": creation_id},
    )
    resp.raise_for_status()
    return resp.json()
