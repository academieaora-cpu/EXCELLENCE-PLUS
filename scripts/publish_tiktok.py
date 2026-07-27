#!/usr/bin/env python3
"""AORA — Publication TikTok (Content Posting API) pour Excellence+"""
import os
import requests

API_URL = "https://open.tiktokapis.com/v2/post/publish/content/init/"


def _raw_url(video_path):
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    return f"https://raw.githubusercontent.com/{repo}/main/{video_path}"


def publish(meta, body):
    """Publie une vidéo TikTok par URL (PULL_FROM_URL) depuis visuels/approuves/."""
    token = os.environ["TIKTOK_ACCESS_TOKEN"]
    video_path = meta.get("visuel_ref")

    payload = {
        "post_info": {
            "title": body,
            "privacy_level": "PUBLIC_TO_EVERYONE",
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": _raw_url(video_path),
        },
    }
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()
