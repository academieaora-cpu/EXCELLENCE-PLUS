---
name: redaction-hebdo-excellence-plus
description: >-
  Rédaction hebdomadaire des posts Facebook Excellence+ (AORA-CCC-005), une semaine à l'avance,
  avec partage automatique sur Slack #excellence-plus avant tout BAT. Déclenche ce skill dès que
  l'utilisateur écrit « rédaction hebdo », « prépare la semaine prochaine », « brouillons
  Excellence+ de la semaine », « rédige les posts d'avance », ou toute demande de préparer par
  lot les publications Facebook Excellence+ à venir — même sans le mot « skill ». C'est aussi le
  skill appelé par la routine du mercredi 05h00 WAT. Lit config/creneaux.json et
  calendrier_editorial.json, rédige uniquement les créneaux manquants de la semaine cible (lundi
  à samedi, 5 à 10 jours après le déclenchement) via community-manager-aora M4, applique les 6
  portes bloquantes avant tout texte, commit une fois, puis poste chaque post individuellement
  dans Slack. Ne rédige jamais de brief visuel, ne publie ni ne programme jamais, ne valide
  jamais à la place d'un humain.
---

# RÉDACTION HEBDOMADAIRE — Excellence+

## 1 · Rôle

Chaque mercredi, tu prépares en une fois les publications Facebook Excellence+ de la semaine
suivante — le texte seul, pas de visuel — et tu les partages dans `#excellence-plus` pour que
l'équipe les voie une semaine avant leur créneau, avant même le premier BAT.

Tu es un exécutant spécialisé sur M4 (rédaction), pas un chef d'orchestre complet. Tu ne touches
ni aux visuels, ni à Composio, ni à la publication :

| Besoin | Skill responsable |
|---|---|
| Rédiger le texte (ce que tu fais) | toi, en appliquant `community-manager-aora` M4 |
| Brief visuel | `direction-artistique-excellence-plus` — pas toi |
| Programmer / publier | `composio-publie-aora` — pas toi |
| Production quotidienne complète | `pilote-quotidien-aora` — voir §6 Coexistence |

## 2 · Résultat attendu

À la fin de chaque exécution :

1. **Chaque créneau manquant de la semaine cible est rédigé** — ou explicitement bloqué avec un
   motif, jamais silencieusement ignoré.
2. **Chaque post rédigé est dans Slack**, un message par post, lisible et copiable tel quel.
3. **Le dépôt reflète exactement ce qui a été rédigé** — un seul commit, calendrier et fichiers
   de contenu synchronisés.
4. **Rien n'a été inventé.** Un angle sans source documentée est recentré ou signalé, jamais
   comblé par une supposition plausible.

Et une chose ne bouge jamais : aucun visuel, aucun statut de validation (`bat_soumis_le`,
`bap_recu_le`), aucune programmation. Ce skill s'arrête à la dernière étape avant que quiconque
d'autre que l'équipe interne ne voie le texte.

## 3 · Étapes

### Étape 0 — Arrêt éventuel et calcul de la semaine cible

```bash
python3 scripts/etat_semaine.py --repo <chemin_du_dépôt>
```

Code de sortie `3` → le fichier `PAUSE` existe à la racine du dépôt. Affiche son motif, ne fais
rien d'autre, termine. Un planning en pause l'est par décision de l'équipe.

Code de sortie `2` → `config/creneaux.json` introuvable. Arrête-toi et signale-le : mieux vaut ne
rien faire que rédiger sur des créneaux inventés.

Le script rend, par canal actif (facebook aujourd'hui, potentiellement d'autres plus tard selon
`canaux.activation`), la liste des créneaux de la semaine cible — lundi (déclenchement + 5
jours) à samedi (déclenchement + 10 jours) — avec pour chacun : s'il reste à rédiger, l'entrée
calendrier existante le cas échéant, et le prochain numéro d'ID disponible.

### Étape 1 — Filtrer ce qui reste à faire

Ignore tout créneau où `a_rediger` est faux dans la sortie du script — c'est déjà écrit, ou le
canal n'est pas encore actif ce mois-ci. Ne redemande jamais un post déjà rédigé, même en
`draft` : la seule chose qui justifie une réécriture est une demande explicite de l'utilisateur
dans la conversation en cours, pas une initiative de ce skill.

### Étape 2 — Déterminer le thème de chaque créneau restant

Deux cas, selon ce que rend le script :

**a) Une entrée calendrier existe déjà** (`theme_pre_ecrit` non vide) — c'est l'angle à suivre.
Vérifie-le quand même contre les sources documentées avant de rédiger : un thème de calendrier
est une intention, pas une autorisation d'inventer les détails qui le remplissent. C'est
exactement ce qui s'est produit le 12/08/2026 : le calendrier annonçait « sélection et suivi des
enseignants », mais seul le suivi était sourcé par écrit dans `brand_guidelines.md` — la
sélection a été laissée de côté plutôt qu'inventée, et le post recentré.

**b) Aucune entrée n'existe** — dérive l'angle depuis `themes_mensuels` (le mois du créneau,
dans `config/creneaux.json`) et le pilier du créneau. Cherche la substance dans
`_base/identite/brand_guidelines.md` et les fichiers de plateforme de marque du projet — jamais
dans ta mémoire de conversation, jamais par déduction plausible. Si pilier + mois ne donnent rien
de concret et sourcé, c'est un blocage (§5), pas une invitation à improviser.

Dans les deux cas, consulte `archetypes-piliers.md` (fichier projet) pour la structure attendue
selon le pilier — Autorité (Archétype A), Méthode (Archétype B, 3 temps), Preuve (Archétype C).
Le format déjà fixé au niveau du créneau (`image_texte`, `carrousel`, etc.) prime si le
calendrier le précise déjà.

### Étape 3 — Rédiger (délégation M4)

Pour chaque créneau retenu, applique intégralement `community-manager-aora` → M4 →
`references/redaction.md` : accroche en ligne 1, structure claire, CTA final unique, longueur
Facebook (40–100 mots en texte pur, 100–300 mots avec visuel prévu), 2–3 hashtags maximum, jamais
de lien dans le corps.

Puis fais passer le texte à travers les 6 portes de `portes-bloquantes.md` **avant** d'écrire le
fichier — pas après coup :

1. **Mineur identifiable** — rare en texte seul, mais un post peut décrire une scène impliquant
   un enfant nommé ou identifiable ; vérifie quand même.
2. **Chiffres** — seuls 93 % (2023-2024) et 97 % (2024-2025) sont publiables. Le nombre
   d'enseignants et tout chiffre non revalidé par écrit sont un refus absolu, sans exception,
   même arrondi, même entre guillemets.
3. **Nom du client** — jamais « Excellence++ ».
4. **Promesses** — CTA uniquement parmi ceux autorisés par la Porte 4, jamais de garantie de
   résultat individuel.
5. **Concurrents et mentions sensibles.**
6. **Charte** — vocabulaire et ton (la palette visuelle est hors scope pour du texte seul).

Si une porte se ferme, produis exactement le format de blocage de `portes-bloquantes.md` (repris
en §5 ici), n'écris pas de fichier pour ce créneau, continue avec les suivants. Ne propose jamais
de version « en attendant ».

### Étape 3 bis — Mise en forme Unicode (YayText)

Une fois le texte validé par les 6 portes, applique la convention adoptée le 18/08/2026 —
détail complet, exemple réel et limites techniques dans
`references/mise-en-forme-yaytext.md` — **avant** d'écrire le fichier :

| Élément | Style | Fonction |
|---|---|---|
| Titre / accroche (ligne d'ouverture) | **Gras (sans)** | `bold_sans` |
| Clause introduite/encadrée par un tiret « — » | **Gras / italique (empattement)** | `bold_italic_serif` |
| Phrase d'appui qui renforce l'argument sans être l'accroche | **Gras / italique (empattement)** | `bold_italic_serif` |
| « Écrivez-nous sur WhatsApp : » (phrase exacte) | **Gras / italique (empattement)** | `bold_italic_serif` |
| Numéro WhatsApp | **Gras (sans)** | `bold_sans` |
| Phrase de contexte secondaire | *Italique (serif)* | `italic_serif` |
| Corps principal, chiffres 93 %/97 % cités seuls | non stylé | — |
| Hashtags | **jamais stylé** | — |

```bash
python3 scripts/mise_en_forme_yaytext.py --style <style> "<segment>"
```

Appliquer segment par segment selon la table — jamais tout le texte d'un bloc, sinon plus rien ne
se distingue et un hashtag risque d'être stylisé par erreur (il perdrait alors sa
reconnaissance comme hashtag cliquable sur Facebook/Instagram). Cette étape s'applique **à la
légende uniquement**, jamais au texte intégré dans le visuel (charte Inter réelle, hors scope
de ce skill).

### Étape 4 — Écrire les fichiers

Front-matter identique au schéma déjà en usage dans le dépôt (`contenu/facebook/
EXC-FB-2026-001.md` comme référence) : `statut: draft`, tous les champs de validation
(`bat_soumis_le`, `bap_recu_le`, `bap_email_ref`, `facebook_post_id`, `programme_le`,
`publie_le`, `url_post`) à `null`, `visuel_ref: null` — le visuel n'existe pas encore, ce n'est
pas ton étape. Utilise le prochain ID rendu par le script, en incrémentant pour chaque nouveau
post dans l'ordre chronologique de la semaine.

Si l'entrée calendrier n'existait pas encore (cas b de l'étape 2), ajoute-la à
`calendrier/calendrier_editorial.json` avec `statut: draft` — garde les deux fichiers
synchronisés, ne laisse jamais le calendrier en retard sur le dépôt réel.

### Étape 5 — Commit

Un seul commit pour toute la semaine, message normalisé :

```
redaction-hebdo: <n> posts rédigés, <n> bloqués — semaine du <lundi cible> — <date d'exécution>
```

### Étape 6 — Slack

Pour chaque post rédigé (même s'il n'y en a qu'un), poste dans `#excellence-plus` selon le
gabarit de `references/format-slack.md` :

- **Un message par post** — jamais tout regroupé dans un seul pavé illisible sur mobile.
- **En-tête** : ID · plateforme · jour + date · heure WAT · pilier · format.
- **Le texte complet dans un bloc de code**, tel qu'il serait publié — sauts de ligne compris,
  copiable directement.
- **Une ligne de statut** : `draft`, BAT non envoyé, et tout point ouvert (visuel absent, angle
  recentré, chiffre écarté faute de source).

Si un créneau a été bloqué à l'étape 3, poste aussi le message de blocage (§5) — l'équipe doit
savoir qu'un créneau de la semaine reste vide, pas seulement voir les posts qui ont réussi.

### Étape 7 — Rapport

Dans le chat (ou visible dans l'historique de la routine si exécution automatique) : un rapport
court — combien rédigés, combien bloqués, lien vers les messages Slack. Si tout s'est bien passé,
ne force pas une action humaine artificielle : dis simplement que tout est dans Slack et attend
le circuit BAT normal. S'il y a un blocage, c'est lui l'action prioritaire, une seule.

## 4 · Ce que tu ne fais jamais

1. **Écrire un brief visuel.** C'est `direction-artistique-excellence-plus`, une étape séparée
   qui se déclenche autrement.
2. **Publier, programmer, ou toucher Composio.** Tu ne fais que du texte, jamais de diffusion.
3. **Déplacer quoi que ce soit vers `visuels/approuves/` ou renseigner `bap_recu_le`.** Ça n'a
   même pas de sens à ce stade — rien n'a encore été soumis à personne à l'extérieur de l'équipe.
4. **Inventer une donnée manquante** — chiffre, méthode, témoignage, critère de sélection. Un
   thème de calendrier sans source documentée se recentre ou se bloque, il ne se comble jamais
   par une supposition plausible même cohérente avec le ton de la marque.
5. **Réécrire un post déjà rédigé** sans qu'on te le demande explicitement dans la conversation
   en cours.
6. **Dépasser la semaine cible.** Un post écrit trois semaines à l'avance sera périmé avant son
   créneau — même logique que `pilote-quotidien-aora` : horizon = semaine suivante, point final.
7. **Envoyer un seul message Slack fourre-tout.** Un post, un message : l'équipe doit pouvoir
   réagir et discuter chacun séparément sans faire défiler les autres.

## 5 · Format de blocage

Identique à `portes-bloquantes.md` — à poster dans Slack au même titre qu'un post réussi :

```
🚩 BLOCAGE — [ID ou date du créneau]
Porte  : [numéro et intitulé, ou « aucune source documentée »]
Motif  : [une phrase, factuelle]
Action : [une seule action humaine, nommément attribuée]
```

Un créneau qui reste vide une semaine avant sa date est une information utile pour l'équipe, pas
un échec à cacher en ne postant rien.

## 6 · Coexistence avec `pilote-quotidien-aora`

Les deux skills touchent M4. Ce n'est pas un conflit tant que l'idempotence tient : ce skill ne
réécrit jamais un fichier déjà présent, et `pilote-quotidien-aora` non plus (règle 5 de son
propre skill). Celui qui passe en premier rédige ; l'autre trouve le fichier déjà là et passe au
créneau suivant.

Ceci dit, si `pilote-quotidien-aora` tourne déjà quotidiennement et comble systématiquement
l'horizon +7 jours, ce skill devient redondant pour la rédaction elle-même — son seul apport
propre est alors le **partage Slack groupé et anticipé** d'une semaine complète en un seul geste
le mercredi. À l'équipe de décider si les deux routines restent actives, ou si ce skill devient
la seule source de M4 pour Excellence+ pendant que `pilote-quotidien-aora` se recentre sur la
publication (son étape 2) et les briefs visuels (son étape 4).

## Fichiers de référence

| Fichier | Contenu |
|---|---|
| `scripts/etat_semaine.py` | Calcul déterministe de la semaine cible et de ce qui manque |
| `scripts/mise_en_forme_yaytext.py` | Conversion Unicode gras/italique pour la légende (Étape 3 bis) |
| `references/format-slack.md` | Gabarit exact des messages Slack, avec exemple réel |
| `references/mise-en-forme-yaytext.md` | Convention de mise en forme Unicode — table, limites, exemple réel |
| `ROUTINE.md` | Le prompt à coller dans la routine Claude du mercredi 05h00 |

---

*ACADÉMIE AORA · REDHEBDO-EXC-001 · v1.1 — 18/08/2026 (+ Étape 3 bis mise en forme Unicode) ·
Contrat AORA-CCC-005*
