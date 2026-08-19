# LA ROUTINE — ce qu'on colle et où

## Paramétrage

```
Nom        : Rédaction hebdomadaire — Excellence+
Cadence    : Chaque mercredi
Heure      : 05h00 WAT  (04h00 UTC)
Dépôt      : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type       : Routine distante (tourne même ordinateur éteint)
```

**Pourquoi mercredi 05h00** : mercredi est le jour médian des trois créneaux Facebook actuels
(lundi / mercredi / samedi dans `config/creneaux.json`). Rédiger le mercredi pour la semaine qui
commence le lundi suivant donne une semaine complète d'avance sur le premier créneau de cette
semaine, et plus encore sur les deux autres — cohérent avec la règle « jamais au-delà de
l'horizon + 7 jours » déjà en vigueur dans `pilote-quotidien-aora`. 05h00 place le rapport Slack
avant que l'équipe n'arrive, tout en laissant une heure d'écart avec la routine quotidienne de
07h00 plutôt que les trois heures d'origine — à surveiller si l'exécution hebdomadaire (plus
longue, trois posts d'un coup) venait à empiéter dessus certaines semaines.

**Première exécution automatique** : mercredi 12/08/2026, pour la semaine du lundi 17/08/2026.
La semaine du 10/08 (créneaux des 10, 12 et 15/08) reste gérée manuellement — c'est la période de
transition avant la bascule sur cette routine, pas un trou dans sa couverture.

**Ce que « routine distante » veut dire ici** : c'est la fonctionnalité native de tâche
récurrente de Claude — pas une Action GitHub. Les Actions GitHub de ce dépôt (voir
`.github/workflows/`) tournent en Python pur, sans accès à Claude ni aux connecteurs MCP ; c'est
pour ça que `programmation_quotidienne.yml` produit un texte qu'un humain colle dans un chat
plutôt que d'appeler Composio lui-même. La routine ci-dessous n'a pas ce problème : elle s'exécute
comme une conversation Claude normale, avec l'accès complet au dépôt (bash) et à Slack (MCP) — le
même accès que celui utilisé pour rédiger et poster les posts du 10/08 et du 12/08 à la main.

---

## Le prompt

```
Exécute la rédaction hebdomadaire Excellence+.

Dépôt : academieaora-cpu/EXCELLENCE-PLUS (branche main)
Skill : redaction-hebdo-excellence-plus — suis-le intégralement, étapes 0 à 7.

Rappel des points qui ne se négocient pas :
- Vérifie PAUSE avant tout. S'il existe : affiche le motif et arrête-toi.
- N'écris jamais de brief visuel, ne touche jamais à Composio ni à visuels/approuves/.
- Ne rédige que les créneaux de la semaine cible (lundi +5 à samedi +10 jours après
  aujourd'hui). Rien au-delà, rien en-deçà.
- Passe chaque texte par les 6 portes de portes-bloquantes.md AVANT de l'écrire dans le dépôt.
- N'invente aucune donnée manquante — recentre l'angle sur ce qui est documenté par écrit,
  ou bloque explicitement. Un thème de calendrier n'autorise jamais à inventer ses détails.
- Un message Slack par post rédigé dans #excellence-plus, jamais un seul message groupé.
- Un seul commit pour toute la semaine, message normalisé.

Sortie : chaque post posté individuellement dans Slack #excellence-plus (gabarit
references/format-slack.md), plus un rapport court dans le chat — une seule action
humaine si quelque chose est bloqué, rien à forcer sinon.
```

Le prompt reste court volontairement. Toute la logique vit dans le skill : quand une règle
change, on modifie le skill, pas la routine.

---

## Avant la première exécution automatique

Lance la routine manuellement une fois sur la semaine du 17/08 avant de la programmer pour de
vrai — même logique que pour `pilote-quotidien-aora` : une routine programmée sans avoir été vue
tourner produit sa première surprise un mercredi à 4h du matin, un jour où personne ne regarde.

Vérifie aussi que `#excellence-plus` reste le bon canal si l'équipe ou la structure change — ce
skill ne demande pas confirmation avant chaque envoi, il poste directement dans le canal résolu
au moment de l'exécution.

---

## Après un mois

Points à revoir avec l'expérience :

- **Le jour** — si le calendrier éditorial change de rythme (plus ou moins de trois créneaux par
  semaine, jours différents), le mercredi médian n'est peut-être plus le bon point d'ancrage.
- **La coexistence avec `pilote-quotidien-aora`** — si celui-ci couvre déjà systématiquement
  l'horizon +7 jours tout seul, envisager de retirer la rédaction de cette routine et de ne
  garder que le partage Slack groupé du mercredi, ou de désactiver l'une des deux routines.

---

*ACADÉMIE AORA · REDHEBDO-EXC-001 · Routine v1.0 — 08/08/2026*
