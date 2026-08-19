# Mise en forme Unicode (YayText) — légendes Facebook Excellence+

**Décision du 18/08/2026.** Convention adoptée pour toute légende Facebook Excellence+ à partir
de cette date. S'applique **uniquement à la légende** (le texte publié avec le visuel) — jamais
au texte intégré dans l'image elle-même, qui reste en Inter réel via Canva/Pillow (voir
`direction-artistique-excellence-plus`). Les deux systèmes typographiques sont indépendants :
changer l'un ne change pas l'autre.

Outil de référence : [yaytext.com/fr/gras-italique](https://yaytext.com/fr/gras-italique/).
Reproduit ici en local (`scripts/mise_en_forme_yaytext.py`) pour rester déterministe et ne pas
dépendre d'un copier-coller manuel — la conversion caractère par caractère à la main est une
source d'erreur, en particulier sur les mots accentués.

---

## Pourquoi ces caractères et pas du markdown

Facebook n'a pas de markdown natif dans les légendes : `**gras**` ou `*italique*` s'affichent
tels quels, astérisques compris, au moment de la publication. Les caractères du bloc Unicode
*Mathematical Alphanumeric Symbols* (U+1D400–U+1D7FF) sont différents : ce sont d'autres lettres,
qui s'affichent grasses/italiques par construction, sans balise. Ils survivent au copier-coller
et s'affichent identiquement sur mobile, desktop, et dans Slack.

---

## Table de correspondance

| Élément de la légende | Style | Fonction |
|---|---|---|
| Titre / accroche (la ligne d'ouverture, ex. « — DEUX CHIFFRES, DEUX ANNÉES ») | **Gras (sans)** | `bold_sans` |
| Clause introduite ou encadrée par un tiret « — » à l'intérieur d'une phrase | **Gras / italique (empattement)** | `bold_italic_serif` |
| Phrase d'appui qui renforce l'argument central sans être l'accroche elle-même | **Gras / italique (empattement)** | `bold_italic_serif` |
| Phrase exacte « Écrivez-nous sur WhatsApp : » | **Gras / italique (empattement)** | `bold_italic_serif` |
| Numéro WhatsApp (`config/contacts.json`) | **Gras (sans)** | `bold_sans` |
| Phrase de contexte secondaire (comparaison générique, mise en perspective) | *Italique (serif)* | `italic_serif` |
| Corps principal — l'essentiel de chaque paragraphe | non stylé | — |
| Chiffres 93 % / 97 % quand ils sont cités seuls, hors clause à tiret | non stylé | — |
| Hashtags | **jamais stylé, sans exception** | — |

**Pourquoi le corps principal reste non stylé** : une légende où tout est en gras ne met plus
rien en avant. Le style marque l'exception ; le texte normal reste la référence de lecture — la
même logique que « CTA final unique » en `references/redaction.md` : trop de mise en avant équivaut
à aucune.

**Pourquoi les hashtags ne sont jamais stylés** — règle technique, pas éditoriale : Facebook et
Instagram détectent un hashtag à partir de son texte brut après le `#`. Des lettres Unicode
« mathématiques » stylées risquent de ne plus être reconnues comme un hashtag cliquable/cherchable
— un hashtag stylé est un hashtag mort à l'usage. Aucune exception, même pour un hashtag jugé
secondaire.

**Ce qui décide « peu important » vs « moyennement pertinent » vs non stylé** reste un jugement
éditorial — pas une règle mécanique. Repère utile : si la phrase est l'argument que le post existe
pour faire passer, elle reste non stylée. Si elle éclaire, illustre, ou referme l'argument sans le
porter, elle est candidate au style. La grille d'autocritique M4 (`references/redaction.md`)
s'applique aussi ici : si une hésitation subsiste, choisir la sobriété plutôt que le style.

---

## Limites Unicode assumées (à connaître, pas des bugs)

1. **Aucune lettre accentuée précomposée n'existe** dans ce bloc Unicode. Le script décompose le
   texte (NFD) : la lettre de base est stylée, l'accent combinant reste collé dessus (`é` → `e` +
   accent). C'est la méthode standard de ce type d'outil. Effet mesuré : un mot accentué stylé
   compte +1 caractère par lettre accentuée (l'accent devient un codepoint séparé) — négligeable
   sur la longueur d'une légende Facebook (40–300 mots), mais bon à savoir si un jour un compteur
   de caractères strict s'y ajoute.
2. **Gras / italique (empattement) n'a pas de chiffres dédiés.** Le script replie sur le chiffre
   Gras (serif) simple plutôt que de laisser un chiffre en romain au milieu d'un mot stylé. Si un
   chiffre sensible (93, 97) tombe dans une clause à tiret, vérifier visuellement avant BAT — la
   valeur ne change pas, seule la police change, mais une vérification reste plus sûre qu'une
   confiance aveugle au script.
3. **Italique (serif) n'a ni chiffres, ni le « h » minuscule** (trou historique du standard
   Unicode : U+1D455 n'a jamais été assigné). Le script utilise ℎ (U+210E — la même lettre que la
   constante de Planck, seule forme italique du « h » qui existe réellement en Unicode). Ne
   concerne que ce style ; les deux autres n'ont pas ce trou.
4. **Ponctuation et emoji ne changent jamais** — aucune variante stylée n'existe pour eux dans ce
   bloc. Un tiret, des guillemets, un emoji 📲 traversent la conversion identiques.

---

## Exemple réel — EXC-FB-2026-006

Texte actuellement dans le dépôt (`contenu/facebook/EXC-FB-2026-006.md`), inchangé par cette mise
à jour de skill — ceci illustre la convention, ce n'est pas une réécriture rétroactive :

```
— DEUX CHIFFRES, DEUX ANNÉES

93 % en 2023-2024. 97 % en 2024-2025. Ce n'est pas un slogan — c'est ce qu'on a mesuré, deux
années de suite.

Beaucoup de structures annoncent un taux de réussite. Peu peuvent montrer comment il évolue
d'une année sur l'autre. Chez Excellence+, cette évolution fait partie de la preuve : chaque
bilan sert à corriger le suivi, pas seulement à le constater.

C'est ce travail — mesuré, documenté, transmis aux familles chaque semaine — qui explique
l'écart entre les deux chiffres.

📲 Écrivez-nous sur WhatsApp : +237 699 403 969

#ExcellencePlus #Yaoundé #Résultats
```

Avec la convention appliquée (sortie réelle du script, testée) :

```
— 𝗗𝗘𝗨𝗫 𝗖𝗛𝗜𝗙𝗙𝗥𝗘𝗦, 𝗗𝗘𝗨𝗫 𝗔𝗡𝗡𝗘́𝗘𝗦

93 % en 2023-2024. 97 % en 2024-2025. Ce n'est pas un slogan — 𝒄'𝒆𝒔𝒕 𝒄𝒆 𝒒𝒖'𝒐𝒏 𝒂 𝒎𝒆𝒔𝒖𝒓𝒆́, 𝒅𝒆𝒖𝒙
𝒂𝒏𝒏𝒆́𝒆𝒔 𝒅𝒆 𝒔𝒖𝒊𝒕𝒆.

𝐵𝑒𝑎𝑢𝑐𝑜𝑢𝑝 𝑑𝑒 𝑠𝑡𝑟𝑢𝑐𝑡𝑢𝑟𝑒𝑠 𝑎𝑛𝑛𝑜𝑛𝑐𝑒𝑛𝑡 𝑢𝑛 𝑡𝑎𝑢𝑥 𝑑𝑒 𝑟𝑒́𝑢𝑠𝑠𝑖𝑡𝑒. 𝑃𝑒𝑢 𝑝𝑒𝑢𝑣𝑒𝑛𝑡 𝑚𝑜𝑛𝑡𝑟𝑒𝑟 𝑐𝑜𝑚𝑚𝑒𝑛𝑡 𝑖𝑙 𝑒́𝑣𝑜𝑙𝑢𝑒
𝑑'𝑢𝑛𝑒 𝑎𝑛𝑛𝑒́𝑒 𝑠𝑢𝑟 𝑙'𝑎𝑢𝑡𝑟𝑒. Chez Excellence+, cette évolution fait partie de la preuve : chaque bilan
sert à corriger le suivi, pas seulement à le constater.

C'est ce travail — 𝒎𝒆𝒔𝒖𝒓𝒆́, 𝒅𝒐𝒄𝒖𝒎𝒆𝒏𝒕𝒆́, 𝒕𝒓𝒂𝒏𝒔𝒎𝒊𝒔 𝒂𝒖𝒙 𝒇𝒂𝒎𝒊𝒍𝒍𝒆𝒔 𝒄𝒉𝒂𝒒𝒖𝒆 𝒔𝒆𝒎𝒂𝒊𝒏𝒆 — qui explique
l'écart entre les deux chiffres.

📲 𝑬́𝒄𝒓𝒊𝒗𝒆𝒛-𝒏𝒐𝒖𝒔 𝒔𝒖𝒓 𝑾𝒉𝒂𝒕𝒔𝑨𝒑𝒑 : +𝟮𝟯𝟳 𝟲𝟵𝟵 𝟰𝟬𝟯 𝟵𝟲𝟵

#ExcellencePlus #Yaoundé #Résultats
```

Repère de lecture du choix éditorial dans cet exemple :
- Titre en Gras (sans) — règle fixe.
- « c'est ce qu'on a mesuré, deux années de suite » stylé : clause introduite par un tiret.
- Le 2ᵉ paragraphe ouvre sur une comparaison générique (Italique — peu important) avant de
  revenir au fait propre à Excellence+ (non stylé — c'est l'argument).
- « mesuré, documenté, transmis aux familles chaque semaine » stylé : clause encadrée par deux
  tirets (incise), le reste de la phrase reste non stylé.
- CTA et numéro : règle fixe.
- 93 % et 97 % : non stylés (cités seuls, hors clause à tiret) — cohérent avec la règle de
  sobriété sur le corps principal.

---

## Utilisation du script

```bash
python3 scripts/mise_en_forme_yaytext.py --style bold_sans "Trois choses à vérifier"
python3 scripts/mise_en_forme_yaytext.py --style bold_italic_serif "Écrivez-nous sur WhatsApp :"
python3 scripts/mise_en_forme_yaytext.py --style italic_serif "Beaucoup de structures annoncent…"
```

Appliquer segment par segment selon la table ci-dessus, jamais le texte entier d'un coup — sinon
plus rien ne se distingue, et les hashtags se feraient styliser par erreur.

---

## Contrôle avant BAT

Ajout à l'autocritique standard (`references/redaction.md`, grille M4) quand la mise en forme a
été appliquée :
- Les hashtags sont-ils restés en texte brut, sans exception ?
- Les chiffres 93 %/97 % sont-ils toujours lisibles et exacts après conversion ?
- Le titre est-il bien le seul élément en Gras (sans) — pas de confusion avec le CTA ou le numéro ?
- Le corps principal reste-t-il majoritairement non stylé ?

---

*ACADÉMIE AORA · REDHEBDO-EXC-001 · Annexe mise en forme — 18/08/2026 · Contrat AORA-CCC-005*
