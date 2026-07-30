# ROUTINE 2 — Production quotidienne

> Elle remplit le stock que la Routine 1 programmera. Sans elle, la Routine 1 n'a rien à
> envoyer et le calendrier se vide.

## Paramétrage

```
Nom       : Excellence+ — Pilote quotidien
Cadence   : Chaque jour
Heure     : 05h00 WAT  (04h00 UTC)
Dépôt     : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type      : Routine distante
Connecteurs requis : Slack
```

**Pourquoi 05h00** — avant R1 (03h00) c'était trop tôt pour ce que R1 vient de programmer ; après
R3, trop tard pour que le lot du jour profite d'une production fraîche. 05h00 laisse le rapport
arriver avant que l'équipe commence sa journée, avec deux heures d'avance sur le BAT de 07h00.

**Pourquoi tous les jours et pas seulement en semaine** — passage quotidien décidé pour rester
aligné avec R1 et R3, qui tournent désormais tous les jours elles aussi. Un dimanche sans visuel
neuf dans `approuves/` ne produit qu'un rapport court ("rien à faire") — coût nul, cohérence du
dispositif gagnée. Si le week-end s'avère systématiquement improductif (personne pour monter les
visuels), revenir à jours ouvrés plutôt que laisser tourner un passage qui ne sert jamais à rien.

**Pourquoi séparée de la Routine 1** — la production (écrire des textes, briefer des visuels)
et la programmation (envoyer chez Composio) échouent pour des raisons différentes et se
réparent différemment. Les fondre en une seule routine produit un rapport où l'on ne sait plus
ce qui a marché.

---

## Le prompt

```
Exécute le pilote quotidien Excellence+.

Dépôt : academieaora-cpu/EXCELLENCE-PLUS, branche main.
Skill : pilote-quotidien-aora — suis-le intégralement, étapes 0 à 6.

Rappel des points qui ne se négocient pas :

· Vérifie PAUSE avant tout. S'il existe : affiche le motif et arrête-toi.

· Ne déplace JAMAIS un visuel dans visuels/approuves/. Ce geste appartient à
  l'équipe — il EST la validation du visuel. Si tu le fais, plus personne ne
  valide rien et le contrôle disparaît sans que quiconque l'ait décidé.

· Ne programme rien toi-même. La programmation est le métier de la Routine 1.

· Respecte le quota calculé par le skill. Ne le dépasse pas : trois posts
  écrits avec soin valent mieux que huit remplis à la va-vite. Le stock n'a de
  valeur que s'il est publiable tel quel.

· Contrôle liste rouge AVANT d'écrire chaque post dans le dépôt, pas après.
  Contrôler à la production coûte trente secondes ; contrôler seulement à la
  publication laisse le défaut vivre une semaine dans le dépôt.

· Chiffres opposables, les seuls : 93 % (2023-2024) et 97 % (2024-2025).
  N'invente aucune donnée manquante — effectif, témoignage, photo. Signale le
  manque plutôt que de le combler.

· Ne signale comme écart qu'un créneau PASSÉ resté vide. Les créneaux futurs
  non couverts sont normaux pendant la montée en charge.

· Cadence de référence : 3 publications par semaine AU TOTAL, tous canaux
  confondus — mardi 12h30, jeudi 19h00, samedi 10h00 WAT.
  Source qui fait foi : config/creneaux.json.

Sortie : le rapport court dans Slack, canal #excellence-plus.
Un seul commit, message normalisé.
Termine par UNE seule action humaine, la plus bloquante, avec sa conséquence.
```

---

## Ce qu'il faut regarder les premiers jours

**Jour 2** — comparez l'avance à celle de la veille. Si elle n'a pas bougé, c'est que les
visuels ne sont pas descendus dans `approuves/` : le goulot est humain, pas machine. C'est
l'information la plus utile de la semaine.

**Après une semaine** — l'avance devrait avoir gagné 4 à 6 jours. Si oui, le rythme est bon.
Si le quota est atteint chaque jour sans effort, montez l'objectif d'avance. S'il ne l'est
jamais, c'est le goulot visuel qu'il faut traiter — pas le quota.
