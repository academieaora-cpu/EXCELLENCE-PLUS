# Routines Claude — AORA × Excellence+

Quatre routines, quatre métiers distincts. Chacune échoue pour ses propres raisons et se répare
séparément — c'est pour cela qu'elles ne sont pas fondues en une seule.

| # | Routine | Quand | Ce qu'elle fait | Connecteurs |
|---|---|---|---|---|
| **1** | [Programmation](routine1_programmation.md) | tous les jours · 03h00 WAT | Enregistre les BAP (Gmail + dépôts manuels via `traiter_bap.py`), applique les 8 portes, **programme chez Composio**, écrit l'identifiant en retour | Composio · Slack · Gmail (lecture) |
| **2** | [Production](routine2_production.md) | jours ouvrés · 07h00 WAT | Écrit les textes manquants, brieffe les visuels, mesure l'avance | Slack |
| **3** | [BAT hebdomadaire](routine3_bat_hebdomadaire.md) | mercredi · 09h00 WAT | Constitue le lot, **rédige un brouillon** Gmail pour Laurence | Gmail · Slack |
| **4** | [Vérification + propositions Meta Ads](routine4_metaads.md) | tous les jours · 03h00 WAT<br>+ 07h15 WAT | 03h00 : vérifie les 4 portes, audite (10 contrôles + trous silencieux), **propose** des boosts (écrit dans `en_preparation/` uniquement). 07h15 : rapport quotidien Slack (`pilote-metaads-aora`). **Ne crée et ne dépense rien** | Slack (fil Meta Ads) · Meta Marketing API (lecture) |

Trois skills complètent R4 pour ce qu'un script seul ne peut pas trancher : `meta-ads-publie-aora`
(construire/exécuter une campagne ou un boost en chat), `verifier-validations-gmail-aora`
(détecter une BAB par email, formule stricte), `pilote-metaads-aora` (le rapport de 07h15,
documenté aussi comme skill pour un usage à la demande). Aucun des trois n'exécute une dépense
de lui-même — voir chaque `SKILL.md` pour ses propres interdits.

## L'enchaînement sur une semaine

```
lundi     03h00  R1 programme  ·  R4 vérifie + propose des boosts
          07h00  R2 écrit les textes qui manquent, brieffe les visuels
          07h15  R4 rapport Meta Ads quotidien (Slack)
          06h00  publication (créneau pilier 1)
mardi     03h00  R1 programme  ·  R4 vérifie + propose
          07h15  R4 rapport
mercredi  03h00  R1 programme  ·  R4 vérifie + propose
          07h00  R2 produit  ·  07h15  R4 rapport  ·  09h00  R3 prépare le BAT du lot S+2
          12h00  publication (créneau pilier 2)
jeudi     03h00  R1 programme  ·  R4 vérifie + propose
          07h15  R4 rapport
vendredi  03h00  R1 programme  ·  R4 vérifie + propose
          07h00  R2 produit — dernier passage avant le week-end  ·  07h15  R4 rapport
samedi    03h00  R1 programme  ·  R4 vérifie + propose
          07h15  R4 rapport
          06h00  publication (créneau pilier 3)
dimanche  03h00  R1 programme  ·  R4 vérifie + propose
          07h15  R4 rapport
```

Créneaux de publication : `config/creneaux.json` fait foi (lundi 06h00 · mercredi 12h00 ·
samedi 06h00 depuis le 02/08/2026). Ne pas les relire ici : ce tableau est un rappel, pas la
source de vérité.

Le week-end est couvert : R1 et R4 tournent tous les jours, les deux passages de R4 compris.
Seules la production (R2) et le BAT (R3) s'arrêtent, parce qu'ils demandent une équipe disponible
derrière.

**R1 et R4 tournent à la même heure à 03h00, dans deux workflows séparés.** Ce n'est pas un oubli
de factorisation : R1 engage du contenu, R4 engage de l'argent. Les fondre ferait qu'une erreur de
configuration sur l'un exposerait l'autre. Même horaire, jamais même fichier.

**Le rapport de 07h15 a remplacé un passage hebdomadaire du lundi 08h00** (calqué à l'origine sur
`rapport_hebdo.yml`). Un rapport quotidien couvre déjà « l'équipe voit l'état Meta Ads en arrivant
» tous les jours — garder les deux aurait doublé le même message un lundi sur deux, à moins d'une
heure d'écart.

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
garde-fous vivent ailleurs finit par s'en écarter sans que personne le voie. Pour R2, R3 et R4,
qui n'ont aucun rôle dans le traitement des BAP, ces interdits restent **absolus, sans
exception**. Pour R1, dont l'étape 2 existe précisément pour ce traitement, ils sont resserrés à
une seule porte étroite plutôt que levés :

1. **Jamais renseigner `bap_recu_le` ni `bap_email_ref` à la main.** R1 ne le fait jamais
   directement non plus — seul `scripts/traiter_bap.py`, appelé en étape 2, en a le droit, et
   seulement sur la base d'un fichier BAP vérifié.
2. **Jamais déplacer un fichier dans `visuels/approuves/` à la main.** Même règle : seul
   `scripts/traiter_bap.py` le fait, jamais une routine directement, jamais sur une simple
   lecture d'email non formalisée en fichier BAP.
3. **Jamais envoyer un email au client** — brouillon uniquement. Sans exception, pour les trois
   routines.

## Ordre de mise en service

Ne planifiez pas les quatre le même jour.

1. **R2 d'abord**, seule pendant deux ou trois jours. Elle ne publie rien : le risque est nul et
   vous voyez le stock monter.
2. **R4 ensuite** — elle ne peut rien dépenser en l'état (quatre portes fermées) et son rapport
   quotidien vous montre exactement ce qui manque encore côté payant. C'est la routine la moins
   risquée des quatre, et la plus utile à faire tourner tôt : elle documente le verrou.
3. **R3**, une fois qu'il y a de quoi constituer un lot.
4. **R1 en dernier**, et faites-la tourner **à la main** au moins une fois avant de la planifier.
   C'est la seule qui envoie quelque chose vers l'extérieur sans déclenchement manuel.

Une routine qu'on programme sans l'avoir vue tourner produit sa première surprise à 3h du matin,
un jour où personne ne regarde.

**R4 fait exception à ce dernier point, mais dans un seul sens** : son passage programmé ne peut
créer aucune campagne — l'exécution réelle est conditionnée à un `workflow_dispatch` manuel. La
surprise possible à 3h du matin se limite à un rapport qui dit « verrouillé ». C'est le
déclenchement manuel, lui, qui mérite d'être vu tourner en dry-run avant d'être lancé avec
`executer: true`.

## Avant que R1 puisse programmer

Trois valeurs manquent encore, et elles sont gardées par la CI — un post validé qui contient
encore `A_REMPLIR` bloque avant publication :

- numéro WhatsApp du CTA
- identifiant de la Page Facebook Excellence+
- secret `SLACK_WEBHOOK_URL` (ou `SLACK_BOT_TOKEN` + `SLACK_CHANNEL`) dans les settings du dépôt

## Avant que R4 puisse créer une campagne

R4 tourne dès aujourd'hui — elle rapportera simplement « verrouillé » tant que les quatre portes
sont fermées. Ce n'est pas une panne, c'est l'état attendu au mois 1 (août 2026, Meta Ads non
activé par contrat AORA-CCC-005).

Ce qui manque, par ordre de blocage :

- **`ad_account_id`** dans `meta-ads/config/meta_ads_comptes.json` — identifiant Meta réel, à
  obtenir de M. NDOMMIE ou du Business Manager AORA. Jamais deviné, jamais découvert par un
  listing d'API : un compte atteignable n'est pas un compte autorisé.
- `instagram_actor_id` et `devise_compte` (même fichier) — le second vaut un facteur 100 sur le
  budget réel selon la devise du compte
- une **BAB écrite** archivée dans `meta-ads/validation/BAB_budget/`, puis `scenario_retenu` et
  `montant_mensuel_fcfa` renseignés à la main (jamais par `verifier-validations-gmail-aora`, qui
  s'arrête à la preuve — voir son `SKILL.md` §4) ; et d'abord, un gabarit email qui demande
  explicitement la formule de `config/validation_formules.json → bab` — aucun gabarit du dépôt
  ne l'envoie encore
- **`scenarios_budget_metaads.pdf`**, absent du dépôt — la porte 2 refuse de s'ouvrir tant qu'il
  manque, même montant renseigné
- le mois concerné passé à `"autorise": true` dans `meta_ads_activation.json` — geste humain
- secrets `META_MARKETING_TOKEN` et `SLACK_WEBHOOK_URL_METAADS`, **distincts de ceux de Composio**

Détail complet : [routine4_metaads.md](routine4_metaads.md) et `meta-ads/README.md`.

Et le connecteur **Composio doit être activé dans la conversation** où tourne la routine —
c'est un interrupteur par conversation, pas un réglage global.
