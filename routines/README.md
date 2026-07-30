# Routines Claude — AORA × Excellence+

Trois routines, trois métiers distincts. Chacune échoue pour ses propres raisons et se répare
séparément — c'est pour cela qu'elles ne sont pas fondues en une seule.

| # | Routine | Quand | Ce qu'elle fait | Connecteurs |
|---|---|---|---|---|
| **1** | [Programmation](routine1_programmation.md) | tous les jours · 03h00 WAT | Enregistre les BAP (Gmail + dépôts manuels via `traiter_bap.py`), applique les 8 portes, **programme chez Composio**, écrit l'identifiant en retour | Composio · Slack · Gmail (lecture) |
| **2** | [Production](routine2_production.md) | jours ouvrés · 07h00 WAT | Écrit les textes manquants, brieffe les visuels, mesure l'avance | Slack |
| **3** | [BAT hebdomadaire](routine3_bat_hebdomadaire.md) | mercredi · 09h00 WAT | Constitue le lot, **rédige un brouillon** Gmail pour Laurence | Gmail · Slack |

## L'enchaînement sur une semaine

```
lundi     07h00  R2 écrit les textes qui manquent, brieffe les visuels
mardi     03h00  R1 programme ce qui est prêt · 12h30 publication
mercredi  07h00  R2 produit  ·  09h00  R3 prépare le BAT du lot S+2
jeudi     03h00  R1 programme · 19h00 publication
vendredi  07h00  R2 produit — dernier passage avant le week-end
samedi    03h00  R1 programme · 10h00 publication
dimanche         aucune routine
```

Le samedi est couvert : la Routine 1 tourne tous les jours, y compris le week-end. Seule la
production (R2) s'arrête, parce qu'elle demande une équipe disponible derrière.

## Ce qui n'est PAS une routine

**La détection d'un BAP reçu** est déjà automatique et n'a pas besoin de routine dédiée : le
workflow GitHub `notif_bap.yml` se déclenche au push et alerte Slack au moment où `bap_recu_le`
est renseigné — qu'il l'ait été à la main ou par `scripts/traiter_bap.py` (étape 2 de la
Routine 1). Un `git push` est un signal plus fiable et plus immédiat qu'un passage horaire.

**Le dépôt d'un visuel dans `approuves/`** n'est plus un geste exclusivement humain depuis que
`scripts/traiter_bap.py` existe (voir [routine1_programmation.md](routine1_programmation.md)
étape 2) — mais ce n'est toujours pas un geste que les routines exécutent librement. Une seule
porte y donne accès : un fichier BAP vérifié dans `validation/BAP/`, déposé à la main par
Laurence OU écrit par la Routine 1 après lecture d'un email de validation Gmail sans aucune
ambiguïté sur la publication concernée. Dans les deux cas, c'est le script — jamais une routine
directement — qui contrôle et déplace. Rien d'autre ne fait bouger un fichier vers `approuves/`.

## Les trois interdits communs

Ils figurent dans chaque prompt, et ce n'est pas de la redondance : une routine dont les
garde-fous vivent ailleurs finit par s'en écarter sans que personne le voie. Pour R2 et R3, qui
n'ont aucun rôle dans le traitement des BAP, ces interdits restent **absolus, sans exception**.
Pour R1, dont l'étape 2 existe précisément pour ce traitement, ils sont resserrés à une seule
porte étroite plutôt que levés :

1. **Jamais renseigner `bap_recu_le` ni `bap_email_ref` à la main.** R1 ne le fait jamais
   directement non plus — seul `scripts/traiter_bap.py`, appelé en étape 2, en a le droit, et
   seulement sur la base d'un fichier BAP vérifié.
2. **Jamais déplacer un fichier dans `visuels/approuves/` à la main.** Même règle : seul
   `scripts/traiter_bap.py` le fait, jamais une routine directement, jamais sur une simple
   lecture d'email non formalisée en fichier BAP.
3. **Jamais envoyer un email au client** — brouillon uniquement. Sans exception, pour les trois
   routines.

## Ordre de mise en service

Ne planifiez pas les trois le même jour.

1. **R2 d'abord**, seule pendant deux ou trois jours. Elle ne publie rien : le risque est nul et
   vous voyez le stock monter.
2. **R3 ensuite**, une fois qu'il y a de quoi constituer un lot.
3. **R1 en dernier**, et faites-la tourner **à la main** au moins une fois avant de la planifier.
   C'est la seule qui envoie quelque chose vers l'extérieur.

Une routine qu'on programme sans l'avoir vue tourner produit sa première surprise à 3h du matin,
un jour où personne ne regarde.

## Avant que R1 puisse programmer

Trois valeurs manquent encore, et elles sont gardées par la CI — un post validé qui contient
encore `A_REMPLIR` bloque avant publication :

- numéro WhatsApp du CTA
- identifiant de la Page Facebook Excellence+
- secret `SLACK_WEBHOOK_URL` (ou `SLACK_BOT_TOKEN` + `SLACK_CHANNEL`) dans les settings du dépôt

Et le connecteur **Composio doit être activé dans la conversation** où tourne la routine —
c'est un interrupteur par conversation, pas un réglage global.
