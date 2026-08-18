#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mise_en_forme_yaytext.py — AORA × Excellence+ (AORA-CCC-005)

Convertisseur Unicode "texte stylé" pour légendes Facebook — même principe que
https://yaytext.com/fr/gras-italique/, en local et sans dépendance.

Facebook (comme Instagram/TikTok) n'a pas de markdown natif dans les légendes : les balises
**gras** ou *italique* s'affichent telles quelles, lettre pour lettre, au moment de la
publication. Le seul moyen d'obtenir un vrai rendu gras/italique dans une légende est
d'utiliser des caractères Unicode qui SONT visuellement gras/italique (bloc "Mathematical
Alphanumeric Symbols", U+1D400–U+1D7FF) — ce ne sont pas des balises, ce sont d'autres
caractères.

Trois styles couverts (ceux utilisés dans la convention Excellence+ du 18/08/2026) :
    bold_sans           "Gras (sans)"                     ex. 𝗧𝗶𝘁𝗿𝗲
    bold_italic_serif   "Gras / italique (empattement)"   ex. 𝘁𝗶𝗿𝗲𝘁
    italic_serif        "Italique (serif)"                ex. 𝑝𝑒𝑢 𝑖𝑚𝑝𝑜𝑟𝑡𝑎𝑛𝑡

Limites Unicode assumées (documentées, pas des bugs) :
  - Aucune lettre accentuée n'existe nativement dans ce bloc. On décompose (NFD) : la lettre
    de base est stylée, l'accent combinant reste collé dessus. Effet secondaire mesuré : un
    mot accentué stylé compte +1 caractère par lettre accentuée (accent = codepoint séparé).
  - Le style bold_italic_serif n'a pas de variante chiffre dédiée -> repli sur le chiffre
    Gras (serif) plutôt que de laisser un chiffre en romain au milieu d'un mot stylé.
  - Le style italic_serif n'a NI variante chiffre, NI le "h" minuscule (trou historique du
    standard Unicode) -> chiffres laissés en romain, "h" remplacé par ℎ (U+210E, la même
    lettre que la constante de Planck, seule forme italique du "h" qui existe en Unicode).
  - Aucune ponctuation, aucun emoji, aucun hashtag n'a de variante stylée : ils traversent la
    conversion inchangés. NE JAMAIS appeler ce script sur un hashtag — Facebook/Instagram
    risquent de ne plus le reconnaître comme cliquable (voir SKILL.md, §Mise en forme Unicode).

Usage :
    python3 mise_en_forme_yaytext.py --style bold_sans "Trois choses à vérifier"
    python3 mise_en_forme_yaytext.py --style bold_italic_serif "Écrivez-nous sur WhatsApp :"
    echo "699 403 969" | python3 mise_en_forme_yaytext.py --style bold_sans --stdin
"""
import argparse
import sys
import unicodedata

STYLES = {
    "bold_sans": {"upper": 0x1D5D4, "lower": 0x1D5EE, "digit": 0x1D7EC},
    "bold_italic_serif": {"upper": 0x1D468, "lower": 0x1D482, "digit": 0x1D7CE},
    "italic_serif": {"upper": 0x1D434, "lower": 0x1D44E, "digit": None},
}

ITALIC_LOWER_H_EXCEPTION = "\u210E"  # U+1D455 n'existe pas en Unicode ; repli standard.


def _style_letter(ch: str, style_name: str, spec: dict) -> str:
    if "A" <= ch <= "Z":
        return chr(spec["upper"] + (ord(ch) - ord("A")))
    if "a" <= ch <= "z":
        if ch == "h" and style_name == "italic_serif":
            return ITALIC_LOWER_H_EXCEPTION
        return chr(spec["lower"] + (ord(ch) - ord("a")))
    if "0" <= ch <= "9":
        if spec["digit"] is None:
            return ch
        return chr(spec["digit"] + (ord(ch) - ord("0")))
    return ch  # ponctuation / espace / emoji / hashtag marker : jamais transformé


def style_text(text: str, style_name: str) -> str:
    """Stylise `text` selon `style_name` ('bold_sans' | 'bold_italic_serif' | 'italic_serif').
    Préserve les accents français par décomposition NFD + réattachement de l'accent combinant."""
    if style_name not in STYLES:
        raise ValueError(f"Style inconnu : {style_name!r}. Attendu : {list(STYLES)}")
    spec = STYLES[style_name]
    decomposed = unicodedata.normalize("NFD", text)
    out = []
    for ch in decomposed:
        if unicodedata.combining(ch):
            out.append(ch)
        else:
            out.append(_style_letter(ch, style_name, spec))
    return "".join(out)


def _main() -> int:
    parser = argparse.ArgumentParser(description="Convertisseur Unicode YayText — AORA Excellence+")
    parser.add_argument("--style", required=True, choices=list(STYLES), help="Style cible")
    parser.add_argument("text", nargs="?", help="Texte à styliser (ou utiliser --stdin)")
    parser.add_argument("--stdin", action="store_true", help="Lire le texte depuis stdin")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read().rstrip("\n")
    elif args.text:
        text = args.text
    else:
        parser.error("Fournir le texte en argument ou utiliser --stdin")
        return 2

    sys.stdout.write(style_text(text, args.style) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
