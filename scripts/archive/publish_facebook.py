#!/usr/bin/env python3
"""AORA — Publication Facebook (Graph API) pour Excellence+"""
import os
import requests

GRAPH_URL = "https://graph.facebook.com/v19.0"


def publish(meta, body):
    """Publie un post sur la Page Facebook Excellence+. Retourne la réponse Graph API."""
    page_id = os.environ["FB_PAGE_ID"]
    token = os.environ["FB_ACCESS_TOKEN"]
    image_path = meta.get("visuel_ref")

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img:
            resp = requests.post(
                f"{GRAPH_URL}/{page_id}/photos",
                params={"access_token": token},
                data={"caption": body, "published": "true"},
                files={"source": img},
            )
    else:
        resp = requests.post(
            f"{GRAPH_URL}/{page_id}/feed",
            params={"access_token": token},
            data={"message": body},
        )

    resp.raise_for_status()
    return resp.json()
