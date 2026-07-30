# Routines Claude — AORA × Excellence+

Trois routines, trois métiers distincts. Chacune échoue pour ses propres raisons et se répare
séparément — c'est pour cela qu'elles ne sont pas fondues en une seule.

| # | Routine | Quand | Ce qu'elle fait | Connecteurs |
|---|---|---|---|---|
| **1** | [Programmation](routine1_programmation.md) | tous les jours · 03h00 WAT | Applique les 8 portes, **programme chez Composio**, écrit l'identifiant en retour | Composio · Slack · Gmail (lecture) |
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

**La détection d'un BAP reçu** est déjà automatique et n'a pas besoin de routine : le workflow
GitHub `notif_bap.yml` se déclenche au push et alerte Slack au moment où un humain renseigne
`bap_recu_le`. Un `git push` est un signal plus fiable et plus immédiat qu'un passage horaire.

**Le dépôt d'un visuel dans `approuves/`** reste un geste humain. Aucune routine ne le fait,
aucune ne le contourne. C'est la signature de validation du visuel — l'automatiser reviendrait
à supprimer le contrôle.

## Les trois interdits communs

Ils figurent dans chaque prompt, et ce n'est pas de la redondance : une routine dont les
garde-fous vivent ailleurs finit par s'en écarter sans que personne le voie.

1. **Jamais renseigner `bap_recu_le` ni `bap_email_ref`** — même en ayant l'email sous les yeux.
2. **Jamais déplacer un fichier dans `visuels/approuves/`.**
3. **Jamais envoyer un email au client** — brouillon uniquement.

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
