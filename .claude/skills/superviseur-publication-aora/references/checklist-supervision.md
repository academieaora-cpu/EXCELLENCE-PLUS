# Checklist de supervision — version courte

À relire en 30 secondes avant ou après toute exécution de routine touchant la publication.

| # | Contrôle | Fichier de vérité | Écart type |
|---|---|---|---|
| 1 | Page Facebook cible | `config/page_cible.json` | Composio pointe vers une autre Page/ID |
| 2 | Créneaux (tout post daté) | `config/creneaux.json` | Post daté à un jour/heure absent du fichier |
| 3 | Double porte | état réel du dépôt (front-matter + `visuels/approuves/`) | `composio_id` sans BAP écrit et/ou sans visuel approuvé |
| 4 | Idempotence | front-matter de tous les posts | même `composio_id` sur deux fichiers |
| 5 | Vocabulaire | front-matter (`statut`, `publie_le`) | rapport dit « publié » sans `publie_le` renseigné |
| 6 | Contacts WhatsApp | `config/contacts.json` | numéro hors liste approuvée, ou `A_REMPLIR` encore présent |
| 7 | Style du titre | `config/mise_en_forme.json` → `styles.accroche.style_yaytext` | titre stylé dans une autre famille Unicode que celle attendue |
| 8 | Automatismes concurrents | `.github/workflows/publish_scheduled.yml` | encore actif → jamais une preuve, rappel une fois par audit |

## Dernier état constaté (02/08/2026 — à mettre à jour, pas à recopier tel quel indéfiniment)

- `config/page_cible.json` : **absent**. Page cible connue uniquement par la conversation :
  Excellence+ Éducation, id `61584305458367`.
- `config/contacts.json` : créé en local (même session), **pas encore poussé** sur `main`. Numéros
  WhatsApp approuvés : `+237 699 403 969`, `+237 679 941 300`. Le +33 n'est pas un contact WhatsApp.
- `config/mise_en_forme.json` : accroche = **gras_serif** + majuscule (mis à jour le 02/08/2026,
  corrigé depuis un réglage initial erroné en gras sans-serif).
- `config/creneaux.json` : Lundi 06h00 · Mercredi 12h00 · Samedi 06h00 WAT. Re-validation client
  par email : statut non confirmé au moment de l'écriture de ce skill.
- **Écart réel détecté par le contrôle 2** : `contenu/facebook/EXC-FB-2026-001.md` est daté mardi
  12:30 — un créneau qui n'existe plus depuis le 02/08/2026. Ce post a été créé avant le changement
  de calendrier et n'a pas été corrigé. À traiter avant tout BAT.
- `publish_scheduled.yml` : actif (cron `*/15 5-21 * * *`), appelle `check_and_publish.py` dont
  l'appel Composio n'est pas implémenté et qui ne vérifie pas la porte visuel. Désactivation
  recommandée par `composio-publie-aora/SKILL.md` §1, pas encore faite au moment de l'écriture.

Cette section se périme vite — si elle ne correspond plus à ce que `verifier_conformite.py`
rapporte, fais confiance au script, pas à ce tableau.
