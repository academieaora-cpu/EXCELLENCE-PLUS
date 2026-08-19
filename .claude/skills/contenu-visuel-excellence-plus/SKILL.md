---
name: contenu-visuel-excellence-plus
description: >-
  Donne à la demande le contenu texte (M4) d'UN post Excellence+ pour une date précise du
  calendrier CE-EXC-001, avec le statut réel du visuel associé (prêt / à produire / bloqué).
  Déclenche ce skill dès que l'utilisateur demande « le contenu visuel du [date] », « le contenu
  du [date] selon le calendrier Excellence+ », « qu'est-ce qu'on publie le [date] », « donne-moi
  le post du [date] », « le texte du EXC-FB-[ID] ». Une seule date, à la demande — pas un lot ni
  la semaine (→ redaction-hebdo-excellence-plus) et pas un brief graphique complet avec palette et
  composition (→ direction-artistique-excellence-plus, jamais remplacé par ce skill).
---

# Contenu Visuel Excellence+ — à la demande

Répond à une question simple et récurrente : *« qu'est-ce qu'on publie le [date] ? »*
Donne le texte (M4) prêt à relire, et dit honnêtement où en est l'image (M5) — jamais l'un sans
l'autre.

> Ce skill ne produit pas d'image, ne publie rien, ne renseigne jamais `bap_recu_le`. Il ne
> remplace ni `direction-artistique-excellence-plus` (brief visuel complet, 2 variantes) ni
> `redaction-hebdo-excellence-plus` (rédaction en lot sur une semaine).

---

## 0. Position dans la chaîne

```
"Le contenu du [date] ?" (demande ponctuelle, une date)
         ↓
   ►  contenu-visuel-excellence-plus   ← ce skill
         ↓  texte M4 (v1 → autocritique → v2) + statut réel du visuel M5
   visuel à produire, rien ne bloque  → proposer direction-artistique-excellence-plus
   actif D1 manquant (pilier Preuve)  → blocage, même procédure que ce skill dédié
```

---

## 1. Chargement obligatoire

Cloner à froid `academieaora-cpu/EXCELLENCE-PLUS` — jamais la mémoire de conversation. Lire
dans l'ordre :

1. `CLAUDE.md`
2. `_base/couleurs/palette_excellence.json`
3. `_base/identite/brand_guidelines.md`
4. `config/creneaux.json`
5. `config/contacts.json`
6. `config/validation_formules.json` (si un email de validation doit être évoqué)

Fichier absent → arrêter, alerter l'équipe. Ne jamais produire dans le vide.

---

## 2. Trouver l'entrée calendrier

Source unique : `rapports/calendrier_editorial_excellence_plus.html` (CE-EXC-001).

```python
re.search(r'window\.ENTRIES\s*=\s*(\[.*?\n\]);', content, re.S)
```

Filtrer sur `date_iso` (YYYY-MM-DD). Pas d'entrée pour la date demandée → le dire, ne jamais
inventer un post.

Relever : `id`, `pilier`, `plateforme`, `jour`/`heure` (recouper avec `config/creneaux.json`,
qui fait foi en cas de divergence), `statut`, `bap_recu_le`.

---

## 3. Vérifier si le texte existe déjà

Avant de rédiger, chercher :
- `contenu/[plateforme]/[ID].md` dans le dépôt
- Recherche dans Slack `#excellence-plus` (canal `C0BLGLD4FNV`) sur l'ID du post

**Trouvé** → le présenter tel quel, signaler son statut (draft/BAT/BAP). S'il n'est pas committé
dans le dépôt alors qu'il existe sur Slack : signaler l'écart, c'est une perte de traçabilité.
**Absent** → rédiger, étape 4.

---

## 4. Rédiger (si absent)

Ton : rassurant · crédible · proche · déterminé. Voix AORA : direct · exigeant · proche ·
ambitieux.

Forme attendue (calée sur les posts déjà validés du projet), **avec la mise en forme Unicode
(YayText) adoptée le 18/08/2026** — détail, limites et exemple réel dans
`redaction-hebdo-excellence-plus/references/mise-en-forme-yaytext.md`, jamais dupliqué ici :

```
— 𝗔𝗖𝗖𝗥𝗢𝗖𝗛𝗘 𝗘𝗡 𝗠𝗔𝗝𝗨𝗦𝗖𝗨𝗟𝗘𝗦 (4 à 8 mots)

Paragraphe d'ouverture — situe le sujet, sans vendre.

Paragraphe de développement — le concret, propre à l'angle du pilier du jour.

Phrase de chiffres — 93 % (2023-2024) / 97 % (2024-2025) uniquement, si pertinent.

📲 𝑬́𝒄𝒓𝒊𝒗𝒆𝒛-𝒏𝒐𝒖𝒔 𝒔𝒖𝒓 𝑾𝒉𝒂𝒕𝒔𝑨𝒑𝒑 : +𝟮𝟯𝟳 𝟲𝟵𝟵 𝟰𝟬𝟯 𝟵𝟲𝟵

#ExcellencePlus #Yaoundé #[thème]
```

Titre en Gras (sans), CTA + numéro en Gras/italique (empattement) et Gras (sans) — règles fixes.
Les clauses à tiret et le curseur peu important/moyennement pertinent restent un choix éditorial
au cas par cas (voir le fichier référencé). **Les hashtags ne sont jamais stylés** — un hashtag
en caractères Unicode "mathématiques" risque de ne plus être reconnu comme cliquable par
Facebook/Instagram.

*Correction 18/08/2026 : la ligne CTA utilisait « CTA — WhatsApp : » dans une version antérieure
de ce gabarit ; corrigée en « Écrivez-nous sur WhatsApp : », la formule réellement en usage dans
EXC-FB-2026-005/006 et autorisée par `brand_guidelines.md`.*

**Angle par pilier** — pour ne pas empiéter sur un post déjà publié sur un autre pilier :

| Pilier | Angle du texte |
|---|---|
| Autorité éducative | Un conseil concret aux parents — une idée, rien à acheter |
| La méthode Excellence+ | Le mécanisme de suivi — vérifier qu'un post récent ne l'a pas déjà couvert |
| La preuve | La mesure elle-même — ce qui est tracé/documenté, pas le mécanisme de suivi |

**6 portes bloquantes** (détail complet dans
`direction-artistique-excellence-plus/references/portes-bloquantes.md`, s'appliquent au texte à
l'identique) :

1. Mineur identifiable nommé/décrit → jamais sans autorisation écrite au dossier
2. Chiffres → seuls 93 % et 97 %, jamais le nombre d'enseignants ni d'élèves suivis
3. « Excellence+ » — jamais « Excellence++ »
4. Aucune promesse de résultat individuel
5. Aucun concurrent nommé
6. CTA WhatsApp uniquement, seul numéro lu dans `config/contacts.json` — ne jamais coder le
   numéro en dur dans le skill

---

## 5. Autocritique obligatoire

Standard AORA — jamais sauté :
1. Rédiger le texte (v1)
2. Formuler 2 à 3 faiblesses explicites (chevauchement de pilier, CTA répété, angle trop
   abstrait, etc.)
3. Livrer une v2 corrigée

---

## 6. Statut du visuel (M5) — toujours inclus, jamais produit ici

- Identifier l'archétype du pilier (Conseil / Dispositif / Document —
  `direction-artistique-excellence-plus/references/archetypes-piliers.md`).
- **Pilier La preuve** : vérifier `visuels/photos_terrain/` — actif D1 présent ou non.
  - Absent → même format de blocage que `direction-artistique-excellence-plus` :
    ```
    🚩 BLOCAGE — [ID post]
    Porte  : Doctrine iconographique — D1 obligatoire (pilier La Preuve)
    Motif  : [constat factuel sur l'état du dossier]
    Action : [une seule action humaine, nommément attribuée]
    ```
  - Présent → signaler que le brief visuel peut être demandé à
    `direction-artistique-excellence-plus`.
- **Autres piliers (D2 par défaut)** : signaler que l'image reste à produire via
  `direction-artistique-excellence-plus` — pas de blocage par défaut.

---

## 7. Ce que ce skill ne fait jamais

- Ne commite ni ne pousse rien sans demande explicite.
- Ne poste jamais dans Slack sans demande explicite.
- Ne renseigne ni ne devine `bap_recu_le`.
- Ne produit pas le brief visuel complet (variantes, palette, composition) —
  `direction-artistique-excellence-plus` seul le fait.
- Ne traite pas un lot de dates — `redaction-hebdo-excellence-plus` seul le fait.

---

## Commande

```
@contenu [date ou ID]   → texte + statut visuel pour cette date/post, à la demande
```

## Langue

Français. Réponse directement exploitable, sans jargon de production dans la sortie finale.

---

*Créé le 15/08/2026, à partir du cas EXC-FB-2026-006 (22/08/2026). Mis à jour le 18/08/2026 :
gabarit avec mise en forme Unicode + correction de la formule CTA.*
