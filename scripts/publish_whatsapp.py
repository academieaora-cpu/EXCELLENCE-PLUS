#!/usr/bin/env python3
"""AORA — Publication WhatsApp Channel pour Excellence+"""
import os
import requests

GRAPH_URL = "https://graph.facebook.com/v19.0"


def publish(meta, body):
    """Publie un message sur le WhatsApp Channel Excellence+.
    Nécessite l'accès API "WhatsApp Channels" activé sur le compte Business Meta."""
    channel_id = os.environ["WHATSAPP_CHANNEL_ID"]
    token = os.environ["WHATSAPP_ACCESS_TOKEN"]

    resp = requests.post(
        f"{GRAPH_URL}/{channel_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"messaging_product": "whatsapp", "text": {"body": body}},
    )
    resp.raise_for_status()
    return resp.json()
