# LA ROUTINE — ce qu'on colle et où

## Paramétrage

```
Nom        : Pilote quotidien — Excellence+
Cadence    : Chaque jour ouvré
Heure      : 07h00 WAT  (06h00 UTC)
Dépôt      : academieaora-cpu/EXCELLENCE-PLUS · branche main
Type       : Routine distante (tourne même ordinateur éteint)
```

**Pourquoi 07h00** : le rapport arrive avant que la journée soit prise. L'équipe a la journée
entière pour monter les visuels demandés, et les créneaux de 18h30 restent tenables le jour même.

**Pourquoi jours ouvrés** : les créneaux du samedi et du dimanche sont programmés dès le vendredi.
Faire tourner la routine le week-end ne couvrirait rien de plus. Pour passer en quotidien, un seul
changement de cadence.

**Pourquoi une routine distante** : une tâche locale ne s'exécute que si la machine est allumée. Un
dispositif de publication qui dépend d'un ordinateur ouvert n'est pas un dispositif.

---

## Le prompt

```
Exécute le pilote quotidien Excellence+.

Dépôt : academieaora-cpu/EXCELLENCE-PLUS (branche main)
Skill : pilote-quotidien-aora — suis-le intégralement, étapes 0 à 6.

Rappel des points qui ne se négocient pas :
- Vérifie PAUSE avant tout. S'il existe : affiche le motif et arrête-toi.
- Ne déplace jamais un visuel dans visuels/approuves/. Ce geste appartient à l'équipe.
- Publie uniquement via composio-publie-aora, jamais directement.
- Respecte le quota calculé par scripts/etat_depot.py. Ne le dépasse pas.
- Contrôle liste rouge sur chaque post AVANT de l'écrire dans le dépôt.
- Ne signale comme écart qu'un créneau PASSÉ non couvert. Les créneaux futurs
  non couverts sont normaux pendant la montée en charge.
- Termine par UNE seule action humaine, la plus bloquante, avec sa conséquence.

Sortie : le rapport au format references/rapport-quotidien.md, posté dans Slack
sur #excellence-plus. Un seul commit, message normalisé.
```

Le prompt reste court volontairement. Toute la logique vit dans le skill : quand une règle change,
on modifie le skill, pas la routine. Une routine dont le prompt contient les règles finit
désynchronisée du reste du dispositif.

---

## Avant la première exécution

Trois valeurs à renseigner dans `config/creneaux.json` :

```
<NUMERO_WHATSAPP>     → lien wa.me du CTA principal
<NUMERO_TELEPHONE>    → CTA appel
<FACEBOOK_PAGE_ID>    → page Excellence+
```

Et la structure minimale dans le dépôt :

```
config/creneaux.json
contenu/facebook/
visuels/approuves/
visuels/en_production/
calendrier/calendrier_editorial.json
_base/identite/brand_guidelines.md
rapports/
```

Sans `config/creneaux.json`, le script s'arrête en code 2 et la routine ne fait rien. C'est voulu :
mieux vaut une routine qui ne démarre pas qu'une routine qui publie avec des créneaux inventés.

---

## Les trois premiers jours

**Jeudi 30/07 — première exécution.** L'avance sera basse, la phase RATTRAPAGE, le quota à 3. Le
rapport sera long : c'est normal, il y a tout à faire. Lis surtout l'action du jour.

**Vendredi 31/07 — vérification.** Compare l'avance à celle de la veille. Si elle n'a pas bougé,
c'est que les visuels ne sont pas descendus dans `approuves/` : le goulot est humain, pas machine.
C'est l'information la plus utile de la semaine.

**Lundi 03/08 — première semaine complète.** L'avance devrait avoir gagné 4 à 6 jours. Si oui, le
rythme est bon et l'objectif de 14 jours tombe avant la mi-août.

Lance la routine manuellement une ou deux fois avant de la planifier. Une routine qu'on programme
sans l'avoir vue tourner produit sa première surprise à 7h du matin, un jour où personne ne regarde.

---

## Après un mois

Le prompt de la routine se réécrit avec l'expérience. Les points à revoir :

- **L'heure** — si les visuels descendent systématiquement en fin de journée, 07h00 est peut-être
  trop tôt et le rapport arrive avant que la veille soit terminée.
- **Le quota** — s'il est atteint chaque jour sans effort, l'objectif d'avance peut monter à 21
  jours. S'il ne l'est jamais, c'est le goulot visuel qu'il faut traiter, pas le quota.
- **La cadence** — en régime de maintien, trois exécutions par semaine peuvent suffire.

*ACADÉMIE AORA · PIL-QUO-001 · Routine v1.0 — 29/07/2026*
