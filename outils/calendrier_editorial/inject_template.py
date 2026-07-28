#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_template.py — Produit un fichier HTML AUTONOME.

Remplace dans le template :
  __DATA_JS__        -> contenu de data.js
  __LOGO_AORA__       -> data URI base64 du logo AORA
  __LOGO_EXCELLENCE__ -> data URI base64 du logo Excellence+

Usage :
  python3 inject_template.py --template template.html --data data.js \
      --logo-aora aora_logo_400w.png --logo-excellence excellence_plus_logo_500x500.png \
      --out out/calendrier_editorial_excellence_plus.html
"""
import argparse
import base64
import os
import codecs
import mimetypes


def data_uri(path):
    if not path or not os.path.exists(path):
        return None
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--logo-aora", default=None)
    ap.add_argument("--logo-excellence", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with codecs.open(a.template, "r", encoding="utf-8") as f:
        html = f.read()
    with codecs.open(a.data, "r", encoding="utf-8") as f:
        data_js = f.read()

    html = html.replace("__DATA_JS__", data_js)

    la = data_uri(a.logo_aora)
    le = data_uri(a.logo_excellence)
    if la:
        html = html.replace("__LOGO_AORA__", la)
    if le:
        html = html.replace("__LOGO_EXCELLENCE__", le)
    html = html.replace("__LOGO_AORA__", "")
    html = html.replace("__LOGO_EXCELLENCE__", "")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with codecs.open(a.out, "w", encoding="utf-8") as f:
        f.write(html)

    size = os.path.getsize(a.out)
    print("HTML autonome écrit : %s (%.0f Ko) — logo AORA:%s, logo Excellence+:%s"
          % (a.out, size / 1024, "oui" if la else "non", "oui" if le else "non"))


if __name__ == "__main__":
    main()
